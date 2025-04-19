.PHONY: run-minikube check-stock-app check-spark check-spark fwd-spark minio-ui run-app log-app log-spark-master log-spark-worker restart-app

####################################### API cmd #######################################
check-api:
	kubectl get pods -n stock-api-namespace

spark-logs-ui:
	minikube service spark-history-service -n stock-api-namespace

log-spark-history:
	kubectl logs deployment/spark-history-server -n stock-api-namespace

log-api:
	kubectl logs deployment/stock-api-deployment -n stock-api-namespace

run-api:
	minikube service stock-api-service -n stock-api-namespace

redeploy-api:
	./deployment/deploy_api.sh
	kubectl rollout restart deployment stock-api-deployment -n stock-api-namespace
	kubectl rollout restart deployment spark-history-server -n stock-api-namespace


####################################### Spark cluster cmd #######################################
check-spark:
	kubectl get pods -n spark-namespace

log-spark-master:
	kubectl logs deployment/spark-master-deployment -n spark-namespace

log-spark-worker:
	kubectl logs deployment/spark-worker-deployment -n spark-namespace

fwd-spark:
	kubectl port-forward deployment/spark-master-deployment 8080:8080 -n spark-namespace

redeploy-spark:
	./deployment/deploy_spark.sh
	kubectl rollout restart deployment spark-master-deployment -n spark-namespace
	kubectl rollout restart deployment spark-worker-deployment -n spark-namespace


####################################### MINIO cmd #######################################
check-minio:
	kubectl get pods -n minio-dev

minio-ui:
	minikube service minio-service -n minio-dev

log-minio:
	kubectl describe pod datasaku-minio-0 -n minio-dev

redeploy-minio:
	./deployment/deploy_minio.sh
	kubectl rollout restart statefulset datasaku-minio -n minio-dev
	echo "Redeploying api & spark might be required depending on the change!"


####################################### Mongo cmd #######################################
check-mongo:
	kubectl get pods -n stock-mongo-namespace

mongo-sh:
	@POD_NAME=$$(kubectl get pods -n stock-mongo-namespace -l app=mongo -o jsonpath='{.items[0].metadata.name}'); \
	kubectl exec -it $$POD_NAME -n stock-mongo-namespace -- mongosh

log-mongo:
	kubectl logs deployment/mongo-deployment -n stock-mongo-namespace

redeploy-mongo:
	./deployment/deploy_mongo.sh
	kubectl rollout restart deployment mongo-deployment -n stock-mongo-namespace



####################################### ETL with Airflow cmd #######################################
check-etl:
	kubectl get pods -n spark-jobs

check-airflow:
	kubectl get pods -n airflow

airflow-ui:
	minikube service airflow-webserver-svc -n airflow

log-etl:
	@if [ -z "$(ID)" ]; then \
	  echo "Usage: make log-etl ID=<number>"; \
	  exit 1; \
	fi
	kubectl logs spark-stock-etl-$(ID)-driver -n spark-jobs -f

log-airflow:
	kubectl logs deployment/airflow-webserver -n airflow

airflow-artefacts:
	kubectl exec -it deployment/airflow-scheduler -n airflow -- /bin/bash

redeploy-etl:
	./deployment/deploy_etl_spark_operator.sh

redeploy-airflow:
	./deployment/deploy_etl_airflow.sh
	kubectl rollout status deployment/airflow-webserver -n airflow
	kubectl rollout status deployment/airflow-scheduler -n airflow