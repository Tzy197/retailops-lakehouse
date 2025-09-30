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

## Lokale Befehle

Die wichtigsten Schritte laufen jetzt über das `Makefile`.  
Vorher `.env.example` kopieren und ggf. anpassen (enthält Container-Namen und Pfade):

```bash
cp .env.example .env

# Stack starten (Zookeeper, Kafka, Spark, MinIO, Postgres, Airflow)
make up
# Producer starten (Events ins Kafka-Topic schicken)
make producer
# Bronze-Streaming-Job starten
make bronze
# Logs des Bronze-Jobs verfolgen
make logs
# Kafka-Topic-Infos anzeigen
make topic
# Einen Blick in die ersten Parquet-Dateien werfen
make head
# Stack stoppen
make down
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

Unit- und Build-Tests für den Kafka Producer sowie für den Bronze-Job sind enthalten.
Lokal ausführen mit:

```bash
poetry run pytest
```

Die Tests prüfen Producer-Logik, Schema-Validierung und einen Smoke-Test für den Bronze-Stream.
Sie laufen außerdem automatisch in GitHub Actions (CI).
