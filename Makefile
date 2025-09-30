# Makefile

.PHONY: up producer topic bronze logs head down

up:
	@./scripts/start_stack.sh

producer:
	@{ [ -f .env ] || echo "Hinweis: .env nicht gefunden – nutze Defaults"; } >/dev/null; \
	set -a; [ -f .env ] && . .env; set +a; \
	poetry run python data_gen/produce_orders.py \
		--bootstrap "$${KAFKA_BOOTSTRAP:-localhost:9093}" \
		--topic "$${TOPIC:-orders.v1}" \
		--eps "$${EPS:-10}" \
		--max "$${MAX_EVENTS:-0}" \
		$${SEED:+--seed $$SEED}

topic:
	@set -a; [ -f .env ] && . .env; set +a; \
	docker exec -it "$${KAFKA_CONTAINER:-retailops-lakehouse-kafka-1}" \
	  kafka-topics --bootstrap-server kafka:9092 --describe --topic "$${TOPIC:-orders.v1}"

bronze:
	@./scripts/run_bronze.sh

logs:
	@set -a; [ -f .env ] && . .env; set +a; \
	docker exec -it "$${SPARK_CONTAINER:-retailops-lakehouse-spark-1}" \
	  sh -lc '[ -f /tmp/bronze.log ] && tail -n 200 -f /tmp/bronze.log || echo "kein /tmp/bronze.log"'

head:
	@./scripts/head_bronze.sh

down:
	@DO_DOWN=true ./scripts/stop_stack.sh