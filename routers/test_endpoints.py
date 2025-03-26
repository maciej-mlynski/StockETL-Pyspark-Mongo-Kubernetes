from fastapi import APIRouter, HTTPException
from minio import Minio
from minio.error import S3Error
import io

router = APIRouter()

minio_client = Minio(
            endpoint='minio-service.minio-dev.svc.cluster.local:6544',
            access_key="minio",
            secret_key="minio123",
            secure=False
        )

@router.get("/read_csv/")
def read_csv(file_path: str):

    try:
        response = minio_client.get_object(bucket_name="rawstockdata", object_name=file_path)
    except S3Error as e:
        raise HTTPException(status_code=404, detail=f"File not found: {e}")

    try:
        content = response.read().decode("utf-8")
        response.close()
        response.release_conn()
        return {"file_path": file_path, "content": content}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/write_dummy_csv/")
def write_dummy_csv(bucket_name:str = 'stockdata'):
    try:
        dummy_csv_content = "col1,col2,col3\n1,2,3\n4,5,6\n"
        dummy_data = io.BytesIO(dummy_csv_content.encode("utf-8"))

        object_name = "dummy_data.csv"
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=dummy_data,
            length=len(dummy_csv_content),
            content_type="text/csv"
        )

        return {"message": "File uploaded", "object_name": object_name}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=str(e))