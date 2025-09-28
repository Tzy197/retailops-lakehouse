import json
import random
from datetime import datetime
from unittest.mock import patch

from data_gen import produce_orders as mod


def test_build_producer_params():
    calls = {}

    class DummyKP:
        def __init__(self, **kwargs):
            calls["kwargs"] = kwargs

        def flush(self):
            pass

        def close(self):
            pass

    with patch.object(mod, "KafkaProducer", DummyKP):
        _ = mod.build_producer("localhost:9093")
        kw = calls["kwargs"]

        assert kw["bootstrap_servers"] == "localhost:9093"
        assert kw["acks"] == "all"
        assert kw["linger_ms"] == 50
        assert kw["retries"] == 10

        v = kw["value_serializer"]({"x": 1})
        assert isinstance(v, (bytes, bytearray))
        assert json.loads(v.decode("utf-8")) == {"x": 1}

        assert kw["key_serializer"]("k") == b"k"
        assert kw["key_serializer"](None) is None


def test_make_item_and_order_shapes():
    products = [
        {"product_id": "P1", "category": "fruit", "price_min": 1.0, "price_max": 2.0}
    ]
    customers = [{"customer_id": "C1", "country": "DE"}]

    item = mod.make_item(products[0])
    assert {"product_id", "qty", "unit_price", "category"} <= item.keys()
    assert 1 <= item["qty"] <= 3
    assert products[0]["price_min"] <= item["unit_price"] <= products[0]["price_max"]

    order = mod.make_order(customers, products)
    assert {
        "order_id",
        "customer_id",
        "ts",
        "items",
        "total_amount",
        "country",
    } <= order.keys()

    # ts parsbar als ISO-8601
    datetime.fromisoformat(order["ts"].replace("Z", "+00:00"))

    total = round(sum(i["qty"] * i["unit_price"] for i in order["items"]), 2)
    assert abs(order["total_amount"] - total) < 1e-6
    assert order["customer_id"] == "C1"
    assert order["country"] == "DE"


def test_seed_reproducibility():
    products = [
        {"product_id": "P1", "category": "fruit", "price_min": 1.0, "price_max": 2.0},
        {"product_id": "P2", "category": "veg", "price_min": 3.0, "price_max": 4.0},
    ]
    customers = [
        {"customer_id": "C1", "country": "DE"},
        {"customer_id": "C2", "country": "AT"},
    ]

    random.seed(42)
    a = mod.make_order(customers, products)
    random.seed(42)
    b = mod.make_order(customers, products)

    # order_id und ts variieren immer → ausblenden
    def strip(d):
        return {k: v for k, v in d.items() if k not in {"order_id", "ts"}}

    assert strip(a) == strip(b)
