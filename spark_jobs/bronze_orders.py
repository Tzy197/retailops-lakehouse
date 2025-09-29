# spark_jobs/bronze_orders.py
import os

from pyspark.sql import SparkSession
from pyspark.sql import functions as F
from pyspark.sql import types as T

APP_NAME = "bronze_orders"
KAFKA_BOOTSTRAP = "kafka:9092"
KAFKA_TOPIC = "orders.v1"

# ENV-Override für Tests/CI
OUTPUT_PATH = os.getenv("BRONZE_OUTPUT_PATH", "/lake/bronze/orders")
CHECKPOINT_PATH = os.getenv("BRONZE_CHECKPOINT_PATH", "/lake/checkpoints/orders_bronze")
BAD_RECORDS_PATH = os.getenv("BRONZE_BAD_PATH", "/lake/bronze/orders_corrupt")

ORDER_SCHEMA = T.StructType(
    [
        T.StructField("order_id", T.StringType(), True),
        T.StructField("customer_id", T.StringType(), True),
        T.StructField("ts", T.StringType(), True),
        T.StructField(
            "items",
            T.ArrayType(
                T.StructType(
                    [
                        T.StructField("product_id", T.StringType(), True),
                        T.StructField("qty", T.IntegerType(), True),
                        T.StructField("unit_price", T.DoubleType(), True),
                        T.StructField("category", T.StringType(), True),
                    ]
                )
            ),
            True,
        ),
        T.StructField("total_amount", T.DoubleType(), True),
        T.StructField("country", T.StringType(), True),
    ]
)


def build_spark(app_name: str = APP_NAME) -> SparkSession:
    return SparkSession.builder.appName(app_name).getOrCreate()


def main():
    spark = build_spark()
    spark.sparkContext.setLogLevel("WARN")

    raw = (
        spark.readStream.format("kafka")
        .option("kafka.bootstrap.servers", KAFKA_BOOTSTRAP)
        .option("subscribe", KAFKA_TOPIC)
        .option("startingOffsets", "earliest")
        .option("failOnDataLoss", "false")
        .load()
    )

    json_str = F.col("value").cast("string")

    with_parsed = raw.select(
        F.col("key").cast("string").alias("kafka_key"),
        "topic",
        "partition",
        "offset",
        F.col("timestamp").alias("kafka_timestamp"),
        json_str.alias("json_value"),
        F.from_json(json_str, ORDER_SCHEMA).alias("data"),
    )

    parsed = (
        with_parsed.withColumn("ts", F.to_timestamp("data.ts"))
        .withColumn("ingested_at", F.current_timestamp())
        .withColumn("p_date", F.to_date("ingested_at"))
    )

    good = parsed.filter(F.col("data").isNotNull()).select(
        "kafka_key",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        F.col("data.order_id").alias("order_id"),
        F.col("data.customer_id").alias("customer_id"),
        F.col("data.ts").cast("timestamp").alias("ts"),
        F.col("data.items").alias("items"),
        F.col("data.total_amount").alias("total_amount"),
        F.col("data.country").alias("country"),
        "ingested_at",
        "p_date",
    )

    bad = parsed.filter(F.col("data").isNull()).select(
        "kafka_key",
        "topic",
        "partition",
        "offset",
        "kafka_timestamp",
        F.col("json_value").alias("_corrupt"),
        "ingested_at",
        "p_date",
    )

    # kleine-Datei-Kontrolle (lokal)
    good = good.repartition(4, F.col("p_date"))

    good_q = (
        good.writeStream.format("parquet")
        .option("path", OUTPUT_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH)
        .option("maxRecordsPerFile", "50000")
        .outputMode("append")
        .partitionBy("p_date")
        .trigger(processingTime="20 seconds")
        .start()
    )

    bad_q = (
        bad.writeStream.format("parquet")
        .option("path", BAD_RECORDS_PATH)
        .option("checkpointLocation", CHECKPOINT_PATH + "_corrupt")
        .outputMode("append")
        .partitionBy("p_date")
        .trigger(processingTime="20 seconds")
        .start()
    )

    good_q.awaitTermination()
    bad_q.awaitTermination()


if __name__ == "__main__":
    main()
