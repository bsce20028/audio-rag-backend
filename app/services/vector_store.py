from app.models.db import TranscriptChunk


def upsert_chunks(
    db,
    transcript_id,
    chunks: list[dict],
    embeddings: list[list[float]]
) -> None:
    """
    Save all chunks with their embedding vectors to the DB.
    chunks and embeddings must be the same length and same order.
    """
    for chunk, vector in zip(chunks, embeddings):
        db_chunk = TranscriptChunk(
            transcript_id=transcript_id,
            speaker=chunk["speaker"],
            text=chunk["text"],
            start_time=chunk["start_time"],
            end_time=chunk["end_time"],
            chunk_index=chunk["chunk_index"],
            embedding=vector
        )
        db.add(db_chunk)

    db.commit()


def search(
    db,
    transcript_id,
    query_vector: list[float],
    top_k: int = 5
) -> list[TranscriptChunk]:
    """
    Find the top_k most semantically similar chunks for a given query vector.
    Filters by transcript_id so search stays within one audio file.
    Uses pgvector cosine distance — lower = more similar.
    """
    results = (
        db.query(TranscriptChunk)
        .filter(TranscriptChunk.transcript_id == transcript_id)
        .order_by(TranscriptChunk.embedding.cosine_distance(query_vector))
        .limit(top_k)
        .all()
    )
    return results