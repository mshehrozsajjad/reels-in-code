"""Word timings from any voice-over or video (your own recording, any TTS, any footage).

    python <skill>/tools/timings.py talking_head.mp4 words.json
    python <skill>/tools/timings.py voice.mp3 words.json --model small.en
    python <skill>/tools/timings.py voice.mp3 words.json --script script.txt --estimate

Default: faster-whisper (local, free) gives a real time for every word.
--estimate: no speech model needed. Finds where speech is (silence detection) and spreads the
script's words over it by length. Good enough for captions when whisper can't be installed or
can't download its model; check the preview and nudge any page that's off.

Writes [{"w": "word", "s": start_seconds, "e": end_seconds}, ...]
"""
import argparse
import json
import re
import subprocess


def whisper_words(media, model_name, language):
    from faster_whisper import WhisperModel

    model = WhisperModel(model_name, device="auto", compute_type="int8")
    segments, _ = model.transcribe(media, word_timestamps=True, language=language, vad_filter=True)
    return [{"w": w.word.strip(), "s": round(w.start, 3), "e": round(w.end, 3)} for seg in segments for w in seg.words if w.word.strip()]


def speech_regions(media, noise_db=-35, min_silence=0.18):
    out = subprocess.run(["ffmpeg", "-i", media, "-af", f"silencedetect=n={noise_db}dB:d={min_silence}", "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    dur = float(re.search(r"Duration: (\d+):(\d+):([\d.]+)", out).groups()[2]) + 60 * float(re.search(r"Duration: (\d+):(\d+)", out).groups()[1]) \
        + 3600 * float(re.search(r"Duration: (\d+)", out).groups()[0])
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", out)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", out)]
    regions, cur = [], 0.0
    for s, e in zip(starts, ends + [dur] * (len(starts) - len(ends))):
        if s - cur > 0.05:
            regions.append((cur, s))
        cur = e
    if dur - cur > 0.05:
        regions.append((cur, dur))
    return regions


def script_words(path):
    words = []
    for line in open(path).read().splitlines():
        line = line.strip()
        if line and not line.startswith("#"):
            words += line.replace("|", " ").split()
    return words


def estimate_words(media, script):
    tokens = script_words(script)
    regions = speech_regions(media)
    weights = [len(re.sub(r"[^\w]", "", t)) + 2 for t in tokens]
    total_speech = sum(e - s for s, e in regions)
    per = total_speech / sum(weights)
    out, ri, used = [], 0, 0.0  # walk through speech regions, filling them in order
    for tok, w in zip(tokens, weights):
        need = w * per
        while ri < len(regions) and used >= regions[ri][1] - regions[ri][0] - 1e-6:
            ri, used = ri + 1, 0.0
        if ri >= len(regions):
            ri, used = len(regions) - 1, regions[-1][1] - regions[-1][0]
        s = regions[ri][0] + used
        used = min(used + need, regions[ri][1] - regions[ri][0])
        out.append({"w": tok, "s": round(s, 3), "e": round(regions[ri][0] + used, 3)})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("media", help="audio or video file with speech")
    ap.add_argument("out", help="words.json to write")
    ap.add_argument("--model", default="base.en", help="whisper model: base.en (fast), small.en, medium.en (more accurate)")
    ap.add_argument("--language", default=None)
    ap.add_argument("--script", help="script.txt (needed for --estimate)")
    ap.add_argument("--estimate", action="store_true", help="no speech model: spread the script over the detected speech")
    a = ap.parse_args()
    if a.estimate:
        if not a.script:
            raise SystemExit("--estimate needs --script")
        words = estimate_words(a.media, a.script)
    else:
        try:
            words = whisper_words(a.media, a.model, a.language)
        except Exception as e:  # model can't install or download (offline sandbox, blocked network)
            if not a.script:
                raise SystemExit(f"whisper failed ({e.__class__.__name__}: {e}). Re-run with --script script.txt --estimate")
            print(f"whisper failed ({e.__class__.__name__}), estimating from the script instead")
            words = estimate_words(a.media, a.script)
    with open(a.out, "w") as f:
        json.dump(words, f, indent=1, ensure_ascii=False)
    print(f"{len(words)} words -> {a.out}")


if __name__ == "__main__":
    main()
