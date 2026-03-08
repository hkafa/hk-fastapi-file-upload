import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'app'))

import pytest
from fastapi.testclient import TestClient
from main import app
from store import Repo
client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_store():
    Repo.store.clear()

def test_upload_returns_metadata():
    response = client.post("/upload", files={"file": b"Hello, World!"})
    assert response.status_code == 201
    data = response.json()
    assert "id" in data
    assert "filename" in data
    assert "hash" in data
    assert "uploaded_at" in data


def test_list_returns_all_files():
    client.post("/upload", files={"file": b"file one"})
    client.post("/upload", files={"file": b"file two"})
    response = client.get("/files")
    assert response.status_code == 200
    assert len(response.json()) == 2


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

