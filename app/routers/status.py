from fastapi import APIRouter
from ..constants import VERSION_NAME, PROJECT_NAME, GOOGLE_CLOUD_PROJECT
from ..constants import atlas_username, atlas_password

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
        "atlas_username": atlas_username,
        "atlas_password": atlas_password,
    }
