# Project Installation & Deployment

Below are the steps required to run this application, which consists of:
- A **MinIO** instance for storing raw data (S3-compatible object storage).
- A **MongoDB** instance for database storage.
- A **FastAPI** application that interacts with both MongoDB and MinIO.

---

## Prerequisites

1. **Minikube**  
   Install following the official guide:  
   [https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fhomebrew](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fhomebrew)

2. **Docker**  
   [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

3. **mc (MinIO Client)** for manual data uploads

    Install via Homebrew (on macOS):
    
    ```
    brew install minio/stable/mc
    ```

---

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

8. **Create another bucket**:
    
    ```
    mc mb myminio/stockdata
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

4. **Check the FastAPI logs**:
    
    ```
    kubectl logs deployment/stock-etl-deployment -n stock-etl-namespace
    ```

5. **Access the FastAPI service via Minikube**:
    
    ```
    minikube service stock-etl-service -n stock-etl-namespace
    ```

---

## Current Features & Future Plans

Currently, the application can:
- Check MongoDB server status.
- Read from and write data to S3 (MinIO).

In the near future, **full API functionality** will be provided by adding a Spark Operator on Kubernetes, enabling advanced data processing features.
