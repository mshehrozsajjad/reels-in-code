"""Word timings from any voice-over or video (your own recording, any TTS, any footage).

    python tools/timings.py voice.mp3 words.json
    python tools/timings.py talking_head.mp4 words.json --model small.en

Writes [{"w": "word", "s": start_seconds, "e": end_seconds}, ...] using faster-whisper (runs locally, free).
"""
import argparse
import json

from faster_whisper import WhisperModel


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media", help="audio or video file with speech")
    ap.add_argument("out", help="words.json to write")
    ap.add_argument("--model", default="base.en", help="whisper model: base.en (fast), small.en, medium.en (more accurate)")
    ap.add_argument("--language", default=None, help="e.g. en, de (needed for non-.en models if auto-detect is wrong)")
    a = ap.parse_args()
    model = WhisperModel(a.model, device="auto", compute_type="int8")
    segments, _ = model.transcribe(a.media, word_timestamps=True, language=a.language, vad_filter=True)
    words = [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for seg in segments for w in seg.words if w.word.strip()]
    with open(a.out, "w") as f:
        json.dump(words, f, indent=1, ensure_ascii=False)
    print(f"{len(words)} words -> {a.out}")


if __name__ == "__main__":
    main()
