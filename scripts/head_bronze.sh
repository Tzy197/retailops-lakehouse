#!/usr/bin/env bash
set -euo pipefail

# --- .env laden + Defaults ---
ENV_FILE="${ENV_FILE:-.env}"
if [ -f "$ENV_FILE" ]; then
  set -a
  . "$ENV_FILE"
  set +a
fi

#!/usr/bin/env bash
set -euo pipefail
source .env

SQL="
CREATE OR REPLACE TEMP VIEW bronze_orders
USING parquet
OPTIONS (path '${BRONZE_OUTPUT_PATH}');

SELECT
  p_date,
  order_id,
  customer_id,
  total_amount,
  country,
  ingested_at
FROM bronze_orders
ORDER BY ingested_at DESC
LIMIT 5
"

docker exec -it \
  -u 0 \
  -e USER=root \
  -e HOME=/root \
  -e HADOOP_USER_NAME=root \
  "${SPARK_CONTAINER}" \
  /opt/bitnami/spark/bin/spark-sql \
    --conf spark.hadoop.hadoop.security.authentication=simple \
    -e "${SQL}"