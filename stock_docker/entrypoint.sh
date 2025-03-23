#!/bin/bash

# Get the workload parameter passed to the container
SPARK_WORKLOAD=$1
echo "SPARK_WORKLOAD: $SPARK_WORKLOAD"

if [ "$SPARK_WORKLOAD" == "master" ]; then
    echo "Starting Spark Master..."
    start-master.sh -p 7077
elif [ "$SPARK_WORKLOAD" == "worker" ]; then
    echo "Starting Spark Worker..."
    start-worker.sh spark://spark-master:7077
elif [ "$SPARK_WORKLOAD" == "history" ]; then
    echo "Starting Spark History Server..."
    start-history-server.sh
elif [ "$SPARK_WORKLOAD" == "app" ]; then
    echo "Starting FastAPI Application..."
    uvicorn main:app --host 0.0.0.0 --port 8000
else
    echo "Invalid workload argument. Exiting."
    exit 1
fi
