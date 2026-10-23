"""Turn a script + word timings into the edit file (remotion/public/edit.json).

    python tools/build_edit.py --script script.txt --words words.json --video talking_head.mp4
    python tools/build_edit.py --script script.txt --words words.json --audio voice.mp3            # type on black
    python tools/build_edit.py --script script.txt --words words.json --audio voice.mp3 --video broll.mp4

script.txt: one line = one on-screen page, written as   small words above | KEYWORD | small words below
    this reel never touched an | editing app.
    I build the | system | that edits them.
Lines starting with # are ignored. The words must follow what is actually said (small differences are fine).

The result is a starting point: one scene with your footage (or black) and all the type pages.
Cut-ins, insets and mask words are added by editing edit.json (that is what the skill tells Claude to do).
"""
import argparse
import difflib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PUB = ROOT / "remotion" / "public"
FPS = 30


def norm(w):
    return re.sub(r"[^a-z0-9]", "", w.lower())


def media_dur(p):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)], capture_output=True, text=True)
    return float(out.stdout.strip())


def parse_script(path):
    pages = []
    for line in Path(path).read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        parts = [x.strip() for x in line.split("|")]
        if len(parts) == 1:  # no | given: last word is the keyword
            ws = parts[0].split()
            parts = [" ".join(ws[:-1]), ws[-1], ""]
        while len(parts) < 3:
            parts.append("")
        pages.append([p.split() for p in parts[:3]])
    return pages


def align(script_tokens, words):
    """Give every script token the time of the matching spoken word (fuzzy, in order)."""
    a = [norm(t) for t in script_tokens]
    b = [norm(w["w"]) for w in words]
    times = [None] * len(a)
    for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
        for k in range(blk.size):
            times[blk.a + k] = words[blk.b + k]["s"]
    # fill gaps by interpolating between known neighbours
    known = [i for i, x in enumerate(times) if x is not None]
    if not known:
        raise SystemExit("none of the script words were found in the transcript")
    for i in range(len(times)):
        if times[i] is None:
            prev = max([k for k in known if k < i], default=None)
            nxt = min([k for k in known if k > i], default=None)
            if prev is None:
                times[i] = times[nxt]
            elif nxt is None:
                times[i] = times[prev] + 0.25 * (i - prev)
            else:
                times[i] = times[prev] + (times[nxt] - times[prev]) * (i - prev) / (nxt - prev)
    missed = len(a) - len(known)
    if missed:
        print(f"note: {missed} script words had no exact match and were timed by interpolation")
    return times


def copy_in(src):
    src = Path(src)
    PUB.mkdir(parents=True, exist_ok=True)
    dst = PUB / src.name
    if src.resolve() != dst.resolve():
        shutil.copy(src, dst)
    return src.name


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--script", required=True)
    ap.add_argument("--words", required=True)
    ap.add_argument("--video", help="footage shown full screen (its own sound is used if no --audio)")
    ap.add_argument("--audio", help="separate voice-over")
    ap.add_argument("--out", default=str(PUB / "edit.json"))
    a = ap.parse_args()
    if not a.video and not a.audio:
        raise SystemExit("give --video, --audio, or both")

    words = json.load(open(a.words))
    pages_tok = parse_script(a.script)
    flat = [t for pg in pages_tok for grp in pg for t in grp]
    times = align(flat, words)

    pages, k = [], 0
    for i, pg in enumerate(pages_tok):
        groups = []
        for grp in pg:
            groups.append([{"w": t, "s": round(times[k + j], 3)} for j, t in enumerate(grp)])
            k += len(grp)
        allw = [w for g in groups for w in g]
        pages.append({"before": groups[0], "key": groups[1], "after": groups[2], "start": allw[0]["s"], "edge": "right" if i % 2 == 0 else "left"})

    total = media_dur(a.audio or a.video) + 0.3
    for i, p in enumerate(pages):
        p["end"] = round(pages[i + 1]["start"] if i + 1 < len(pages) else total, 3)

    scene = {"start": 0, "dur": round(total, 3), "kind": "speaker" if a.video else "black"}
    if a.video:
        scene["src"] = copy_in(a.video)
        scene["muted"] = bool(a.audio)  # use the video's own sound when there is no separate voice-over
    edit = {"fps": FPS, "width": 1080, "height": 1920, "durationInFrames": int(round(total * FPS)),
            "overlay": {"from": 0.58, "strength": 0.95}, "captions": {"top": 1565, "size": 178}, "scenes": [scene], "pages": pages}
    if a.audio:
        edit["audio"] = copy_in(a.audio)
    Path(a.out).write_text(json.dumps(edit, indent=1, ensure_ascii=False))
    print(f"{len(pages)} pages, {total:.1f}s -> {a.out}")


if __name__ == "__main__":
    main()
