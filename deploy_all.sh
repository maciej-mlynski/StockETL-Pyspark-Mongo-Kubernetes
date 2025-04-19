
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
chmod +x deployment/deploy_spark_cluster.sh
./deployment/deploy_spark_cluster.sh

echo
echo "Deploying Mongo db..."
chmod +x deployment/deploy_mongo.sh
./deployment/deploy_mongo.sh

echo
echo "Deploying Fast API app..."
chmod +x deployment/deploy_api.sh
./deployment/deploy_api.sh

echo
echo "Deploying Spark Operator for ETL..."
chmod +x deployment/deploy_etl_spark_operator.sh
./deployment/deploy_etl_spark_operator.sh

echo
echo "Deploying Airflow for ETL..."
chmod +x deployment/deploy_etl_airflow.sh
./deployment/deploy_etl_airflow.sh