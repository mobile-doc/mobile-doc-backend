from fastapi import APIRouter, UploadFile
from ..util import custom_logger
from google.cloud import storage
import os
import uuid

# os.environ[
#     "GOOGLE_APPLICATION_CREDENTIALS"
# ] = "/home/mmk/Downloads/mobile-doc-backend-analytics-sa.json"

router = APIRouter()

bucket_name = "storage_for_files"
client = storage.Client()


@router.post(
    "/upload_file",
    tags=["Upload_File"],
    summary="Uploads a file to GCP bucket",
)
async def upload_file(input_file: UploadFile, api_key_input: str):
    custom_logger.info("upload_file endpoint called")

    if api_key_input != "your_api_key_here":
        return {
            "success": False,
            "message": "API key is wrong",
        }

    if not input_file:
        return {
            "success": False,
            "message": "No file was uploaded",
        }

    file_name = input_file.filename

    destination_blob_name = str(uuid.uuid4()) + "_" + file_name

    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_file(input_file.file)

    custom_logger.info(
        f"File {file_name} uploaded to {bucket_name}/{destination_blob_name}"
    )
    public_url = blob.public_url

    return {
        "success": True,
        "message": "File uploaded successfully",
        "public_url": public_url,
    }
