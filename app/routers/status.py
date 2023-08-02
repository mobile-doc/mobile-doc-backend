from fastapi import APIRouter
from ..constants import VERSION_NAME, PROJECT_NAME, SHORT_SHA, BRANCH_NAME, REPO_NAME

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
        "SHORT_SHA": SHORT_SHA,
        "BRANCH_NAME": BRANCH_NAME,
        "REPO_NAME": REPO_NAME,
        "message": "Welcome to Mobile Docs Backend. Go to /docs for documentation",
    }
