.PHONY: build down run run-scaled run-d stop submit

build:
	docker-compose build

down:
	docker-compose down --volumes

run:
	make down && docker-compose up

run-scaled:
	make down && docker-compose up --scale spark-worker=5

run-d:
	make down && docker-compose up -d

stop:
	docker-compose stop

# Usage: make submit app=<path_to_app_script>
submit:
	docker exec spark-master spark-submit --master spark://spark-master:7077 --deploy-mode client ./apps/$(app)
