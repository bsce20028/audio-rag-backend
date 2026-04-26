import uuid
from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.workers.tasks import process_audio
from app.services.storage import save_upload
from app.core.database import get_db
from app.models.db import Job

router = APIRouter()


@router.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
    original_filename, file_path = await save_upload(file)

    job = Job(
        id=uuid.uuid4(),
        user_id=None,  # optional for now
        original_filename=original_filename,
        file_path=file_path,
        status="PENDING"
    )

    db.add(job)
    await db.commit()
    await db.refresh(job)
    process_audio.delay(str(job.id))

    return {
        "job_id": str(job.id),
        "status": job.status,
        "message": "File uploaded successfully"
    }