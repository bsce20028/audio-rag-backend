from openai import OpenAI
from app.core.config import get_settings

settings = get_settings()
client = OpenAI(api_key=settings.OPENAI_API_KEY)


def build_context(chunks) -> str:
    lines = []

    for chunk in chunks:
        start = f"{int(chunk.start_time // 60):02d}:{int(chunk.start_time % 60):02d}"
        end = f"{int(chunk.end_time // 60):02d}:{int(chunk.end_time % 60):02d}"

        lines.append(
            f"[Speaker: {chunk.speaker} | {start} - {end}]\n{chunk.text}"
        )

    return "\n\n".join(lines)


def build_messages(context: str, question: str) -> list[dict]:
    system_prompt = """You are a helpful assistant with access to an audio transcript. Answer naturally and conversationally like a human — not like a bot.

Rules:
- For greetings (hi, hello, good morning, how are you, etc.) — just respond naturally and warmly. Don't mention the transcript at all.
- For actual questions — answer directly and to the point using the transcript context below. Don't add unnecessary preamble.
- NEVER say "I couldn't find that in the transcript" for small talk or greetings.
- Only mention speaker names and timestamps if the user explicitly asks who said something or when something was said. Otherwise just answer the question naturally.
- If something genuinely isn't in the transcript and it's a real question, just say "I don't have information on that" — keep it short.
- No bullet points, no headers, no excessive formatting unless the answer genuinely needs structure.
- Keep answers concise. Don't over-explain.

TRANSCRIPT:
""" + context

    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question}
    ]


def stream_answer(messages: list[dict]):
    stream = client.chat.completions.create(
        model=settings.LLM_MODEL,
        messages=messages,
        stream=True
    )

    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta