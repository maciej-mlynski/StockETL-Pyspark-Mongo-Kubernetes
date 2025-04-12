#!/bin/bash
set -e

# Input param (folder name) -> specific folder or all
FOLDER_NAME="$1"

if [ -z "$FOLDER_NAME" ]; then
  echo "Error: No folder name provided."
  echo "Usage: ./load_raw_data_minio.sh <folder_name>|all"
  exit 1
fi

echo "WARNING: Each time this script is executed, existing data will be overwritten!"

MINIO_ALIAS="myminio"
RAW_BUCKET="rawstockdata"
STOCK_BUCKET="stockdata"
LOCAL_FOLDER_PATH="RawStockData"
MINIO_SERVICE="minio-service"
MINIO_NAMESPACE="minio-dev"

MINIO_USER=$(kubectl get secret minio-secret -n $MINIO_NAMESPACE -o jsonpath="{.data.minio-access-key}" | base64 --decode)
MINIO_PASSWORD=$(kubectl get secret minio-secret -n $MINIO_NAMESPACE -o jsonpath="{.data.minio-secret-key}" | base64 --decode)

# Start minikube service for minio
minikube service $MINIO_SERVICE -n $MINIO_NAMESPACE --url > minio_url.txt &
sleep 5

# Get minio URLs from files
MINIO_URL=$(head -n1 minio_url.txt)

# Set-up MinIO client
mc alias set $MINIO_ALIAS "$MINIO_URL" "$MINIO_USER" "$MINIO_PASSWORD"

# Create buckets
mc mb --ignore-existing $MINIO_ALIAS/$RAW_BUCKET
mc mb --ignore-existing $MINIO_ALIAS/$STOCK_BUCKET

upload_folder() {
  local folder="$1"
  if [ -d "$folder" ]; then
    echo "Loading folder from: $folder"
    mc cp --recursive "$folder" "$MINIO_ALIAS/$RAW_BUCKET/"
  else
    echo "Folder does not exist: $folder"
    exit 1
  fi
}


if [ "$FOLDER_NAME" == "all" ]; then
  for folder in "$LOCAL_FOLDER_PATH"/*; do
    [ -d "$folder" ] && upload_folder "$folder"
  done
else
  upload_folder "$LOCAL_FOLDER_PATH/$FOLDER_NAME"
fi

echo "All data uploaded to MinIO."

echo "MinIO rawstockdata bucket summary:"
mc du --recursive $MINIO_ALIAS/$RAW_BUCKET/
echo "Keep in mind that in MinIO UI you might see less objects than was actually loaded into S3."

# Extract the port from MINIO_URL (assumes the URL is in the form http://<host>:<port>)
PORT=$(echo "$MINIO_URL" | awk -F ':' '{print $NF}')
echo "Identified port: $PORT"

# Find the PID of the process listening on that port
PID_ON_PORT=$(lsof -t -i :"$PORT")
echo "Closing the process listening on port $PORT (PID: $PID_ON_PORT)..."
kill -9 "$PID_ON_PORT"

rm -f minio_url.txt

echo "If you want to open minio UI to see uploaded data run:"
echo "make minio-ui"
