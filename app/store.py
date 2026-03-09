from datetime import datetime
from uuid import uuid4
from uuid import UUID
from fastapi import HTTPException
from logs import get_logger
from schemas import FileData, FileMetadata
from typing import Optional

log = get_logger()

class Repo:
    # The store is a class-level variable so that all Repo instances injected per request
    # share the same in-memory state for the lifetime of the application.
    store: dict[UUID, FileData] = {}

    @staticmethod
    def _create_payload(filename: Optional[str], hash: str, content: bytes) -> FileData:
        """Create a FileData object with a new UUID, filename, hash, content bytes, and current datetime."""
        return FileData(
            id=uuid4(),
            filename=filename,
            hash=hash,
            content=content,
            uploaded_at=datetime.now()
        )

    def save(self, filename: Optional[str], hash: str, content: bytes) -> FileMetadata:
        """Save a file with given filename, hash and content into the store; returns the saved FileMetadata."""
        payload = self._create_payload(filename, hash, content)

        try:
            self.store[payload.id] = payload
        except Exception as e:
            message = f"Error when saving a file to the store: {str(e)}" 
            log.exception(message)
            raise HTTPException(status_code=400, detail=message)

        return payload.to_metadata()

    def get_all(self) -> list[FileMetadata]:
        """Return metadata for all files in the store, without file content."""
        return [file.to_metadata() for file in self.store.values()]

    def _get_one(self, id: UUID) -> FileData:
        """Retrieve a single FileData by ID; raises 404 if not found."""
        try:
            return self.store[id]
        except KeyError:
            message = "File not found"
            log.error(message)
            raise HTTPException(status_code=404, detail=message)

    def delete(self, id: UUID, hash: str) -> FileMetadata:
        """Delete a file by ID, verifying the provided hash matches before deletion."""
        file = self._get_one(id)

        if file.hash != hash:
            message = "Provided hash does not match the file"
            log.error(message)
            raise HTTPException(status_code=400, detail=message)

        del self.store[id]

        return file.to_metadata()
