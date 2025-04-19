from db.airflow_artefacts import AirflowArtifacts
from fastapi import APIRouter, HTTPException
from fastapi import Body
from typing import List
from bson import json_util
import json

router = APIRouter()

# Init AirflowArtifacts
airflow_app = AirflowArtifacts()

@router.get("/get_airflow_artifacts_collection")
async def get_airflow_artifacts_collection():
    try:
        # Run ETL script
        airflow_response = airflow_app.get_airflow_etl_artifacts()
        return json.loads(json_util.dumps(airflow_response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/add_skip_date_to_airflow")
async def add_skip_date_to_airflow(skip_dates: List[str] = Body(..., example=["2025-02-05", "2025-02-07"])):
    try:
        # Run ETL script
        airflow_response = airflow_app.add_skip_date(skip_dates)
        return json.loads(json_util.dumps(airflow_response))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/remove_skip_date_from_airflow", summary="Remove date(s) from skip_dates")
async def remove_skip_date_from_airflow(skip_dates: List[str] = Body(...,example=["2025-02-05"])):

    try:
        result = airflow_app.remove_skip_date(skip_dates)
        return json.loads(json_util.dumps(result))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
