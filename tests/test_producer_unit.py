import random

from data_gen.produce_orders import load_customers, load_products, make_item, make_order


def test_load_seeds():
    prods = load_products()
    custs = load_customers()
    assert len(prods) >= 1
    assert len(custs) >= 1
    for p in prods:
        assert {"product_id", "category", "price_min", "price_max"} <= p.keys()
        assert p["price_min"] <= p["price_max"]


def test_make_item_respects_price_bounds():
    random.seed(123)
    p = {"product_id": "p_1", "category": "x", "price_min": 5.0, "price_max": 10.0}
    it = make_item(p)
    assert 5.0 <= it["unit_price"] <= 10.0
    assert it["qty"] in (1, 2, 3)
    assert it["product_id"] == "p_1"


def test_make_order_schema_and_total():
    random.seed(123)
    prods = [
        {"product_id": "p_1", "category": "c", "price_min": 5.0, "price_max": 5.0},
        {"product_id": "p_2", "category": "c", "price_min": 2.0, "price_max": 2.0},
    ]
    custs = [{"customer_id": "c_1", "country": "DE"}]
    o = make_order(custs, prods)

    assert {
        "order_id",
        "customer_id",
        "ts",
        "items",
        "total_amount",
        "country",
    } <= o.keys()
    assert o["customer_id"] == "c_1"
    assert o["country"] == "DE"
    assert len(o["items"]) >= 1

    total = sum(i["qty"] * i["unit_price"] for i in o["items"])
    assert abs(o["total_amount"] - total) < 1e-6
