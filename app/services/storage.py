import os
import uuid
import aiofiles
from fastapi import UploadFile, HTTPException

ALLOWED_TYPES = {
    "audio/mpeg",
    "audio/wav",
    "audio/mp4",
    "audio/x-m4a",
    "audio/webm",
    "audio/ogg",
}

UPLOAD_DIR = os.getenv("UPLOAD_DIR", "uploads")
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", 500))


async def save_upload(file: UploadFile) -> tuple[str, str]:
    if file.content_type not in ALLOWED_TYPES:
        raise HTTPException(status_code=415, detail="Unsupported file type")

    contents = await file.read()
    size_mb = len(contents) / (1024 * 1024)

    if size_mb > MAX_UPLOAD_SIZE_MB:
        raise HTTPException(status_code=413, detail="File too large")

    ext = file.filename.split(".")[-1]
    file_id = str(uuid.uuid4())
    file_path = f"{UPLOAD_DIR}/{file_id}.{ext}"

    async with aiofiles.open(file_path, "wb") as f:
        await f.write(contents)

    return file.filename, file_path