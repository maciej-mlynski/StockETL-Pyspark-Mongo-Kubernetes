# Project Installation & Deployment

This guide outlines the steps required to run the application, which consists of:
- A **MinIO** instance for storing raw data (S3-compatible object storage).
- A **MongoDB** instance for database storage.
- A **FastAPI** application that interacts with both MongoDB and MinIO.
- A **Spark** transformation engine with a log server.

---

## Prerequisites

1. **Minikube**  
   Install Minikube following the official guide:  
   [https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fhomebrew](https://minikube.sigs.k8s.io/docs/start/?arch=%2Fmacos%2Farm64%2Fstable%2Fhomebrew)

2. **Docker**  
   Download and install Docker Desktop:  
   [https://www.docker.com/products/docker-desktop/](https://www.docker.com/products/docker-desktop/)

3. **mc (MinIO Client)** for uploading data  

   Install via Homebrew (on macOS):

   ```
   brew install minio/stable/mc
   ```

4. **Helm** for spark-operator 

   Install via Homebrew (on macOS):

   ```
   brew install helm
   ```

---

## Set Up MinIO Credentials

1. **Generate base64-encoded username and password**:

   ```
   echo -n '<USER_NAME>' | base64
   echo -n '<PASSWORD>' | base64
   ```

   Example:

   ```
   echo -n 'minio' | base64
   echo -n 'minio321' | base64
   ```

2. **Open the secret configuration file**:

   ```
   minikube/minio/minio-secret.yaml
   ```

3. **Paste the encoded credentials**:

   ```
   minio-access-key: <ENCODED_USERNAME>
   minio-secret-key: <ENCODED_PASSWORD>
   ```

> These credentials will allow you to **log in to the MinIO UI**. The application will automatically use them to read and write data to S3.

---

## Deploy FastAPI, MinIO, MongoDB & Spark to Kubernetes

1. **Make the deployment script executable**:

   ```
   chmode -x deploy_all.sh
   ```

2. **Run the full deployment (Docker & Kubernetes)**:

   ```
   ./deploy_all.sh
   ```

3. **Verify pods**:

   a) FastAPI, MongoDB, Spark History:

   ```
   kubectl get pods -n stock-etl-namespace / make check-app
   ```

   b) Spark:

   ```
   kubectl get pods -n spark-namespace
   ```

   c) MinIO:

   ```
   kubectl get pods -n minio-dev
   ```

> You can also deploy each component individually by following the instructions in `deployment/README.md`.

---

## Upload Raw Stock Data to MinIO

1. **Make the data upload script executable**:

   ```
   chmode -x load_raw_data_minio.sh
   ```

2. **Run the data upload**:

   ```
   ./load_raw_data_minio.sh
   ```

3. **Access the MinIO UI**:

   ```
   minikube service minio-service -n minio-dev
   ```

---

## Running Stock ETL with spark-operator

1. **Before you run ETL you should make sure that raw stock data is already in S3**:
    ```
    minikube service minio-service -n minio-dev
    ```
2. **Change the input_folder_name in `minikube/etl/spark-etl-job.yaml`**:

   - By default, the argument is set to `stocks_historical_to_2025_02_04`
   - You should run this process 4 times in order to process each input folder separately
   - The next file you should run on is `stocks_2025_02_05`, etc.

3. **In order to run ETL with spark operator you should apply manifest by**:
   ```
   kubectl apply -f minikube/etl/spark-etl-job.yaml -n spark-jobs
    ```

4. **In order to see the pods run**:
   ```
   kubectl get pods -n spark-jobs
    ```
5. **In order to see ETL logs/results you can run**:
   ```
   kubectl logs spark-stock-etl-driver -n spark-jobs -f
   kubectl describe sparkapplication spark-stock-etl -n spark-jobs
   ```

---
## Running the APIs

1. **Start the Kubernetes application**:

   ```
   minikube service stock-etl-service -n stock-etl-namespace
   ```

2. **Open the second URL displayed in the terminal output.**

3. **Access the Swagger UI to explore available APIs.**
   
### Mongo
1. check_mongo_sever
2. get_etl_artifacts_by_run_id
3. get_stock_artifacts_by_ticker_name

> This APIs can help you validate the ETL results

### Reports
1. get_top_stocks
   
> This API work on spark cluster, and it can present top profit stocks for you extremely fast!


## Checking the Spark Cluster

1. **Forward the Spark UI port in your terminal**:

   ```
   kubectl port-forward deployment/spark-master-deployment 8080:8080 -n spark-namespace
   ```

2. **Open the following URL in your web browser**:

   ```
   127.0.0.1:8080
   ```

3. **In the Spark UI, you can monitor**:
   - Available workers and their resources
   - Active applications
   - Completed job runs

Keep in mind that if you didn't run get_top_stocks API you may not see anything there

---

## Viewing Spark Logs

1. **Start the Spark History Server**:

   ```
   minikube service spark-history-service -n stock-etl-namespace
   ```

2. **A browser window should open with the Spark History Server UI.**  
   If not, copy the URL displayed in the terminal and open it manually.

3. **In the Spark History UI, you can**:
   - View a list of completed Spark applications
   - Check each run’s App ID, name, user, duration, and submission time
   - Click on any App ID to:
     - Inspect stages, tasks, and jobs
     - Review execution timelines, performance metrics, and job summaries
     - Visualize DAGs (Directed Acyclic Graphs) for stage dependencies
     - Download event logs for debugging or tuning

---

## Current Features & Future Plans

**Currently available via API**:
- Select top-performing stocks within a given timeframe
- Health-check endpoint for MongoDB connectivity
- Retrieve ETL artifacts from MongoDB

**Spark operator on k8s**:
- ETL process is now triggerd by applying SparkApplication manifest
- It executes full ETL process using a Spark operator (S3 input/output, MongoDB artifact storage)

**Additional functionality**:
- Debug Spark jobs using the integrated Spark History Server
- Makefile with handy commands for:
  - Pod status checks  
  - Deployment logs  
  - Redeploying apps/images  
  - Managing Kubernetes namespaces  
  - And more...

**Coming soon**:
- Apache Airflow implementation to automate ETL process (Any new file is uploaded to `rawstockdata` in S3 -> ETL will be triggered)
- Spark history for spark-operator
- Jupyter Notebook integration within the Kubernetes cluster
- Autoscaling for the Spark cluster
- Spark Operator for job lifecycle management
- Apache Airflow for ETL pipeline scheduling and orchestration
