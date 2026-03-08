from fastapi import APIRouter, Depends
from schemas import FileMetadata
from store import Repo

router = APIRouter()

@router.get("/files", response_model=list[FileMetadata])
async def get_files(repo: Repo = Depends()):
    """Return metadata for all uploaded files."""
    files = repo.get_all()
    return files
