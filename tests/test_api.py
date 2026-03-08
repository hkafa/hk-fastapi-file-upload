import sys
import os
import hashlib

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

import pytest
from fastapi.testclient import TestClient
from main import app
from store import Repo
from endpoints.upload import FileUploadState
from schemas import FileData, FileMetadata
from uuid import uuid4
from datetime import datetime

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_store():
    Repo.store.clear()


# --- Endpoint tests ---

def test_upload_returns_metadata():
    response = client.post("/upload", files={"file": b"Hello, World!"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "hash" in data
    assert "uploaded_at" in data
    assert "content" not in data


def test_list_returns_all_files():
    client.post("/upload", files={"file": b"file one"})
    client.post("/upload", files={"file": b"file two"})
    response = client.get("/files")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_does_not_return_content():
    client.post("/upload", files={"file": b"Hello, World!"})
    files = client.get("/files").json()
    assert "content" not in files[0]


def test_delete_removes_file():
    upload = client.post("/upload", files={"file": b"Hello, World!"}).json()
    response = client.delete(f"/files/{upload['id']}?hash={upload['hash']}")
    assert response.status_code == 200
    assert len(client.get("/files").json()) == 0


def test_delete_wrong_hash_returns_400():
    upload = client.post("/upload", files={"file": b"Hello, World!"}).json()
    response = client.delete(f"/files/{upload['id']}?hash=wronghash")
    assert response.status_code == 400


def test_delete_nonexistent_returns_404():
    response = client.delete("/files/00000000-0000-0000-0000-000000000000?hash=abc")
    assert response.status_code == 404


# --- Unit tests ---

def test_file_upload_state_chunked_hash_matches_full_hash():
    """Verify that hashing a file in chunks produces the same SHA256 as hashing it whole."""
    content = b"Hello, World!" * 1000
    state = FileUploadState()
    for i in range(0, len(content), 64):
        state.update(content[i:i + 64])
    assert state.hexdigest() == hashlib.sha256(content).hexdigest()
    assert state.get_content_bytes() == content


def test_file_data_to_metadata_excludes_content():
    """Verify that to_metadata strips the content field."""
    file_data = FileData(id=uuid4(), hash="abc123", content=b"secret", uploaded_at=datetime.now())
    metadata = file_data.to_metadata()
    assert isinstance(metadata, FileMetadata)
    assert metadata.id == file_data.id
    assert metadata.hash == file_data.hash
    assert not hasattr(metadata, "content")
