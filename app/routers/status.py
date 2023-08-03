from fastapi import APIRouter
from ..constants import (
    VERSION_NAME,
    PROJECT_NAME,
    GOOGLE_CLOUD_PROJECT,
    GAE_VERSION,
    GAE_MEMORY_MB,
)

router = APIRouter()


@router.get(
    "/",
    tags=["General"],
)
async def root():
    return {
        "success": True,
        "project_name": PROJECT_NAME,
        "version_name": VERSION_NAME,
        "GOOGLE_CLOUD_PROJECT": GOOGLE_CLOUD_PROJECT,
        "GAE_VERSION": GAE_VERSION,
        "GAE_MEMORY_MB": GAE_MEMORY_MB,
        "message": "Welcome to Mobile Docs Backend. Go to /docs for documentation",
    }
