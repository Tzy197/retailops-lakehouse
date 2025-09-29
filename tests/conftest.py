# tests/conftest.py
import os

import pytest
from pyspark.sql import SparkSession


@pytest.fixture(scope="session")
def spark_session():
    os.environ.setdefault("PYSPARK_PYTHON", "python3")
    spark = (
        SparkSession.builder.appName("test_session").master("local[2]").getOrCreate()
    )
    spark.sparkContext.setLogLevel("ERROR")
    yield spark
    spark.stop()
