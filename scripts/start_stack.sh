#!/usr/bin/env bash
set -euo pipefail

# .env laden (falls vorhanden) und Variablen exportieren
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
fi

echo "==> docker compose up…"
docker compose up -d

echo "==> warte auf Kafka…"
for i in {1..30}; do
  if docker exec "$KAFKA_CONTAINER" kafka-topics --bootstrap-server kafka:9092 --list >/dev/null 2>&1; then break; fi
  sleep 1
done

echo "==> Topic prüfen/erstellen: $TOPIC"
if ! docker exec "$KAFKA_CONTAINER" kafka-topics --bootstrap-server kafka:9092 --list | grep -q "^${TOPIC}\$"; then
  docker exec -it "$KAFKA_CONTAINER" kafka-topics \
    --bootstrap-server kafka:9092 \
    --create --topic "$TOPIC" \
    --partitions "$PARTITIONS" \
    --replication-factor "$REPLICATION"
else
  echo "    Topic existiert."
fi

echo "==> Ivy-Cache im Spark-Container…"
docker exec "$SPARK_CONTAINER" mkdir -p /tmp/.ivy2

echo "✅ Stack bereit. Starte nun: make bronze  (oder ./scripts/run_bronze.sh)"