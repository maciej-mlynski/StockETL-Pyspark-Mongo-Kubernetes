#!/bin/bash
set -e

# This script deploys Minio on Kubernetes.
# YAML files are located in the directory: stock_minikube/minio

# Delete the namespace if it exists and create a new one
echo "Deleting namespace 'minio-dev' (if exists)..."
kubectl delete namespace minio-dev --ignore-not-found
echo "Creating namespace 'minio-dev'..."
kubectl create namespace minio-dev

# Persistent Volumes (PV) and Persistent Volume Claims (PVC)
# Delete existing PVs for a clean installation (data in /data remains persistent)
echo "Deleting existing PVs: minio-volume-0 and minio-volume-1 (if they exist)..."
kubectl delete pv minio-volume-0 --ignore-not-found
kubectl delete pv minio-volume-1 --ignore-not-found

echo "Applying Persistent Volume (PV)..."
kubectl apply -f minikube/minio/minio-pv.yaml -n minio-dev

echo "Applying Persistent Volume Claim (PVC)..."
kubectl apply -f minikube/minio/minio-pvclaim.yaml -n minio-dev

# Secret
# The secret key is set to "minio123". Feel free to change the value in the minio-secret.yaml file.
echo "Encoding password 'minio123' in base64:"
encoded_secret=$(echo -n 'minio123' | base64)
echo "Encoded password: $encoded_secret"

echo "Applying Secret..."
kubectl apply -f minikube/minio/minio-secret.yaml -n minio-dev

# Deploy Minio
# Deploy the StatefulSet, headless service, and service for Minio.
echo "Deploying Minio StatefulSet..."
kubectl apply -f minikube/minio/minio-sts.yaml -n minio-dev

echo "Deploying Minio headless service..."
kubectl apply -f minikube/minio/minio-headless-service.yaml -n minio-dev

echo "Deploying Minio service..."
kubectl apply -f minikube/minio/minio-service.yaml -n minio-dev

# Optionally add a DNS entry to use the hostname minio.kubernetes.net
echo "If you want to use DNS, run the following command:"
echo 'echo "127.0.0.1 minio.kubernetes.net" | sudo tee -a /etc/hosts'

# Troubleshooting commands
echo "------------------------------"
echo "Troubleshooting commands:"
echo "kubectl get pv"
echo "kubectl get pvc -n minio-dev"
echo "kubectl get all -n minio-dev"
echo "kubectl get pods -n minio-dev"
echo "kubectl describe statefulset -n minio-dev"
echo "kubectl describe pod datasaku-minio-0 -n minio-dev"
echo "kubectl get svc -n minio-dev"
echo "------------------------------"

echo "Minio deployment completed successfully."
