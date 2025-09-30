#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi

echo "==> Zeige Bronze-Logs aus $SPARK_CONTAINER:/tmp/bronze.log"
docker exec -it "$SPARK_CONTAINER" sh -lc '
  if [ -f /tmp/bronze.log ]; then
    tail -n 200 -f /tmp/bronze.log
  else
    echo "⚠️  Keine /tmp/bronze.log gefunden"
    exit 1
  fi
'