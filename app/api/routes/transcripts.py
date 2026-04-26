from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.models.db import Transcript
from sqlalchemy import select
import uuid

router = APIRouter()


@router.get("/transcripts/{job_id}")
async def get_transcript(job_id: str, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Transcript).where(Transcript.job_id == uuid.UUID(job_id))
    )
    transcript = result.scalar_one_or_none()

    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    return transcript.raw_json