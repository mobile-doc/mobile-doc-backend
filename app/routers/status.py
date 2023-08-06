from fastapi import APIRouter
from ..constants import (
    VERSION_NAME,
    PROJECT_NAME,
    GOOGLE_CLOUD_PROJECT,
    SHORT_SHA,
    TAG_NAME,
)

router = APIRouter()


@router.get(
    "/",
    tags=["General"],
)
async def root():
    return {
        "success": True,
        "message": "Welcome to Mobile Docs Backend. Go to /docs for documentation",
    }


@router.get(
    "/status",
    tags=["General"],
)
async def status():
    return {
        "success": True,
        "project_name": PROJECT_NAME,
        "version_name": VERSION_NAME,
        "GOOGLE_CLOUD_PROJECT": GOOGLE_CLOUD_PROJECT,
        "SHORT_SHA": SHORT_SHA,
        "TAG_NAME": TAG_NAME,
    }
