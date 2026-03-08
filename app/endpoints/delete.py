from typing import Annotated
from uuid import UUID
from fastapi import APIRouter, Depends, Query
from schemas import FileMetadata
from store import Repo

router = APIRouter()


@router.delete("/files/{id}", response_model=FileMetadata)
async def delete_file(
    id: UUID,
    hash: Annotated[str, Query()],
    repo: Repo = Depends()
):
    """Delete a file by its ID, with the SHA256 hash required as a secondary confirmation.

    Both parameters must correspond to the same stored file. Returns the metadata of the
    deleted file on success, or 404 if the file is not found.
    """
    file = repo.delete(id, hash)
    return file
