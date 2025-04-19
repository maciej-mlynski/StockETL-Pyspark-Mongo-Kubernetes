#!/bin/bash
set -e

echo "Deleting spark for ETL namespaces (if exists)..."
kubectl delete sparkapplication spark-stock-etl-job -n spark-jobs || true
kubectl delete namespace spark-operator --ignore-not-found
kubectl delete namespace spark-jobs --ignore-not-found

echo "Creating new spark-etl namespaces..."
kubectl create namespace spark-operator
kubectl create namespace spark-jobs

echo "Removing local Docker image 'stock-etl-app:latest' if it exists..."
docker rmi stock-etl-app:latest --force || true

echo "Configuring Docker environment for Minikube..."
eval $(minikube docker-env)

echo "Building the Docker image 'stock-etl-app:latest'..."
docker build -t stock-etl-app:latest -f docker/ETL/Dockerfile .

echo "Installing spark-operator via Helm..."
helm repo remove spark-operator || true
helm repo add spark-operator https://kubeflow.github.io/spark-operator
helm repo update

helm install spark-operator spark-operator/spark-operator \
  --namespace spark-operator \
  --create-namespace \
  --set "spark.jobNamespaces={spark-jobs}" \
  --set webhook.enable=true \
  --set webhook.port=443 \
  --set enableBatchScheduler=true \
  --set enableMetrics=true

echo "Creating spark-jobs service account..."
kubectl create serviceaccount spark -n spark-jobs

echo "Applying RBAC for spark-operator..."
kubectl apply -f minikube/etl_spark_operator/spark-operator-rbac.yaml

echo "Adding Mino secrets to spark-jobs..."
kubectl delete secret minio-secret -n spark-jobs --ignore-not-found
kubectl get secret minio-secret -n minio-dev -o yaml \
  | sed 's/namespace: minio-dev/namespace: spark-jobs/' \
  | kubectl apply -f -

echo "Environment is ready to perform first ETL process!"
echo "WARNING! Load raw data into S3 to trigger ETL"
