#!/bin/bash
set -e

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
TUNNEL_PID=$!
sleep 5

# Get minio URLs from files
MINIO_URL=$(head -n1 minio_url.txt)
MINIO_UI_URL=$(sed -n '2p' minio_url.txt)

# Set-up MinIO client
mc alias set $MINIO_ALIAS "$MINIO_URL" $MINIO_USER $MINIO_PASSWORD

# Create buckets
mc mb --ignore-existing $MINIO_ALIAS/$RAW_BUCKET
mc mb --ignore-existing $MINIO_ALIAS/$STOCK_BUCKET

# Load each folder existing in $LOCAL_FOLDER_PATH
for folder in "$LOCAL_FOLDER_PATH"/*; do
  if [ -d "$folder" ]; then
    echo "Loading data from: $folder"
    mc cp --recursive "$folder" "$MINIO_ALIAS/$RAW_BUCKET/"
  fi
done

echo "All data uploaded to MinIO."

echo "Upload stats:"
mc du --recursive $MINIO_ALIAS/$RAW_BUCKET/
echo "Keep in mind that in MinIO UI you might see less objects than was actually loaded into S3."

# Open minio UI
echo "MinIO URLs"
echo "MinIO API: $MINIO_URL"
echo "MinIO UI: $MINIO_UI_URL"

# Stop tunel
rm -f minio_url.txt
kill $TUNNEL_PID