# retailops-lakehouse

End-to-End Data & AI Pipeline Demo: Kafka → Spark → dbt → Airflow → FastAPI → ML

## Überblick

Demo-Projekt zur Umsetzung einer modernen Datenpipeline.  
Ziel: Von Event-Streaming über Datenmodellierung bis zur Bereitstellung von KPIs und Predictions.

## Aktueller Stand

- Projektstruktur mit Poetry, Linter/Formatter (Black, Ruff, Mypy, Pytest)
- Docker-Infra läuft lokal mit:
  - Kafka + Zookeeper
  - Postgres (DB für Airflow/dbt)
  - MinIO (Data Lake Simulation)
  - Apache Airflow (Orchestrierung)
  - Apache Spark (Transformation)

## Tech Stack

- **Programmiersprachen**: Python, SQL
- **Streaming/Compute**: Kafka, Spark
- **Orchestrierung/Modellierung**: Airflow, dbt
- **Serving**: FastAPI (folgt)
- **Infra**: Docker Compose

## Kafka Setup

Nach dem Start der Docker-Umgebung (`docker compose up -d`) muss das Topic **orders.v1** einmalig angelegt werden:

```bash
# Topic erstellen (3 Partitionen, keine Replikation)
docker exec -it retailops-lakehouse-kafka-1 \
  kafka-topics --bootstrap-server kafka:9092 --create \
  --topic orders.v1 --partitions 3 --replication-factor 1

# Kontrolle
docker exec -it retailops-lakehouse-kafka-1 \
  kafka-topics --bootstrap-server kafka:9092 --describe --topic orders.v1
```

## Bronze Layer (Orders)

Erster Streaming-Job für den **Bronze Layer** mit Spark:

- **Quelle:** Kafka-Topic `orders.v1` (Datenstrom aus Producer)
- **Verarbeitung:** Spark Structured Streaming mit Kafka-Connector
- **Ziel:** Speicherung der Rohdaten als **Parquet-Dateien** im Lake (`lake/bronze/orders/`)
- **Struktur:** Partitionierung nach `p_date` (z. B. `p_date=2025-09-29`)
- **Nutzen:**
  - Persistente Ablage der eingehenden Rohdaten
  - Grundlage für weitere Transformationen in Silver/Gold Layer
  - Sicherung auch bei Streaming-Ausfällen

## Bronze Job manuell starten

Der Bronze-Job kann manuell gestartet werden, **sobald der Producer Nachrichten ins Kafka-Topic `orders.v1` schreibt**:

```bash
# 1) Ivy-Cache anlegen (nur einmal nötig)
docker exec retailops-lakehouse-spark-1 mkdir -p /tmp/.ivy2

# 2) Job starten (mit ENV Variablen)
docker exec -it \
  -u 0 \
  -e USER=root \
  -e HOME=/root \
  -e HADOOP_USER_NAME=root \
  -e BRONZE_OUTPUT_PATH=/lake/bronze/orders \
  -e BRONZE_CHECKPOINT_PATH=/lake/checkpoints/orders_bronze \
  -e BRONZE_BAD_PATH=/lake/bronze/orders_corrupt \
  retailops-lakehouse-spark-1 \
  /opt/bitnami/spark/bin/spark-submit \
    --conf spark.jars.ivy=/tmp/.ivy2 \
    --conf spark.hadoop.hadoop.security.authentication=simple \
    --conf "spark.driver.extraJavaOptions=-Duser.name=root" \
    --conf "spark.executor.extraJavaOptions=-Duser.name=root" \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    /opt/spark_jobs/bronze_orders.py
```

## Tests

Unit- und Build-Tests für den Kafka Producer sowie für den Bronze-Job sind enthalten.
Lokal ausführen mit:

```bash
poetry run pytest
```

Die Tests prüfen Producer-Logik, Schema-Validierung und einen Smoke-Test für den Bronze-Stream.
Sie laufen außerdem automatisch in GitHub Actions (CI).

Die Tests laufen außerdem automatisch in GitHub Actions (CI).
