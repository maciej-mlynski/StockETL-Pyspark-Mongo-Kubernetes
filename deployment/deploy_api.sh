#!/bin/bash
set -e

# This script deploys the main application (FastAPI + Mongo)
# in the 'stock-api-namespace'. It also rebuilds the Docker image if needed.

# 1. Check if stock-api-namespace exists -> if not create one
echo "Checking if 'stock-api-namespace' exists..."
kubectl get namespace stock-api-namespace || kubectl create namespace stock-api-namespace
echo "stock-api-namespace is ready!"

# 2. Remove the Docker image (if it exists)
echo "Removing local Docker image 'stock-api-app:latest' if it exists..."
docker rmi stock-api-app:latest --force || true

# 3. Configure Docker environment for Minikube
echo "Configuring Docker environment for Minikube..."
eval $(minikube docker-env)

# 4. Build the Docker image for FastAPI, Mongo & Spark
echo "Building the Docker image 'stock-api-app:latest'..."
docker build -t stock-api-app:latest -f docker/API/Dockerfile .

# 5. Apply Kubernetes manifests for Spark-history
echo "Applying PV & PVC for Spark logs..."
kubectl apply -f minikube/spark_logs/spark-history-pv-pvc.yaml -n stock-api-namespace
echo "Applying Spark-history manifests..."
kubectl apply -f minikube/spark_logs/spark-history-server.yaml -n stock-api-namespace
kubectl apply -f minikube/spark_logs/spark-history-service.yaml -n stock-api-namespace

# 6. Apply Kubernetes manifests for FastAPI app
echo "Applying FastAPI manifests..."
kubectl apply -f minikube/api/stock-api-deployment.yaml -n stock-api-namespace
kubectl apply -f minikube/api/stock-api-service.yaml -n stock-api-namespace

# 7. Copy minio secrets
kubectl delete secret minio-secret -n stock-api-namespace --ignore-not-found
kubectl get secret minio-secret -n minio-dev -o yaml \
| sed 's/namespace: minio-dev/namespace: stock-api-namespace/' \
| kubectl apply -f -

# 8. Check pods
echo "Checking pods in 'stock-api-namespace'..."
kubectl get pods -n stock-api-namespace

# Final info
echo "To see the FastAPI deployment logs, run:"
echo "  kubectl logs deployment/stock-api-deployment -n stock-api-namespace"

echo "To access the FastAPI service via Minikube, run:"
echo "  minikube service stock-api-service -n stock-api-namespace"
