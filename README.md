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

## Tests

Unit- und Build-Tests für den Kafka Producer sind enthalten.  
Lokal ausführen mit:

```bash
poetry run pytest
```

Die Tests laufen außerdem automatisch in GitHub Actions (CI).
