#!/bin/bash
set -e

# This script deploys the main application (FastAPI + Mongo)
# in the 'stock-etl-namespace'. It also rebuilds the Docker image if needed.

# 1. Delete the namespace if it exists
echo "Deleting namespace 'stock-etl-namespace' (if it exists)..."
kubectl delete namespace stock-etl-namespace --ignore-not-found

# 1a. Create the namespace
echo "Creating namespace 'stock-etl-namespace'..."
kubectl create ns stock-etl-namespace

# 2. Remove the Docker image (if it exists)
echo "Removing local Docker image 'stock-etl-app:latest' if it exists..."
docker rmi stock-etl-app:latest --force || true

# 3. Configure Docker environment for Minikube
echo "Configuring Docker environment for Minikube..."
eval $(minikube docker-env)

# 4. Build the Docker image for FastAPI, Mongo & Spark
echo "Building the Docker image 'stock-etl-app:latest'..."
docker build -t stock-etl-app:latest -f docker/Dockerfile .

# 5. Apply Kubernetes manifests for MongoDB
echo "Applying MongoDB manifests..."
kubectl apply -f minikube/mongo/mongo-deployment.yaml -n stock-etl-namespace

# 6. Apply Kubernetes manifests for FastAPI app
echo "Applying FastAPI (app) manifests..."
kubectl apply -f minikube/app/stock-etl-deployment.yaml -n stock-etl-namespace
kubectl apply -f minikube/app/stock-etl-service.yaml -n stock-etl-namespace

# 7. Copy minio secrets
kubectl get secret minio-secret -n minio-dev -o yaml \
| sed 's/namespace: minio-dev/namespace: stock-etl-namespace/' \
| kubectl apply -f -

# 8. Check pods
echo "Checking pods in 'stock-etl-namespace'..."
kubectl get pods -n stock-etl-namespace

# Final info
echo "To see the FastAPI deployment logs, run:"
echo "  kubectl logs deployment/stock-etl-deployment -n stock-etl-namespace"

echo "To access the FastAPI service via Minikube, run:"
echo "  minikube service stock-etl-service -n stock-etl-namespace"
