from sys import prefix
import os
from fastapi import FastAPI
from app.core.config import get_settings
from app.api.routes import upload, jobs, transcripts
from app.api.routes import chat
UPLOAD_DIR = os.getenv("UPLOAD_DIR","uploads")

app = FastAPI()

@app.on_event("startup")
def create_upload_dir():
    os.makedirs(UPLOAD_DIR,exist_ok=True)

app.include_router(upload.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(transcripts.router, prefix="/api/v1")
app.include_router(chat.router, prefix="/api/v1")