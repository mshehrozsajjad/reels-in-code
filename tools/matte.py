"""Cut the person out of a video (for the "word behind the speaker" effect).

    python tools/matte.py remotion/public/talking_head.mp4 remotion/public/talking_head_mask.webm

Writes a VP9 WebM with transparency: the person stays, the background is see-through.
In edit.json, put it on the same scene as the footage:  "mask": "talking_head_mask.webm",
"maskWord": {"text": "SYSTEM", "at": 47.8}. The word is drawn between the footage and the cut-out,
so the person's head overlaps it.

Uses Robust Video Matting (MobileNetV3, ONNX, CPU is fine: roughly 5-10 frames per second).
"""
import subprocess
import sys
import urllib.request
from pathlib import Path

import numpy as np
import onnxruntime as ort

MODEL = Path(__file__).parent / "models" / "rvm_mobilenetv3_fp32.onnx"
MODEL_URL = "https://github.com/PeterL1n/RobustVideoMatting/releases/download/v1.0.0/rvm_mobilenetv3_fp32.onnx"


def matte(src, dst, downsample=0.25):
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        print("downloading the matting model (15 MB) ...")
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    probe = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height,r_frame_rate",
                            "-of", "csv=p=0", str(src)], capture_output=True, text=True, check=True).stdout.strip().split(",")
    w, h, fps = int(probe[0]), int(probe[1]), probe[2]
    sess = ort.InferenceSession(str(MODEL), providers=["CPUExecutionProvider"])
    rec = [np.zeros([1, 1, 1, 1], np.float32)] * 4
    ds = np.array([downsample], np.float32)
    dec = subprocess.Popen(["ffmpeg", "-v", "error", "-i", str(src), "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
    enc = subprocess.Popen(["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgba", "-s", f"{w}x{h}", "-r", fps, "-i", "-",
                            "-c:v", "libvpx-vp9", "-pix_fmt", "yuva420p", "-b:v", "0", "-crf", "18", "-row-mt", "1",
                            "-deadline", "good", "-cpu-used", "4", "-auto-alt-ref", "0", str(dst)], stdin=subprocess.PIPE)
    n = 0
    while True:
        buf = dec.stdout.read(w * h * 3)
        if len(buf) < w * h * 3:
            break
        f = np.frombuffer(buf, np.uint8).reshape(h, w, 3)
        x = (f.astype(np.float32) / 255).transpose(2, 0, 1)[None]
        _fgr, pha, *rec = sess.run([], {"src": x, "r1i": rec[0], "r2i": rec[1], "r3i": rec[2], "r4i": rec[3], "downsample_ratio": ds})
        alpha = (np.clip(pha[0, 0], 0, 1) * 255).astype(np.uint8)
        enc.stdin.write(np.dstack([f, alpha]).tobytes())
        n += 1
        if n % 50 == 0:
            print(f"  {n} frames")
    enc.stdin.close()
    enc.wait()
    print(f"{n} frames -> {dst}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    matte(sys.argv[1], sys.argv[2])
