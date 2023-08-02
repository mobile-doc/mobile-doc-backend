from fastapi import APIRouter
from ..constants import VERSION_NAME, PROJECT_NAME

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
        "message": "Welcome to Mobile Docs Backend. Go to /docs for documentation",
    }
