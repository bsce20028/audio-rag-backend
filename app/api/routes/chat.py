from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.deps import get_sync_db
from app.models.schemas import ChatRequest
from app.services.embedding import embed_query
from app.services.vector_store import search
from app.services.rag import build_context, build_messages, stream_answer
from app.models.db import Transcript

router = APIRouter()


@router.post("/chat")
def chat(request: ChatRequest, db: Session = Depends(get_sync_db)):
    
    # 1. Find transcript
    transcript = db.query(Transcript)\
        .filter(Transcript.job_id == request.job_id)\
        .first()

    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")

    # 2. Embed question
    query_vector = embed_query(request.question)

    # 3. Retrieve relevant chunks
    chunks = search(db, transcript.id, query_vector, top_k=5)

    # 4. Build context
    context = build_context(chunks)

    # 5. Build messages
    messages = build_messages(context, request.question)

    # 6. Stream response
    return StreamingResponse(
        stream_answer(messages),
        media_type="text/plain"
    )