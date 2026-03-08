from datetime import datetime
from typing import Optional
from pydantic import BaseModel
from uuid import UUID


class FileMetadata(BaseModel):
    id: UUID
    filename: Optional[str]
    hash: str
    uploaded_at: datetime


class FileData(BaseModel):
    id: UUID
    filename: Optional[str]
    hash: str
    content: bytes
    uploaded_at: datetime

    def to_metadata(self) -> FileMetadata:
        return FileMetadata(id=self.id, filename=self.filename, hash=self.hash, uploaded_at=self.uploaded_at)
