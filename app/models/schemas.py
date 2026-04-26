from pydantic import BaseModel
from datetime import datetime


class UploadResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobResponse(BaseModel):
    job_id: str
    status: str
    original_filename: str
    created_at: datetime
    completed_at: datetime | None = None
    error_message: str | None = None

class ChatRequest(BaseModel):
    job_id: str
    question: str