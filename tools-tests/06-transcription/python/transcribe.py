"""Transcription tools test: transcribe part of a lecture recording locally with faster-whisper.

The audio never leaves this computer. The model weights are downloaded once, on the first run.
The transcript is written to course-materials/transcription-output/ (out of git), and is NOT
printed, because recordings can contain voices of students. Only timing numbers are printed.

Usage: python transcribe.py <recording> [start_seconds end_seconds]
"""
import os
import sys
import time
from pathlib import Path

os.environ["HF_HUB_DISABLE_TELEMETRY"] = "1"  # no usage data to Hugging Face

from faster_whisper import WhisperModel, decode_audio

MODEL = "large-v3-turbo"
LANGUAGE = "he"
SAMPLE_RATE = 16000              # decode_audio returns 16 kHz mono
FULL_LESSON_MIN = 5632 / 60      # 01:33:52, the recording length in the Zoom summary
OUT_DIR = Path(__file__).resolve().parents[3] / "course-materials" / "transcription-output"

if len(sys.argv) not in (2, 4):
    raise SystemExit("Usage: python transcribe.py <recording> [start_seconds end_seconds]")
recording = Path(sys.argv[1])
start_s, end_s = (float(sys.argv[2]), float(sys.argv[3])) if len(sys.argv) == 4 else (0.0, None)

t0 = time.perf_counter()
model = WhisperModel(MODEL, device="cpu", compute_type="int8")
load_s = time.perf_counter() - t0

t0 = time.perf_counter()
audio = decode_audio(str(recording), sampling_rate=SAMPLE_RATE)
audio = audio[int(start_s * SAMPLE_RATE):None if end_s is None else int(end_s * SAMPLE_RATE)]
decode_s = time.perf_counter() - t0
clip_min = len(audio) / SAMPLE_RATE / 60

t0 = time.perf_counter()
segments, info = model.transcribe(audio, language=LANGUAGE)
lines = [f"[{start_s + s.start:7.1f}-{start_s + s.end:7.1f}] {s.text.strip()}" for s in segments]  # runs here
transcribe_s = time.perf_counter() - t0

per_min = transcribe_s / clip_min
OUT_DIR.mkdir(parents=True, exist_ok=True)
out_file = OUT_DIR / f"{recording.stem}_{int(start_s)}s.txt"
out_file.write_text("\n".join(lines) + "\n", encoding="utf-8")

report = (
    f"Model: {MODEL} (int8, CPU), language: {LANGUAGE}\n"
    f"Clip: {clip_min * 60:.1f} s from {recording.name}, starting at {start_s:.0f} s\n"
    f"Model load: {load_s:.1f} s (the first run also downloads the model)\n"
    f"Audio decoding: {decode_s:.1f} s\n"
    f"Transcription: {transcribe_s:.1f} s = {per_min:.1f} s per minute of recording\n"
    f"Estimate for a {FULL_LESSON_MIN:.1f}-minute lesson: {per_min * FULL_LESSON_MIN / 60:.1f} min\n"
    f"Segments: {len(lines)}; transcript saved to {out_file}\n"
)
print(report, end="")
(OUT_DIR / f"log-{recording.stem}_{int(start_s)}s.txt").write_text(report, encoding="utf-8")
