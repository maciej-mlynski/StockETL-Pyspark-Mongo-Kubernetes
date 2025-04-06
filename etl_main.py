from pyspark.sql import SparkSession
from ETL.stock_etl import StockETL
import sys
import os

input_folder = sys.argv[7]
minio_host = os.environ["MINIO_HOST"]
minio_port = os.environ["MINIO_PORT"]
s3_endpoint = f"http://{minio_host}:{minio_port}"

spark = (
    SparkSession.builder
    .appName("StockETLJob")
    .config("spark.jars.packages",
            "org.apache.hadoop:hadoop-aws:3.3.2,com.amazonaws:aws-java-sdk-bundle:1.12.375")
    .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem")
    .config("spark.hadoop.fs.s3a.endpoint", s3_endpoint)
    .config("spark.hadoop.fs.s3a.access.key", os.environ["MINIO_ACCESS_KEY"])
    .config("spark.hadoop.fs.s3a.secret.key", os.environ["MINIO_SECRET_KEY"])
    .config("spark.hadoop.fs.s3a.path.style.access", "true")
    .config("spark.jars.ivy", "/tmp/.ivy2")
    .config("spark.local.dir", "/tmp/spark")
    .getOrCreate()
)

etl_job = StockETL(spark, input_folder)
result = etl_job.run_etl()
print("ETL process completed. Result:", result)

spark.stop()
