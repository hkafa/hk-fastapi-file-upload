from datetime import datetime
from pydantic import BaseModel
from uuid import UUID


class FileMetadata(BaseModel):
    id: UUID
    hash: str
    uploaded_at: datetime


class FileData(BaseModel):
    id: UUID
    hash: str
    content: bytes
    uploaded_at: datetime

    def to_metadata(self) -> FileMetadata:
        return FileMetadata(id=self.id, hash=self.hash, uploaded_at=self.uploaded_at)
