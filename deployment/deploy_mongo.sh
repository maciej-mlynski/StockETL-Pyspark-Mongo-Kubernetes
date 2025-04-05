#!/bin/bash
set -e

# This script deploys the Mongo DB including PV & PVC


# 1. Check if stock-mongo-namespace exists -> if not create one
echo "Checking if 'stock-mongo-namespace' exists..."
kubectl get namespace stock-mongo-namespace || kubectl create namespace stock-mongo-namespace
echo "stock-mongo-namespace is ready!"


# 5. Apply Kubernetes manifests for MongoDB
echo "Applying Persistent Volume (PV) for Mongo..."
kubectl apply -f minikube/mongo/mongo-pv.yaml -n stock-mongo-namespace
echo "Applying Persistent Volume Claim (PVC) for Mongo..."
kubectl apply -f minikube/mongo/mongo-pvc.yaml -n stock-mongo-namespace
echo "Applying MongoDB manifests..."
kubectl apply -f minikube/mongo/mongo-deployment.yaml -n stock-mongo-namespace


echo "Checking pods in 'stock-mongo-namespace'..."
kubectl get pods -n stock-mongo-namespace