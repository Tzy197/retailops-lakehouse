# tests/test_bronze_stream_smoke.py
import os
from uuid import uuid4

from pyspark.sql import functions as F


def test_batch_write_parquet_partitioned(spark_session, tmp_path):
    spark = spark_session

    out = tmp_path / f"bronze_test_out_{uuid4().hex}"
    out.mkdir(parents=True, exist_ok=True)

    df = (
        spark.range(10)
        .withColumn("ingested_at", F.current_timestamp())
        .withColumn("p_date", F.to_date(F.current_timestamp()))
    )

    # Batch write statt Streaming
    (df.write.mode("overwrite").partitionBy("p_date").parquet(str(out)))

    # Assert: mindestens eine Parquet-Datei existiert (rekursiv suchen)
    found = False
    for _, _, files in os.walk(out):
        if any(f.endswith(".parquet") for f in files):
            found = True
            break
    assert found, f"Keine Parquet-Dateien unter {out} gefunden"
