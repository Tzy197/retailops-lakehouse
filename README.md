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
