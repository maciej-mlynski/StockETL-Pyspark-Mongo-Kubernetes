from utils.spark_session import Builder
from ETL.stock_etl import StockETL
from fastapi import APIRouter, HTTPException


router = APIRouter()


@router.put("/run_stock_etl")
async def run_stock_etl(input_folder_path: str='stocks_2025_02_05'):

    try:
        # Build spark session
        spark = Builder('StockETL').get_spark_session()

        # Run ETL script
        etl_app = StockETL(spark, input_folder_path)
        api_artifacts = etl_app.run_etl()

        return api_artifacts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


