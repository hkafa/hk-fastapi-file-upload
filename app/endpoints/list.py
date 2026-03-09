from fastapi import APIRouter, Depends
from schemas import FileMetadata
from store import Repo
from logs import get_logger

router = APIRouter()
log = get_logger()

@router.get("/files", response_model=list[FileMetadata])
async def get_files(repo: Repo = Depends()):
    """Return metadata for all uploaded files."""
    log.info("Listing all files in the store")
    files = repo.get_all()
    return files
