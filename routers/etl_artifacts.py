from db.etl_artifacts import ETLArtifacts
from fastapi import APIRouter, HTTPException
from bson import json_util
import json

router = APIRouter()

@router.get("/get_etl_artifacts_by_run_id")
async def get_etl_artifacts_by_run_id(run_id: int):

    try:
        # Init ETLArtifacts
        etl_app = ETLArtifacts()

        # Run ETL script
        etl_artifacts = etl_app.get_artifacts_by_run_id(run_id)
        if etl_artifacts:
            return json.loads(json_util.dumps(etl_artifacts))
        return [{"Error": f"No run_id: {run_id} found"}]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
