"""Transcribe an audio file with faster-whisper (large-v3, fp16 on CUDA).

Usage:
    python voice_transcribe.py path/to/input.wav
"""
import sys

from faster_whisper import WhisperModel


def transcribe(path: str) -> str:
    model = WhisperModel("large-v3", device="cuda", compute_type="float16")
    segments, _ = model.transcribe(path, vad_filter=True)
    return " ".join(s.text for s in segments)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: voice_transcribe.py <audio_file>", file=sys.stderr)
        sys.exit(2)
    print(transcribe(sys.argv[1]))
