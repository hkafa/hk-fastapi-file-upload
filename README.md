# RevengAI File Service

A simple file upload and listing API consisting of:

- A FastAPI API that can accept file uploads
- For each uploaded file it will generate a SHA256 hash of the file
- Store the files in memory
- Return the list of uploaded files via an endpoint
- Allow deleting a file via an endpoint by both file ID and SHA256

---

## Assumptions

- **Duplicate uploads are permitted.** The store is indexed by a generated UUID (file ID), following standard database convention. Therefore, uploading the same file multiple times will produce distinct entries with different UUIDs but identical hashes

- **File content is not returned by the list endpoint.** Since the supported file types are not specified, returning content was deliberately avoided for two reasons: (1) files could be very large, making a list response very expensive; (2) binary files cannot be directly serialised into JSON without encoding, which would  require the client to decode them. The list endpoint returns metadata only (`id`, `hash`, `uploaded_at`).

---

## Running with Docker

### Build the image

```bash
docker build -t revengai .
```

### Run the container

```bash
docker run -p 8000:8000 revengai
```

> **Note:** Storage is in-memory. All uploaded files are lost when the container stops.

---

## Interactive API Docs

FastAPI provides auto-generated documentation at:

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## API Structure

The API has three endpoints:

| Method   | Path             | Description               |
|----------|------------------|---------------------------|
| `POST`   | `/upload`        | Upload a file             |
| `GET`    | `/files`         | List all uploaded files   |
| `DELETE` | `/files/{id}`    | Delete a file by ID/hash  |

All responses are JSON.

---

## Testing

To run the tests use `uv run pytest`.

---

## Example curl Commands

### 1. Upload a text file

```bash
echo "Hello, World" | curl -F "file=@-" http://localhost:8000/upload
```

### 2. Upload a binary file

```bash
dd if=/dev/urandom bs=64 count=1 of=sample.bin 2>/dev/null

curl -X POST http://localhost:8000/upload \
  -F "file=@sample.bin"
```

### 3. List all files

```bash
curl http://localhost:8000/files
```

### 4. Delete a file

Use the `id` and `hash` from the upload response:

```bash
curl -X DELETE "http://localhost:8000/files/<id>?hash=<hash>"
```

---
