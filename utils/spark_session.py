import os
from pyspark.sql import SparkSession

class Builder:
    def __init__(self, app_name):
        self.app_name = app_name

    def get_spark_session(self):
        minio_host = os.environ["MINIO_HOST"]
        minio_port = os.environ["MINIO_PORT"]
        s3_endpoint = f"http://{minio_host}:{minio_port}"
        spark = (
            SparkSession.builder
            .appName(self.app_name)
            .master(os.environ["SPARK_MASTER_URL"])
            .config("spark.driver.host", os.environ["SPARK_DRIVER_HOST"])
            .master("spark://spark-master-svc.spark-namespace.svc.cluster.local:7077")
            .config("spark.driver.memory", os.environ["SPARK_DRIVER_MEMORY"])
            .config("spark.executor.memory", os.environ["SPARK_EXECUTOR_MEMORY"])
            .config("spark.executor.cores", os.environ["SPARK_TOTAL_EXECUTOR_CORES"])
            .config("spark.cores.max", os.environ["SPARK_MAX_EXECUTOR_CORES"])
            .config("spark.jars.packages",
                    "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.12.375")
            .config("spark.dynamicAllocation.enabled", "false")
            .config("spark.hadoop.fs.s3a.endpoint", s3_endpoint)
            .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"])
            .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"])
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .config("spark.eventLog.enabled", "true")
            .config("spark.eventLog.dir", os.environ["SPARK_EVENTLOG_DIR"])
            .config("spark.history.fs.logDirectory", os.environ["SPARK_EVENTLOG_DIR"])
            .getOrCreate())

        return spark