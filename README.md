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
## Deploy FastApi, MinIO, Mongo & spark to kubernetes
1. **Change full deployment file mode**:
    
    ```
    chmode -x deploy_all.sh
    ```
2. **Perform full deployment**:
    
    ```
    ./deploy_all.sh
    ```
3. **Check if all 3 pods are running**
    
   a) App & Mongo
   ```
    kubectl get pods -n stock-etl-namespace
    ```
   b) Spark
   ```
    kubectl get pods -n spark-namespace
    ```
   c) Minio
    ```
    kubectl get pods -n minio-dev
    ```
* You can deploy each component separately following README.md in `deployment/README.md`

---
## Upload RawStockData to Minio
1. **Change full data loading file mode**:
    
    ```
    chmode -x load_raw_data_minio.sh
    ```
2. **Perform full deployment**:
    
    ```
    ./load_raw_data_minio.sh
    ```

---
## Running ETL API
1. **In order to run API you should first start the Kubernetes App**
    ```
    minikube service stock-etl-service -n stock-etl-namespace
    ```
2. **Open stock-etl-service (2nd url in terminal)**
3. **You should be able to see the Swagger UI with all available APIs**
4. **Find ETL api**
   ```
    api/run_stock_etl
    ```
5. **Select the input folder name or use default one:** `stocks_historical_to_2025_02_04`
6. **Click - execute**

* Keep in mind that running etl on historical data (20GB) might take more than 20 minutes

---
## Spark cluster check
1. **In order to get to Spark UI you MUST first forward the port via terminal**
   ```
    kubectl port-forward deployment/spark-master-deployment 8080:8080 -n spark-namespace
    ```
2. **Then just open the url in you web browser**
   ```
    127.0.0.1:8080
    ```
3. **In the UI you can check:**
   - Available workers & their resources
   - Running Apps
   - Completed runs

---
## Current Features & Future Plans

Currently, the application can:
- Check MongoDB server status.
- Read from and write data to S3 (MinIO) & Mongo DB.
- Use spark cluster in ETL process (read & write s3 data & perform transformations)

In the near future, **full API functionality** will be provided by adding report scrips: top_stocks, performance_compare.