from pyspark.sql import SparkSession
from reports.performance_compare import PerformanceCheck
from fastapi import APIRouter, HTTPException

router = APIRouter()

@router.get("/compare_performance_between_raw_and_transformed_data")
async def compare_performance_between_raw_and_transformed_data():

    try:
        # Init spark Session & Spark context
        spark = SparkSession.builder.master("local[*]").appName("ETL").getOrCreate()

        # Run ETL script
        performance_app = PerformanceCheck(spark)
        results = performance_app.compare()

        # Stop the Spark session after processing.
        spark.stop()
        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
