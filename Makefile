.PHONY: build down run run-scaled run-d stop submit drop-project

build:
	docker-compose -f stock_docker/docker-compose.yaml build

down:
	docker-compose -f stock_docker/docker-compose.yaml down --volumes

run:
	make down && docker-compose -f stock_docker/docker-compose.yaml up

run-scaled:
	make down && docker-compose -f stock_docker/docker-compose.yaml up --scale spark-worker=5

run-d:
	make down && docker-compose -f stock_docker/docker-compose.yaml up -d

stop:
	docker-compose -f stock-docker/stock_docker.yaml stop

# Usage: make submit app=<path_to_app_script>
submit:
	docker exec spark-master spark-submit --master spark://spark-master:7077 --deploy-mode client ./apps/$(app)

# Drop only images with the 'stock-etl' prefix
drop-project:
	@images=$$(docker images --filter=reference='stock-etl*' -q); \
	if [ -n "$$images" ]; then \
		docker rmi $$images; \
	else \
		echo "No stock-etl images to remove"; \
	fi