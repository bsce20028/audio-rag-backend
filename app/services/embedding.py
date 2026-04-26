from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def chunk_transcript(merged_segments: list[dict]) -> list[dict]:
    """
    Group consecutive segments by same speaker into one chunk.
    
    Input:  [{"speaker": "SPEAKER_00", "text": "hello", "start": 0.0, "end": 2.0}, ...]
    Output: [{"speaker": "SPEAKER_00", "text": "hello how are you", "start_time": 0.0, "end_time": 6.0, "chunk_index": 0}, ...]
    """
    if not merged_segments:
        return []

    chunks = []
    chunk_index = 0

    # Start with the first segment
    current_speaker = merged_segments[0]["speaker"]
    current_texts = [merged_segments[0]["text"]]
    current_start = float(merged_segments[0]["start"])
    current_end = float(merged_segments[0]["end"])

    for seg in merged_segments[1:]:
        if seg["speaker"] == current_speaker:
            # Same speaker — keep accumulating
            current_texts.append(seg["text"])
            current_end = float(seg["end"])
        else:
            # Speaker changed — save current chunk, start new one
            chunks.append({
                "speaker": current_speaker,
                "text": " ".join(current_texts).strip(),
                "start_time": current_start,
                "end_time": current_end,
                "chunk_index": chunk_index
            })
            chunk_index += 1

            # Reset for new speaker
            current_speaker = seg["speaker"]
            current_texts = [seg["text"]]
            current_start = float(seg["start"])
            current_end = float(seg["end"])

    # Don't forget the last chunk
    chunks.append({
        "speaker": current_speaker,
        "text": " ".join(current_texts).strip(),
        "start_time": current_start,
        "end_time": current_end,
        "chunk_index": chunk_index
    })

    return chunks
def embed_chunks(texts: list[str]) -> list[list[float]]:
    """
    Embed a list of texts using OpenAI text-embedding-3-small.
    Sends in batches of 100 to stay within API limits.
    
    Input:  ["hello world", "how are you", ...]
    Output: [[0.123, 0.456, ...], [0.789, 0.012, ...], ...]  # each is 1536 floats
    """
    if not texts:
        return []

    all_embeddings = []
    batch_size = 100

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]

        response = client.embeddings.create(
            input=batch,
            model=settings.EMBEDDING_MODEL  # text-embedding-3-small
        )

        # response.data is a list ordered same as input
        batch_embeddings = [item.embedding for item in response.data]
        all_embeddings.extend(batch_embeddings)

    return all_embeddings


def embed_query(query: str) -> list[float]:
    """
    Embed a single query string — used at search time.
    
    Input:  "what did Sarah say about the appointment?"
    Output: [0.123, 0.456, ...]  # 1536 floats
    """
    response = client.embeddings.create(
        input=[query],
        model=settings.EMBEDDING_MODEL
    )
    return response.data[0].embedding