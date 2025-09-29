# tests/test_bronze_schema.py
import json

from pyspark.sql import functions as F

from spark_jobs import bronze_orders as m


def test_from_json_parses_valid_record(spark_session):
    # Fixture spark_session liefern wir unten
    spark = spark_session
    payload = {
        "order_id": "o1",
        "customer_id": "c1",
        "ts": "2025-09-29T12:00:00Z",
        "items": [
            {"product_id": "p1", "qty": 2, "unit_price": 3.5, "category": "fruit"}
        ],
        "total_amount": 7.0,
        "country": "DE",
    }
    df = spark.createDataFrame([json.dumps(payload)], "string").toDF("json_value")
    parsed = df.select(F.from_json("json_value", m.ORDER_SCHEMA).alias("data")).select(
        "data.*"
    )
    row = parsed.first().asDict()
    assert row["order_id"] == "o1"
    assert row["customer_id"] == "c1"
    assert isinstance(row["items"], list)
    assert row["total_amount"] == 7.0
