# Reels in Code

Edit short vertical videos (Reels, TikToks, Shorts) without an editing app.
The whole edit lives in one text file. You give Claude notes like you would to an editor, and every note that matters becomes a rule it remembers next time.

This is the setup I use for my own reels: a **Claude skill** + a **Remotion starter project** with my text style (big keyword lockups, words fading in as they're spoken, a black gradient, and a giant word behind the speaker).

Works with **any footage** (phone, camera, screen recording, AI avatar) and **any voice-over** (your own voice or any text-to-speech).

## What's inside

| | |
|---|---|
| `skill/reels-in-code/SKILL.md` | The Claude skill: script shape for feeds, the notes → edits → rules loop, how the edit file works, render commands |
| `RULES.md` | Your own rules. Claude reads it before every edit and adds to it when you give a lasting note |
| `remotion/` | The video project. `src/style/StyleC.tsx` is the look, `src/Reel.tsx` draws the edit, `public/edit.json` is the edit |
| `tools/timings.py` | Times every word of your audio or video (local Whisper, free) |
| `tools/build_edit.py` | Script + word timings → `edit.json` |
| `tools/matte.py` | Cuts the person out of a clip, for the word-behind-you effect |
| `example/script.txt` | Script format example |

## Setup (once)

You need [Node.js](https://nodejs.org) 18+, Python 3.10+ and [ffmpeg](https://ffmpeg.org).

```bash
git clone https://github.com/mshehrozsajjad/reels-in-code.git
cd reels-in-code
cd remotion && npm install && cd ..
pip install -r tools/requirements.txt
```

See the demo: `cd remotion && npx remotion studio`

**Add the skill to Claude**
- Claude Code: copy `skill/reels-in-code` into `~/.claude/skills/` (or `.claude/skills/` in this project).
- Claude app: zip the `skill/reels-in-code` folder and upload it in your Skills settings.

Then open this folder with Claude and say: *"Let's make a reel about …"*

## Make a reel by hand (what the skill automates)

1. Write `script.txt`, one on-screen page per line: `small words above | KEYWORD | small words below`
2. Record your video or voice-over.
3. `python tools/timings.py my_video.mp4 words.json`
4. `python tools/build_edit.py --script script.txt --words words.json --video my_video.mp4`
5. `cd remotion && npx remotion studio` to preview.
6. Give Claude notes. It edits `remotion/public/edit.json`.
7. `npx remotion render src/index.ts Reel out/reel.mp4 --props=public/edit.json`

Word behind you, on your strongest line:

```bash
python tools/matte.py remotion/public/my_video.mp4 remotion/public/my_video_mask.webm
```
then add `"mask": "my_video_mask.webm", "maskWord": {"text": "SYSTEM", "at": 12.4}` to that scene in `edit.json`.

## License

MIT. Use it, change it, make it yours.
