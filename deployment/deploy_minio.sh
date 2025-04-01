#!/bin/bash
set -e

# This script deploys Minio on Kubernetes.
# YAML files are located in the directory: stock_minikube/minio

# 1. Check if minio-dev exists -> if not create one
echo "Checking if 'minio-dev' exists..."
kubectl get namespace minio-dev || kubectl create namespace minio-dev
echo "minio-dev is ready!"

# Persistent Volumes (PV) and Persistent Volume Claims (PVC)
# Delete existing PVs for a clean installation (data in /data remains persistent)
#echo "Deleting existing PVs: minio-volume-0 and minio-volume-1 (if they exist)..."
#kubectl delete pv minio-volume-0 --ignore-not-found
#kubectl delete pv minio-volume-1 --ignore-not-found

echo "Applying Persistent Volume (PV)..."
kubectl apply -f minikube/minio/minio-pv.yaml -n minio-dev

echo "Applying Persistent Volume Claim (PVC)..."
kubectl apply -f minikube/minio/minio-pvclaim.yaml -n minio-dev

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
