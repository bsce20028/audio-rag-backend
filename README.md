# AudioRAG Backend

Production-ready backend API for transcribing audio files, detecting speakers, and enabling AI-powered Q&A over your recordings.

## What It Does

Upload any audio file → the system transcribes it using Whisper, identifies who spoke when using pyannote.audio, stores semantic embeddings in PostgreSQL with pgvector, and lets you ask natural language questions via a RAG-powered chat endpoint.

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | FastAPI |
| Transcription | faster-whisper (local, free) |
| Speaker Detection | pyannote.audio (local, free) |
| Embeddings | OpenAI text-embedding-3-small |
| Vector DB | PostgreSQL + pgvector |
| LLM | OpenAI GPT-4o-mini |
| Task Queue | Celery + Redis |
| ORM | SQLAlchemy 2.0 + Alembic |

## Prerequisites

- Python 3.10+
- PostgreSQL 16 with pgvector extension
- Redis
- HuggingFace account (for pyannote.audio)
- OpenAI API key

## Setup

```bash
# 1. Clone the repo
git clone https://github.com/YOUR_USERNAME/audiorag-backend.git
cd audiorag-backend

# 2. Create virtual environment
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # Mac/Linux

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Fill in all values in .env

# 5. Create database
psql -U postgres -c "CREATE DATABASE audiodb;"
psql -U postgres -d audiodb -c "CREATE EXTENSION IF NOT EXISTS vector;"

# 6. Run migrations
alembic upgrade head

# 7. Start the API
uvicorn app.main:app --reload
```

## Running the Worker

Open a second terminal and run:

```bash
venv\Scripts\activate
celery -A app.workers.celery_app worker --loglevel=info --pool=solo
```

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | /api/v1/health | Health check |
| POST | /api/v1/upload | Upload audio file |
| GET | /api/v1/jobs/{job_id} | Poll job status |
| GET | /api/v1/transcripts/{job_id} | Get transcript with speaker labels |
| POST | /api/v1/chat | RAG Q&A — streams response |

## Processing Pipeline

1. Audio uploaded → Job created → Celery task enqueued
2. faster-whisper transcribes with word-level timestamps
3. pyannote.audio segments audio by speaker
4. Transcript and speaker segments merged
5. Chunks embedded via OpenAI and stored in pgvector
6. Job marked DONE — ready to chat

## Environment Variables

See `.env.example` for all required variables including database URL, Redis URL, OpenAI API key, and HuggingFace token.

## Project Structure

```
app/
├── api/routes/        # FastAPI route handlers
├── core/              # Config, security, database
├── models/            # SQLAlchemy models + Pydantic schemas
├── services/          # Transcription, embedding, RAG, vector store
└── workers/           # Celery app and tasks
alembic/               # Database migrations
```
