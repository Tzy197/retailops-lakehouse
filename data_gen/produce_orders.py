#!/usr/bin/env python3
import argparse
import csv
import json
import random
import signal
import sys
import time
import uuid
from datetime import UTC, datetime
from pathlib import Path

from kafka import KafkaProducer
from kafka.errors import KafkaError

ROOT = Path(__file__).resolve().parents[1]
SEEDS_DIR = ROOT / "data" / "seeds"
PRODUCTS_CSV = SEEDS_DIR / "products.csv"
CUSTOMERS_CSV = SEEDS_DIR / "customers.csv"


def load_products():
    products = []
    with PRODUCTS_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            products.append(
                {
                    "product_id": row["product_id"],
                    "category": row["category"],
                    "price_min": float(row["price_min"]),
                    "price_max": float(row["price_max"]),
                }
            )
    if not products:
        raise RuntimeError("products.csv leer")
    return products


def load_customers():
    customers = []
    with CUSTOMERS_CSV.open(newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            customers.append(
                {
                    "customer_id": row["customer_id"],
                    "country": row["country"],
                }
            )
    if not customers:
        raise RuntimeError("customers.csv leer")
    return customers


def make_item(prod: dict) -> dict:
    qty = random.randint(1, 3)
    price = round(random.uniform(prod["price_min"], prod["price_max"]), 2)
    return {
        "product_id": prod["product_id"],
        "qty": qty,
        "unit_price": price,
        "category": prod["category"],
    }


def make_order(customers, products) -> dict:
    cust = random.choice(customers)
    items = [make_item(random.choice(products)) for _ in range(random.randint(1, 3))]
    total = round(sum(i["qty"] * i["unit_price"] for i in items), 2)
    return {
        "order_id": str(uuid.uuid4()),
        "customer_id": cust["customer_id"],
        "ts": datetime.now(UTC).replace(microsecond=0).isoformat(),
        "items": items,
        "total_amount": total,
        "country": cust["country"],
    }


def build_producer(bootstrap: str) -> KafkaProducer:
    return KafkaProducer(
        bootstrap_servers=bootstrap,
        acks="all",
        linger_ms=50,
        retries=10,
        value_serializer=lambda v: json.dumps(v).encode("utf-8"),
        key_serializer=lambda v: v.encode("utf-8") if v is not None else None,
    )


stop = False


def _sigint_handler(_sig, _frm):
    global stop
    stop = True


def main():
    parser = argparse.ArgumentParser(description="Orders producer")
    parser.add_argument(
        "--bootstrap", default="localhost:9093", help="Kafka bootstrap servers"
    )
    parser.add_argument("--topic", default="orders.v1", help="Kafka topic")
    parser.add_argument("--eps", type=float, default=10.0, help="Events pro Sekunde")
    parser.add_argument("--max", type=int, default=0, help="Max Events (0 = unendlich)")
    parser.add_argument("--seed", type=int, default=None, help="Random seed")
    args = parser.parse_args()

    if args.seed is not None:
        random.seed(args.seed)

    if not PRODUCTS_CSV.exists() or not CUSTOMERS_CSV.exists():
        sys.exit(f"Seeds nicht gefunden unter {SEEDS_DIR}")

    products = load_products()
    customers = load_customers()
    producer = build_producer(args.bootstrap)

    signal.signal(signal.SIGINT, _sigint_handler)
    signal.signal(signal.SIGTERM, _sigint_handler)

    interval = 1.0 / max(args.eps, 0.001)
    sent = 0
    try:
        while not stop and (args.max == 0 or sent < args.max):
            evt = make_order(customers, products)
            key = evt["customer_id"]
            future = producer.send(args.topic, key=key, value=evt)
            try:
                future.get(timeout=10)
            except KafkaError as e:
                print(f"Send-Fehler: {e}", file=sys.stderr)
            sent += 1
            time.sleep(interval)
    finally:
        producer.flush()
        producer.close()
        print(f"Beendet. Gesendet: {sent}")


if __name__ == "__main__":
    main()
