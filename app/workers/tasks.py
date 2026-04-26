from datetime import datetime
from app.workers.celery_app import celery
from app.core.database import SyncSessionLocal
from app.models.db import Job, Transcript
from app.services.transcription import transcribe
from app.services.speaker_segmentation import segment, merge_with_transcript
from app.services.embedding import chunk_transcript, embed_chunks
from app.services.vector_store import upsert_chunks
import traceback


@celery.task
def process_audio(job_id: str):
    db = SyncSessionLocal()

    try:
        # 1. fetch job & mark processing
        job = db.query(Job).filter(Job.id == job_id).first()
        job.status = "PROCESSING"
        db.commit()

        # 2. transcribe
        print(f"[{job_id}] Starting transcription...")
        transcript_segments = transcribe(job.file_path)
        print(f"[{job_id}] Transcription done — {len(transcript_segments)} segments")

        # 3. speaker segmentation
        print(f"[{job_id}] Starting speaker segmentation...")
        speaker_segments = segment(job.file_path)
        print(f"[{job_id}] Speaker segmentation done — {len(speaker_segments)} speaker segments")

        # 4. merge transcript + speakers
        merged_segments = merge_with_transcript(transcript_segments, speaker_segments)
        print(f"[{job_id}] Merge done — {len(merged_segments)} merged segments")

        # 5. save transcript to DB
        transcript = Transcript(
            job_id=job.id,
            raw_json=merged_segments
        )
        db.add(transcript)
        db.flush()  # get transcript.id without full commit

        # 6. chunk by speaker turn
        chunks = chunk_transcript(merged_segments)
        print(f"[{job_id}] Chunking done — {len(chunks)} chunks")

        # 7. embed all chunks
        texts = [c["text"] for c in chunks]
        print(f"[{job_id}] Embedding {len(texts)} chunks via OpenAI...")
        embeddings = embed_chunks(texts)
        print(f"[{job_id}] Embeddings done — {len(embeddings)} vectors")

        # 8. store vectors in pgvector
        upsert_chunks(db, transcript.id, chunks, embeddings)
        print(f"[{job_id}] Vectors stored in pgvector")

        # 9. mark job done
        job.status = "DONE"
        job.completed_at = datetime.utcnow()
        db.commit()
        print(f"[{job_id}] Pipeline complete ✓")

    except Exception as e:
        job.status = "FAILED"
        job.error_message = str(e)
        db.commit()
        print(f"[{job_id}] FAILED: {e}")
        traceback.print_exc()
        raise

    finally:
        db.close()