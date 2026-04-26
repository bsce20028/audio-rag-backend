import uuid
from sqlalchemy import Column, String, Boolean, ForeignKey, DateTime, Text, Float, Integer
from sqlalchemy.dialects.postgresql import UUID, JSON
from pgvector.sqlalchemy import Vector
from sqlalchemy.sql import func
from app.core.database import Base
from datetime import datetime
from uuid import uuid4
class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = "jobs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    original_filename = Column(String)
    file_path = Column(String)
    status = Column(String, default="PENDING")
    error_message = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True), nullable=True)

class Transcript(Base):
    __tablename__ = "transcripts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    job_id = Column(UUID(as_uuid=True), ForeignKey("jobs.id"), unique=True)
    raw_json = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class TranscriptChunk(Base):
    __tablename__ = "transcript_chunks"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)

    transcript_id = Column(
        UUID(as_uuid=True),
        ForeignKey("transcripts.id"),
        nullable=False
    )

    speaker = Column(String, nullable=True)
    text = Column(Text)

    start_time = Column(Float)
    end_time = Column(Float)

    chunk_index = Column(Integer)

    embedding = Column(Vector(1536))