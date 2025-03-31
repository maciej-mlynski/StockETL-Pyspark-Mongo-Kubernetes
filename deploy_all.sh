
# Deploy max cores, max cpu minikube
# Info: You can set-up max resources in DockerDesktop
echo "Staring minikube with max available resources..."
minikube start --memory=max --cpus=max

echo
echo "Deploying Minio..."
chmod +x deployment/deploy_minio.sh
./deployment/deploy_minio.sh

echo
echo "Deploying Spark cluster..."
chmod +x deployment/deploy_spark.sh
./deployment/deploy_spark.sh

echo
echo "Deploying Fast API with mongo"
chmod +x deployment/deploy_app.sh
./deployment/deploy_app.sh