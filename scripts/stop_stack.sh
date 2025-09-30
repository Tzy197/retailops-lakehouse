#!/usr/bin/env bash
set -euo pipefail

# --- .env laden + Defaults ---
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
fi

# --- Helper ---
container_running() {
  docker ps --format '{{.Names}}' | grep -qx "$1"
}

echo "==> Bronze-Job (falls laufend) beenden…"
if container_running "$SPARK_CONTAINER"; then
  # Versuche, einen evtl. laufenden bronze_orders-Job im Container zu beenden
  docker exec "$SPARK_CONTAINER" sh -lc '
    set -e
    PIDS=$(ps -eo pid,cmd \
      | grep -E "spark-submit.*bronze_orders\.py|python .*bronze_orders\.py" \
      | grep -v grep \
      | awk "{print \$1}")
    if [ -n "$PIDS" ]; then
      echo "Gefundene PIDs: $PIDS"
      kill -TERM $PIDS || true
      sleep 2
      kill -KILL $PIDS || true
    else
      echo "Kein Bronze-Prozess gefunden – überspringe."
    fi
  ' || true
else
  echo "Spark-Container '$SPARK_CONTAINER' läuft nicht – überspringe Bronze-Stop."
fi

echo "==> Docker-Stack herunterfahren…"
# Orphans entfernen, aber nicht hart fehlschlagen, wenn schon down
docker compose down --remove-orphans || true

echo "✅ Stop abgeschlossen."
exit 0