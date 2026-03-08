from fastapi import APIRouter, Depends, HTTPException, UploadFile
from schemas import FileMetadata
from store import Repo
import hashlib

router = APIRouter()

class FileUploadState:
    """Accumulates file content and computes its SHA256 hash incrementally as chunks are read."""

    def __init__(self):
        self.hash = hashlib.sha256()
        self.content = bytearray()

    def update(self, chunk: bytes):
        """Process a chunk of bytes, updating the hash and content buffer."""
        self.hash.update(chunk)
        self.content.extend(chunk)

    def hexdigest(self):
        """Return the final SHA256 hex string."""
        return self.hash.hexdigest()

    def get_content_bytes(self) -> bytes:
        """Return the accumulated file content as bytes."""
        return bytes(self.content)

# Chunk size in bytes
CHUNK_SIZE = 4 * 1024

@router.post("/upload", response_model=FileMetadata, status_code=201)
async def upload_file(
    file: UploadFile,
    state: FileUploadState = Depends(),
    repo: Repo = Depends()
):
    """Accept a file upload, compute its SHA256 hash, and store it in memory.

    The file is read in chunks to avoid loading it entirely into memory before hashing.
    Returns the file metadata (id, hash, uploaded_at) on success.
    """
    try:
        while chunk := await file.read(CHUNK_SIZE):
            state.update(chunk)
    except Exception as e: 
        raise HTTPException(400, f"encountered error while reading the file: {str(e)}")
    
    entry = repo.save(file.filename or "unknown", state.hexdigest(), state.get_content_bytes())
    return entry

