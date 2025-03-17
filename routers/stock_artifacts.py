from db.stock_data_artifacts import StockDataArtifacts
from fastapi import APIRouter, HTTPException
from bson import json_util
import json

router = APIRouter()

@router.get("/get_stock_artifacts_by_ticker_name")
async def get_stock_artifacts_by_ticker_name(ticker_name: str):

    try:
        # Init StockDataArtifacts
        etl_app = StockDataArtifacts()

        # Run ETL script
        etl_artifacts = etl_app.get_stock_artifacts_by_ticker_name(ticker_name)
        if etl_artifacts:
            return json.loads(json_util.dumps(etl_artifacts))
        return [{"Error": f"No ticker: {ticker_name} found"}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
