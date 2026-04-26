from pyannote.audio import Pipeline
from app.core.config import get_settings
import soundfile as sf
import torch

settings = get_settings()

_pipeline = None


def _get_pipeline():
    global _pipeline
    if _pipeline is None:
        _pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            token=settings.HF_TOKEN
        )
    return _pipeline

def segment(file_path: str) -> list[dict]:
    pipeline = _get_pipeline()

    waveform, sample_rate = sf.read(file_path, dtype="float32", always_2d=True)
    waveform = torch.tensor(waveform.T)

    diarization = pipeline(
        {"waveform": waveform, "sample_rate": sample_rate}
    )

    annotation = diarization.speaker_diarization

    result = []
    for turn, _, speaker in annotation.itertracks(yield_label=True):
        result.append({
            "speaker": speaker,
            "start": round(turn.start, 3),
            "end": round(turn.end, 3)
        })

    return result

def merge_with_transcript(transcript_segments, speaker_segments):
    merged = []

    # Keep deterministic order for overlap-based scoring.
    ordered_speakers = sorted(speaker_segments, key=lambda s: (s["start"], s["end"]))

    for seg in transcript_segments:
        seg_start = float(seg["start"])
        seg_end = float(seg["end"])
        seg_duration = max(seg_end - seg_start, 1e-6)
        speaker_label = "UNKNOWN"
        best_overlap = 0.0

        for sp in ordered_speakers:
            overlap_start = max(seg_start, float(sp["start"]))
            overlap_end = min(seg_end, float(sp["end"]))
            overlap = max(0.0, overlap_end - overlap_start)

            if overlap > best_overlap:
                best_overlap = overlap
                speaker_label = sp["speaker"]

        # Fallback for edge-touching intervals with no positive overlap.
        if speaker_label == "UNKNOWN":
            mid = (seg_start + seg_end) / 2
            for sp in ordered_speakers:
                if float(sp["start"]) <= mid <= float(sp["end"]):
                    speaker_label = sp["speaker"]
                    break

        merged.append({
            "speaker": speaker_label,
            "text": seg["text"],
            "start": seg_start,
            "end": seg_end,
            "speaker_overlap_ratio": round(best_overlap / seg_duration, 4)
        })

    return merged