from fastapi import FastAPI
from endpoints.upload import router as upload_router
from endpoints.list import router as list_router
from endpoints.delete import router as delete_router

app = FastAPI(title="RevEng.AI")

app.include_router(upload_router)
app.include_router(list_router)
app.include_router(delete_router)
