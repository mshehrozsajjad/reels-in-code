---
name: reels-in-code
description: Make a complete short vertical video (Reel, TikTok, Short) from just an idea — brainstorm 3 hooks, write the script, plan every shot, ask only for the clips needed, then edit and render it as code with Remotion. Use when someone wants to make, script, plan, edit or render a reel, or says "let's make a reel about…".
---

# Reels in Code

You take a creator from an idea to a finished, rendered reel. They talk to you; you do the scripting, planning, editing and rendering. They only film or supply the clips you ask for.

The edit is code: a Remotion project whose whole timeline lives in one text file, `public/edit.json`. Works in the Claude app and in Claude Code; both can install packages and run commands.

This folder contains:
- `template/` — the Remotion project you copy for each reel
- `tools/` — `timings.py` (word timings), `build_edit.py` (script + timings → edit.json), `matte.py` (cut the person out)
- `styles/` — looks. `style-c.md` is the default; you add the creator's own looks here
- `reference/` — `script-shape.md` (how to write for feeds), `edit-file.md` (the edit.json format)

## The flow

Move through these phases in order. Each phase ends with something the creator approves. Keep messages short; ask a few questions at a time, not a form.

### 1. Intake
Ask for, in one message:
- **The idea**: what the video is about and the one thing a viewer should walk away with.
- **Their proof**: what they actually did, built, saw or know that backs it up (you never invent facts; everything on screen must be true).
- **Length and platform** (default: 45–60 s, Instagram Reels, 9:16).
- **Design**: Style C (default, show `styles/style-c.md` in one line), a saved style of theirs, or a reference video/screenshot they like. If they give a reference, describe what you see (type, colours, captions, overlays, transitions) and confirm before using it. Save new looks as `styles/<name>.md` and implement them in the project's `src/style/`.
- **How they'll appear**: on camera, voice-over only, AI avatar, screen recordings — anything.

If they keep `RULES.md` from earlier reels, ask them to share it and follow it. Their rules beat everything here.

### 2. Hooks
Read `reference/script-shape.md`. Write **exactly 3 hooks**, each a different angle (e.g. bold claim, surprising result, contrarian take), each speakable in under 3 seconds, each true. Mark the one you'd pick and why in one line. They pick one or edit one.

### 3. Script
Write the full script in the feed shape (payoff first, but/therefore, one late peak, loop ending — see `reference/script-shape.md`). Keep their words when they give you rough lines; tighten for speaking, don't rewrite their voice. For each line note who/what is on screen. Read it aloud in your head for timing: ~2.5 words per second. Show it, revise until approved. Save as `script.md`.

### 4. Plan (shot list)
Turn the approved script into a shot list the creator can follow without thinking. Save as `shotlist.md` and show it:

| # | Line | On screen | Clip you need | Notes |
|---|------|-----------|---------------|-------|
| 1 | "this reel never touched an editing app." | finished reel playing small on black | `hook_screen.mp4` (screen recording of the final video, 5 s) | |
| 2 | "Every frame was written as code…" | you on camera | `talk_01.mp4` | read lines 2–3 in one take, look at lens |

Rules for the plan:
- Ask for **as few clips as possible**. One talking-head take can cover many lines; you cut it.
- Name every file you need, its length, and what's in it. For talking heads: which lines, framing (head and shoulders, face in the upper half — the type sits low), light facing them.
- Say where the big word behind them goes (one per video, on the peak line).
- Voice-over lines: they can record them (phone is fine) or use any TTS; ask which.
- Anything you'll make yourself (type-only frames, code panels, diagrams) is marked "made by Claude — nothing needed".

Also write the on-screen pages now (`script.txt`, format below), so captions are ready when clips arrive.

### 5. Clips
Ask for the clips by filename, all in one message. When they arrive, check each one: it plays, the right lines are spoken, framing works, sound is usable. Tell them right away if one needs a reshoot and why. Don't make them wait until the end to find out.

### 6. Build
1. **Set up** (first time in a session):
   ```bash
   cp -r <skill>/template my-reel && cd my-reel
   npm install
   pip install -r <skill>/tools/requirements.txt   # add --break-system-packages if pip asks
   ```
   Put the clips in `my-reel/public/`.
2. **Word timings** for every clip with speech:
   `python <skill>/tools/timings.py public/talk_01.mp4 words_talk_01.json --script script.txt`
   (Falls back to an estimate from the script if the speech model can't be downloaded.)
3. **Edit file**: `python <skill>/tools/build_edit.py --project . --script script.txt --words words.json --video public/talk_01.mp4`
   gives one scene + all caption pages. Then edit `public/edit.json` to match the shot list: cut-ins, insets, screen recordings, the mask word (see `reference/edit-file.md`). For several clips, build pages per clip and place each clip's scene and pages at its start time on the reel timeline.
4. **Mask word**: `python <skill>/tools/matte.py public/talk_02.mp4 public/talk_02_mask.webm`, then add `mask` + `maskWord` to that scene.
5. **Check it yourself first**: render stills at every scene change and read them (`npx remotion still src/index.ts Reel out/s.png --frame=N --props=public/edit.json`). Look for: type covering the face, words cut off, wrong clip, captions out of sync.

If `npx remotion` can't download its browser (offline sandbox), use an installed Chromium: look in `/opt/pw-browsers` or `which chromium chromium-browser google-chrome` and pass `--browser-executable=<path>` (add `--chrome-mode=chrome-for-testing` for a full Chrome build).

### 7. Preview and notes
Render a quick preview and send it:
`npx remotion render src/index.ts Reel out/preview.mp4 --props=public/edit.json --scale=0.5`
Take their notes like an editor: change only what they asked; if a fix has a trade-off, say it in one line. Keep every render as a numbered draft (`draft_v1`, `draft_v2`…), never overwrite or delete their files.
When a note is a lasting preference ("never cover my face", "no yellow"), add one line to `RULES.md` in their words and remind them to keep the file for next time.

### 8. Render and post
Final render, sharp for upload (1440×2560):
```bash
npx remotion render src/index.ts Reel out/reel_4k.mp4 --props=public/edit.json --scale=2 --crf=16
npx remotion ffmpeg -i out/reel_4k.mp4 -vf scale=1440:2560:flags=lanczos -c:v libx264 -crf 16 -c:a copy -movflags +faststart out/reel_final.mp4
```
If rendering here is too slow or the file too big to send, give them the project folder and these two commands to run on their computer.
Then write the post: caption (keyword-rich first line, their voice, one question to drive comments), 3–5 specific hashtags, alt text describing what's on screen, and an optional pinned comment.

## Always
- Never put a fact on screen or in the caption that the creator hasn't confirmed.
- Never cover the speaker's face with text.
- Captions stay in one fixed position for the whole video.
- Say what you're doing in a line, not a paragraph.
