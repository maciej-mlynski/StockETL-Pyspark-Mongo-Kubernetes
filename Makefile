.PHONY: run-minikube check-stock-app check-spark check-spark fwd-spark minio-ui run-app log-app log-spark-master log-spark-worker restart-app

run-minikube:
	minikube start

check-stock-app:
	 kubectl get pods -n stock-etl-namespace

check-spark:
	kubectl get pods -n spark-namespace

check-minio:
	kubectl get pods -n minio-dev

fwd-spark:
	 kubectl port-forward deployment/spark-master-deployment 8080:8080 -n spark-namespace

minio-ui:
	 minikube service minio-service -n minio-dev

run-app:
	minikube service stock-etl-service -n stock-etl-namespace

log-app:
	kubectl logs deployment/stock-etl-deployment -n stock-etl-namespace

log-spark-master:
	kubectl logs deployment/spark-master-deployment -n spark-namespace

log-spark-worker:
	kubectl logs deployment/spark-worker-deployment -n spark-namespace

restart-app:
	kubectl rollout restart deployment stock-etl-deployment -n stock-etl-namespace
