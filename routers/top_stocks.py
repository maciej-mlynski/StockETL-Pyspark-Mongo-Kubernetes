from utils.spark_session import Builder
from reports.top_stocks import TopStocksApp
from fastapi import APIRouter, HTTPException
from datetime import date, time
from typing import Optional
from enum import Enum
import json


router = APIRouter()

class TimeFrame(str, Enum):
    SingleDay = "SingleDay"           # Only the selected day
    PastWeek = "PastWeek"         # 7-day period ending with target date
    PastMonth = "PastMonth"       # One-month period ending with target date
    YearToDate = "YearToDate"    # From January 1st of target year to target date
    PastYear = "PastYear"         # One-year period ending with target date
    HistoricalToDate = "HistoricalToDate"  # From inception to target date


@router.get("/get_top_stocks")
async def get_top_stocks(time_frame: TimeFrame, target_date: date = '2020-01-01', optional_time: Optional[time] = None, num_of_stocks_to_display: Optional[int] = None):

    try:
        # Build spark session
        spark = Builder('TopStocks').get_spark_session()

        # Run ETL script
        top_stocks_app = TopStocksApp(spark)
        top_stocks = top_stocks_app.find_top_n_profit_stocks(target_date, optional_time, time_frame.value, num_of_stocks_to_display)

        # Convert DataFrame to an RDD of JSON strings, then collect it.
        json_str_list = top_stocks.toJSON().collect()

        # Optionally, convert JSON strings to dictionaries:
        json_result = [json.loads(x) for x in json_str_list]

        # Stop the Spark session after processing.
        spark.stop()

        return json_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))