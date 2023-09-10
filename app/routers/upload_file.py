from fastapi import APIRouter, UploadFile, Depends, HTTPException
from typing import Optional
from ..util import custom_logger, AuthHandler
from google.cloud import storage
import os
import uuid

# os.environ[
#     "GOOGLE_APPLICATION_CREDENTIALS"
# ] = "/home/mmk/Downloads/mobile-doc-backend-analytics-sa.json"

router = APIRouter()
auth_handler = AuthHandler()

bucket_name = "storage_for_files"
client = storage.Client()


@router.post(
    "/upload_file",
    tags=["Upload_File"],
    summary="Uploads a file to GCP bucket (for user)",
)
async def upload_file_by_user(
    input_file: UploadFile,
    auth_id: str = Depends(auth_handler.auth_wrapper),
):
    custom_logger.info(f"upload_file endpoint called, auth_id: {auth_id}")

    if auth_id is None:
        HTTPException(status_code=401, detail="Unauthorized")

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


@router.post(
    "/upload_file_with_key",
    tags=["Upload_File"],
    summary="Uploads a file to GCP bucket (for Diagnostic Center)))",
)
async def upload_file(
    input_file: UploadFile,
    api_key_input: str = None,
):
    custom_logger.info(f"upload_file endpoint called, api_key: {api_key_input}")

    if api_key_input != "your_api_key_here":
        HTTPException(status_code=401, detail="Unauthorized")

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
