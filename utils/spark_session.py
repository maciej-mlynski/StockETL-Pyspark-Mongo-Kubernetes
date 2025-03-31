import os
from pyspark.sql import SparkSession

class Builder:
    def __init__(self, app_name, driver_memory="1g", executor_memory="8g", executor_cores="3", spark_cores_max="3"):
        self.app_name = app_name
        self.driver_memory = driver_memory
        self.executor_memory = executor_memory
        self.executor_cores = executor_cores
        self.spark_cores_max = spark_cores_max

    def get_spark_session(self):
        spark_master_url = os.environ.get("SPARK_MASTER_URL", "local[*]")
        spark_driver_host = os.environ.get("SPARK_DRIVER_HOST", "127.0.0.1")
        minio_host = os.environ.get("MINIO_HOST", "minio-service.minio-dev.svc.cluster.local")
        minio_port = os.environ.get("MINIO_PORT", "6544")
        minio_access_key = os.environ.get("MINIO_ACCESS_KEY", "minio")
        minio_secret_key = os.environ.get("MINIO_SECRET_KEY", "minio123")
        s3_endpoint = f"http://{minio_host}:{minio_port}"
        spark = (
            SparkSession.builder
            .appName(self.app_name)
            .master(spark_master_url)
            .config("spark.driver.host", spark_driver_host)
            .master("spark://spark-master-svc.spark-namespace.svc.cluster.local:7077")
            .config("spark.driver.memory", self.driver_memory)
            .config("spark.executor.memory", self.executor_memory)
            .config("spark.executor.cores", self.executor_cores)
            .config("spark.cores.max", self.spark_cores_max)
            .config("spark.jars.packages",
                    "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.12.375")
            .config("spark.dynamicAllocation.enabled", "false")
            .config("spark.hadoop.fs.s3a.endpoint", s3_endpoint)
            .config("spark.hadoop.fs.s3a.access.key", minio_access_key)
            .config("spark.hadoop.fs.s3a.secret.key", minio_secret_key)
            .config("spark.hadoop.fs.s3a.path.style.access", "true")
            .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
            .getOrCreate())

        return spark