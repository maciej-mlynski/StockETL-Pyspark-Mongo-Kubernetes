from pyspark.sql import SparkSession
from ETL.stock_etl import StockETL
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()

class ETLParams(BaseModel):
    input_folder_path: str


@router.put("/run_stock_etl")
async def run_stock_etl(params: ETLParams):

    try:
        # Init spark Session & Spark context
        spark = SparkSession.builder.master("local[*]").appName("ETL").getOrCreate()

        # Run ETL script
        etl_app = StockETL(spark, params.input_folder_path)
        api_artifacts = etl_app.run_etl()

        # Stop the Spark session after processing.
        spark.stop()
        return api_artifacts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
