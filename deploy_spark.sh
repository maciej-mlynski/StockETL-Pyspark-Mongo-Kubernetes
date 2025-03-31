#!/bin/bash
set -e

# This script deploys the Spark Master & Worker

# 1. Delete the namespace if it exists
echo "Deleting namespace 'stock-etl-namespace' (if it exists)..."
kubectl delete namespace spark-namespace --ignore-not-found

# 2. Create the namespace
echo "Creating namespace 'spark-namespace'..."
kubectl create ns spark-namespace

# 3. Apply Kubernetes manifests for Spark (bitnami/spark:3.5.5 image used)
echo "Applying Spark-master manifests from bitnami/spark:3.5.5..."
kubectl apply -f minikube/spark/spark-master-deployment.yaml
echo "Applying Spark-worker manifests from bitnami/spark:3.5.5..."
kubectl apply -f minikube/spark/spark-worker-deployment.yaml

# 4. Check pods
echo "Checking pods in 'spark-namespace'..."
kubectl get pods -n spark-namespace