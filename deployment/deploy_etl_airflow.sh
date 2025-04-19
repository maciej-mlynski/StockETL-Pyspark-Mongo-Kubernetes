#!/bin/bash
set -e

# 1. Check if 'airflow' namespace exists -> if not, create it
echo "Checking if 'airflow' namespace exists..."
kubectl delete namespace airflow --ignore-not-found
kubectl create namespace airflow
echo "Namespace 'airflow' is ready!"

# 2. Remove the Docker image (if it exists)
echo "Removing local Docker image 'airflow-stock:latest' if it exists..."
docker rmi airflow-stock:latest --force || true

# 3. Configure Docker environment for Minikube
echo "Configuring Docker environment for Minikube..."
eval "$(minikube docker-env)"

# 4. Build the Docker image for Airflow
echo "Building the Docker image 'airflow-stock:latest'..."
docker build -t airflow-stock:latest -f docker/AIRFLOW/Dockerfile .

# 5. Copy minio secrets into 'airflow' namespace
echo "Copying minio-secret into 'airflow' namespace..."
kubectl delete secret minio-secret -n airflow --ignore-not-found
kubectl get secret minio-secret -n minio-dev -o yaml \
  | sed 's/namespace: minio-dev/namespace: airflow/' \
  | kubectl apply -f -

# 6. Apply spark role-binding
echo "Applying airflow service account & role-binding..."
kubectl apply -f minikube/etl_airflow/airflow-service-account.yaml
kubectl apply -f minikube/etl_airflow/airflow-spark-role.yaml
kubectl apply -f minikube/etl_airflow/airflow-spark-rolebinding.yaml

# 7. Deploy Postgres
echo "Applying Postgres manifests..."
kubectl apply -f minikube/etl_airflow/postgres-deployment.yaml

# 8. Deploy Airflow (webserver + scheduler)
echo "Applying airflow deployments & service manifests..."
kubectl apply -f minikube/etl_airflow/airflow-deployment.yaml
kubectl apply -f minikube/etl_airflow/airlow-scheduler-deployment.yaml

# 9. Some helpful status commands
echo "Deployments in 'airflow' namespace:"
kubectl get deployments -n airflow
echo
echo "Pods in 'airflow' namespace:"
kubectl get pods -n airflow
echo
echo "To view logs, use: kubectl logs -n airflow <pod-name>"
echo "To open the UI, run: minikube service airflow-webserver-svc -n airflow --url"
