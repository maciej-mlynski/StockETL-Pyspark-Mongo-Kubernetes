# Deploying each component separately


## Deploying MinIO

1. **Start Minikube**:
    
    ```
    minikube start
    ```

2. **Make the MinIO deploy script executable**:
    
    ```
    chmod +x deploy_minio.sh
    ```

3. **Deploy MinIO**:
    
    ```
    ./deploy_minio.sh
    ```

4. **Access MinIO**:
    
    ```
    minikube service minio-service -n minio-dev
    ```

5. **Configure MinIO Client (`mc`)**:

   For example:
   
    ```
    mc alias set myminio <TARGET_PORT_URL> <USER_NAME> <PASSWORD>
    ```
    
   Where `TARGET_PORT_URL` is the port that Minikube shows after running `minikube service`.
   Unless you change anything your credentials are username: minio, password: minio123


6. **Create a bucket**:
    
    ```
    mc mb myminio/rawstockdata
    ```

7. **Upload data**:
    
    ```
    mc cp --recursive <LOCAL_FOLDER_PATH> myminio/rawstockdata
    ```

8. **Create another bucket for ETL output**:
    
    ```
    mc mb myminio/stockdata
    ```

---
## Deploying Spark cluster
1. **Start (or ensure Minikube is running)**:
    
    ```
    minikube start
    ```
2. **Make the spark deploy script executable**:
    
    ```
    chmod +x deploy_spark.sh
    ```

3. **Deploy the spark cluster**:
    
    ```
    ./deploy_spark.sh
    ```

---
## Deploying the FastAPI App (with Mongo)

1. **Start (or ensure Minikube is running)**:
    
    ```
    minikube start
    ```

2. **Make the app deploy script executable**:
    
    ```
    chmod +x deploy_app.sh
    ```

3. **Deploy the app**:
    
    ```
    ./deploy_app.sh
    ```

4. **Access the FastAPI service via Minikube**:
    
    ```
    minikube service stock-etl-service -n stock-etl-namespace
    ```
5. **Check the FastAPI logs while running app**:
    
    ```
    kubectl logs deployment/stock-etl-deployment -n stock-etl-namespace
    ```

---