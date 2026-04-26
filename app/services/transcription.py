from faster_whisper import WhisperModel
from app.core.config import get_settings

settings = get_settings()

model = WhisperModel(
    settings.WHISPER_MODEL_SIZE,
    device="cpu",
    compute_type="int8"
)


def transcribe(file_path: str) -> list[dict]:
    segments, _ = model.transcribe(
        file_path,
        word_timestamps=True
    )

    result = []

    for segment in segments:
        result.append({
            "text": segment.text.strip(),
            "start": segment.start,
            "end": segment.end
        })

    return result