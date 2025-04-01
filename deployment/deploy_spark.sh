#!/bin/bash
set -e

# This script deploys the Spark Master & Worker

# 1. Check if spark-namespace exists -> if not create one
echo "Checking if 'spark-namespace' exists..."
kubectl get namespace spark-namespace || kubectl create namespace spark-namespace
echo "spark-namespace is ready!"


# 3. Apply Kubernetes manifests for Spark (bitnami/spark:3.5.5 image used)
echo "Applying Spark-master manifests from bitnami/spark:3.5.5..."
kubectl apply -f minikube/spark/spark-master-deployment.yaml
echo "Applying Spark-worker manifests from bitnami/spark:3.5.5..."
kubectl apply -f minikube/spark/spark-worker-deployment.yaml

# 4. Check pods
echo "Checking pods in 'spark-namespace'..."
kubectl get pods -n spark-namespace