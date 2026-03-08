from datetime import datetime
from uuid import uuid4
from uuid import UUID

from fastapi import HTTPException
from schemas import FileData, FileMetadata
from typing import Optional

class Repo:
    # The store is indexed by UUID (file ID) rather than SHA256 hash.
    # This follows standard database convention where a generated ID is the primary key.
    # As a consequence, uploading the same file multiple times will create duplicate entries,
    # each with a distinct ID but identical hash. Deduplication could be achieved by keying
    # on hash instead, but that would require the hash to act as the primary identifier,
    # which is not conventional and would make the API surface misleading.
    #
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
            raise HTTPException(400, f"Error when saving a file to the store: {str(e)}")

        return payload.to_metadata()

    def get_all(self) -> list[FileMetadata]:
        """Return metadata for all files in the store, without file content."""
        return [file.to_metadata() for file in self.store.values()]

    def _get_one(self, id: UUID) -> FileData:
        """Retrieve a single FileData by ID; raises 404 if not found."""
        try:
            return self.store[id]
        except KeyError:
            raise HTTPException(404, "File not found")

    def delete(self, id: UUID, hash: str) -> FileMetadata:
        """Delete a file by ID, verifying the provided hash matches before deletion.

        Both the file ID (path parameter) and SHA256 hash (query parameter) must be supplied.
        The hash acts as a secondary confirmation — it ensures the caller is certain they are
        deleting the intended file, guarding against accidental deletion by ID alone.
        """
        file = self._get_one(id)

        if file.hash != hash:
            raise HTTPException(400, "Provided hash does not match the file")

        del self.store[id]

        return file.to_metadata()
