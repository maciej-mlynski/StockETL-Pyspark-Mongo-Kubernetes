#!/bin/bash

# 1. Configure Docker to use Minikube's Docker daemon
echo "=== 1. Configuring Docker environment for Minikube ==="
eval $(minikube docker-env)

# 2. Build the Docker image for the FastAPI application
echo "=== 2. Building the Docker image for FastAPI ==="
docker build -t stock-etl-app:latest -f stock_docker/Dockerfile .

# 3. Create the 'stock-etl-namespace' if it does not already exist
echo "=== 3. Creating 'stock-etl-namespace' (if not exists) ==="
kubectl create namespace stock-etl-namespace 2>/dev/null || true

# 4. Deploy MongoDB, the FastAPI app, and the Service within 'stock-etl-namespace'
echo "=== 4. Applying Kubernetes manifests for MongoDB and FastAPI app ==="
kubectl apply -f stock_minikube/mongo/mongo-deployment.yaml -n stock-etl-namespace
kubectl apply -f stock_minikube/app/stock-etl-deployment.yaml -n stock-etl-namespace
kubectl apply -f stock_minikube/app/stock-etl-service.yaml -n stock-etl-namespace

# 5. Check the pods status in the namespace
echo "=== 5. Checking pods in 'stock-etl-namespace' ==="
kubectl get pods -n stock-etl-namespace

## 6. Retrieve logs from the FastAPI deployment
#echo "=== 6. Fetching logs from 'stock-etl-deployment' ==="
#kubectl logs deployment/stock-etl-deployment -n stock-etl-namespace
#
## 7. Access the FastAPI service through Minikube
#echo "=== 7. Opening the FastAPI service via 'minikube service' ==="
#minikube service stock-etl-service -n stock-etl-namespace
