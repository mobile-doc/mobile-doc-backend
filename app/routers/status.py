from fastapi import APIRouter
from ..constants import *

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
