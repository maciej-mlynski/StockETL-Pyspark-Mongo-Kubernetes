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

## Running the ETL API

1. **Start the Kubernetes application**:

   ```
   minikube service stock-etl-service -n stock-etl-namespace
   ```

2. **Open the second URL displayed in the terminal output.**

3. **Access the Swagger UI to explore available APIs.**

4. **Locate the ETL API endpoint**:

   ```
   api/run_stock_etl
   ```

5. **Specify the input folder name or use the default**: `stocks_historical_to_2025_02_04`

6. **Click "Execute" to start the ETL process.**

> ⚠️ Note: Running the ETL on historical data (~20 GB) may take more than 20 minutes.

---

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
- Execute the full ETL process using a Spark cluster (S3 input/output, MongoDB artifact storage)
- Select top-performing stocks within a given timeframe
- Health-check endpoint for MongoDB connectivity
- Retrieve ETL artifacts from MongoDB

**Additional functionality**:
- Debug Spark jobs using the integrated Spark History Server
- Makefile with handy commands for:
  - Pod status checks  
  - Deployment logs  
  - Redeploying apps/images  
  - Managing Kubernetes namespaces  
  - And more...

**Coming soon**:
- Jupyter Notebook integration within the Kubernetes cluster
- Autoscaling for the Spark cluster
- Spark Operator for job lifecycle management
- Apache Airflow for ETL pipeline scheduling and orchestration
