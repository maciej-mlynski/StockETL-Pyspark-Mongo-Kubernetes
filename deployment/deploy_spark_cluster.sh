#!/bin/bash
set -e

# This script deploys the Spark Master & Worker

#1. Delete spark-namespace if exists
echo "Deleting 'spark-namespace' (if exists)..."
kubectl delete namespace spark-namespace --ignore-not-found

#2. Create spark-namespace
echo "Creating spark-namespace"
kubectl create namespace spark-namespace

#3. Apply Kubernetes manifests for Spark (bitnami/spark:3.5.5 image used)
echo "Applying Spark-master manifests from bitnami/spark:3.5.5..."
kubectl apply -f minikube/spark_cluster/spark-master-deployment.yaml
echo "Applying Spark-worker manifests from bitnami/spark:3.5.5..."
kubectl apply -f minikube/spark_cluster/spark-worker-deployment.yaml

#4. Check pods
echo "Checking pods in 'spark-namespace'..."
kubectl get pods -n spark-namespace