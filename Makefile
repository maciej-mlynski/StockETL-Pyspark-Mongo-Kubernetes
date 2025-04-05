.PHONY: run-minikube check-stock-app check-spark check-spark fwd-spark minio-ui run-app log-app log-spark-master log-spark-worker restart-app

run-minikube:
	minikube start

check-api:
	kubectl get pods -n stock-api-namespace

check-spark:
	kubectl get pods -n spark-namespace

check-minio:
	kubectl get pods -n minio-dev

check-mongo:
	kubectl get pods -n stock-mongo-namespace

fwd-spark:
	kubectl port-forward deployment/spark-master-deployment 8080:8080 -n spark-namespace

mongo-sh:
	@POD_NAME=$$(kubectl get pods -n stock-mongo-namespace -l app=mongo -o jsonpath='{.items[0].metadata.name}'); \
	kubectl exec -it $$POD_NAME -n stock-mongo-namespace -- mongosh

minio-ui:
	minikube service minio-service -n minio-dev

spark-logs-ui:
	minikube service spark-history-service -n stock-api-namespace

run-api:
	minikube service stock-api-service -n stock-api-namespace

log-api:
	kubectl logs deployment/stock-api-deployment -n stock-api-namespace

log-mongo:
	kubectl logs deployment/mongo-deployment -n stock-mongo-namespace

log-spark-history:
	kubectl logs deployment/spark-history-server -n stock-api-namespace

log-spark-master:
	kubectl logs deployment/spark-master-deployment -n spark-namespace

log-spark-worker:
	kubectl logs deployment/spark-worker-deployment -n spark-namespace

redeploy-api:
	./deployment/deploy_api.sh
	kubectl rollout restart deployment stock-api-deployment -n stock-api-namespace
	kubectl rollout restart deployment spark-history-server -n stock-api-namespace

redeploy-mongo:
	./deployment/deploy_mongo.sh
	kubectl rollout restart deployment mongo-deployment -n stock-mongo-namespace

redeploy-spark:
	./deployment/deploy_spark.sh
	kubectl rollout restart deployment spark-master-deployment -n spark-namespace
	kubectl rollout restart deployment spark-worker-deployment -n spark-namespace
	kubectl rollout restart deployment spark-history-server -n spark-namespace

redeploy-minio:
	./deployment/deploy_minio.sh
	kubectl rollout restart statefulset datasaku-minio -n minio-dev
	echo "Redeploying api & spark namespace might be required depending on the change!"
