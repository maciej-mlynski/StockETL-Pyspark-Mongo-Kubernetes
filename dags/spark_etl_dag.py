from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from minio import Minio
from pymongo import MongoClient
from utils import FolderSelector
from spark_sensor import SparkApplicationSensor
import os
from datetime import datetime, timedelta

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'retries': 0,
}

with DAG(
    'spark_etl_dag',
    default_args=default_args,
    schedule_interval=timedelta(seconds=30),
    start_date=datetime(2023, 1, 1),
    catchup=False,
    max_active_runs=1
) as dag:

    def find_new_folder(ti):
        try:
            minio_client = Minio(
                os.environ['MINIO_ENDPOINT'].replace("http://", ""),
                access_key=os.environ['AWS_ACCESS_KEY_ID'],
                secret_key=os.environ['AWS_SECRET_ACCESS_KEY'],
                secure=False
            )
        except Exception as e:
            raise Exception(f"Could not connect to Minio. Error: {e}")
        bucket = "rawstockdata"
        objects = minio_client.list_objects(bucket, recursive=True)
        folders = set([obj.object_name.split('/')[0] for obj in objects])

        try:
            mongo_client = MongoClient(os.environ['MONGO_URI'])
        except Exception as e:
            raise Exception(f"Could not connect to Mongo. Error: {e}")

        collection = mongo_client["StockDB"]["AirflowETLArtifacts"]
        record = collection.find_one({"_id":"processed_folders"}) or {"folders": [], "skip_dates": [], "run_id": 0}
        processed = record.get("folders", [])
        skip_dates = record.get("skip_dates", [])

        # Select folder
        folder = FolderSelector.select_folder(
            new_folders=list(folders),
            processed_folders=processed,
            skip_dates=skip_dates
        )

        # Push folder name
        ti.xcom_push(key="folder_to_process", value=folder)

        # Get run id
        run_id = record.get("run_id", 0)
        ti.xcom_push(key="run_id", value=run_id)

    find_folder = PythonOperator(
        task_id="find_new_folder",
        python_callable=find_new_folder
    )

    prepare_spark_yaml = BashOperator(
        task_id="prepare_spark_yaml",
        bash_command="""
            sed -e 's/__INPUT_FOLDER__/{{ ti.xcom_pull("find_new_folder", key="folder_to_process") }}/g' \
                -e 's/__RUN_ID__/{{ ti.xcom_pull("find_new_folder", key="run_id") }}/g' \
                ${AIRFLOW_HOME}/dags/spark-etl-job-template.yaml > /tmp/spark_job.yaml
        """
    )

    submit_job = BashOperator(
        task_id="submit_spark_job",
        bash_command="kubectl apply -f /tmp/spark_job.yaml -n spark-jobs"
    )

    # Wait until spark job is completed
    wait_for_spark = SparkApplicationSensor(
        task_id="wait_for_spark_job",
        application_name=(
            "spark-stock-etl-"
            "{{ ti.xcom_pull('find_new_folder', key='run_id') }}"
        ),
        namespace="spark-jobs",
    )

    def update_mongo_state(ti):
        client = MongoClient(os.environ['MONGO_URI'])
        coll = client["StockDB"]["AirflowETLArtifacts"]
        folder = ti.xcom_pull(task_ids="find_new_folder", key="folder_to_process")
        # $addToSet + $inc
        coll.update_one(
            {"_id": "processed_folders"},
            {
                "$addToSet": {"folders": folder},
                "$inc": {"run_id": 1}
            },
            upsert=True
        )

    update_mongo = PythonOperator(
        task_id="update_mongo",
        python_callable=update_mongo_state
    )

    find_folder >> prepare_spark_yaml >> submit_job >> wait_for_spark >> update_mongo
