#!/usr/bin/env bash
set -euo pipefail

# .env laden
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
  set -a; . "$ENV_FILE"; set +a
fi

echo "==> Starte Bronze-Job detached…"
docker exec -u 0 -d "$SPARK_CONTAINER" sh -lc "\
  export USER=root HOME=/root HADOOP_USER_NAME=root \
         JAVA_TOOL_OPTIONS='-Duser.name=root' \
         SPARK_SUBMIT_OPTS='-Duser.name=root' \
         PYSPARK_PYTHON=/opt/bitnami/python/bin/python \
         PYSPARK_DRIVER_PYTHON=/opt/bitnami/python/bin/python \
         BRONZE_OUTPUT_PATH='${BRONZE_OUTPUT_PATH}' \
         BRONZE_CHECKPOINT_PATH='${BRONZE_CHECKPOINT_PATH}' \
         BRONZE_BAD_PATH='${BRONZE_BAD_PATH}' \
         KAFKA_BOOTSTRAP='${KAFKA_BOOTSTRAP:-kafka:9092}' \
         TOPIC='${TOPIC:-orders.v1}' \
         STARTING_OFFSETS='${STARTING_OFFSETS:-earliest}'; \
  nohup /opt/bitnami/spark/bin/spark-submit \
    --conf spark.jars.ivy=/tmp/.ivy2 \
    --conf spark.hadoop.hadoop.security.authentication=simple \
    --conf 'spark.driver.extraJavaOptions=-Duser.name=root' \
    --conf 'spark.executor.extraJavaOptions=-Duser.name=root' \
    --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.5.0 \
    /opt/spark_jobs/bronze_orders.py \
    > /tmp/bronze.log 2>&1 & echo \$! > /tmp/bronze.pid
"
echo "✅ Bronze läuft. Logs: make logs   |  Head: make head"