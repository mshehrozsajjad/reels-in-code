---
name: reels-in-code
description: Make short vertical videos (Reels, TikToks, Shorts) as code with Remotion — write the script, time every word, build the edit file, change it from plain-language notes, and turn every note into a lasting rule. Use when someone wants to script, edit, restyle or render a reel without an editing app.
---

# Reels in Code

The whole edit lives in one text file: `remotion/public/edit.json`. Every caption page, every cut, every sound is a line in it. Remotion turns that file into the video. You (Claude) change the file when the creator gives notes, exactly like an editor would change a timeline.

Works with any footage (phone, camera, screen recording, AI avatar) and any voice-over (their own voice, any text-to-speech).

## Before anything: read the rules

Open `RULES.md` in the project root and follow it. It holds the creator's own preferences, collected from earlier notes. Rules there beat the defaults in this skill.

## The loop

1. **Script** (see "Script shape" below). Write it as `script.txt`, one on-screen page per line.
2. **Record / generate** the voice-over or talking-head video. Any tool.
3. **Time every word:**
   `python tools/timings.py talking_head.mp4 words.json`
4. **Build the edit file:**
   `python tools/build_edit.py --script script.txt --words words.json --video talking_head.mp4`
   (or `--audio voice.mp3` for type on black, or both for voice-over over footage)
5. **Preview:** `cd remotion && npx remotion studio` or a still: `npx remotion still src/index.ts Reel out/check.png --frame=120 --props=public/edit.json`. Look at the stills yourself before showing the creator.
6. **Notes → edits.** The creator says things like "the captions cover my chin" or "show the screen recording when I say dashboard". Change `edit.json` (or a component, if the note is about the look) and show the result.
7. **Notes → rules.** If a note is a preference that should apply to every future video (not just this one), add it to `RULES.md` as one short line, in the creator's words. Next video starts with everything they already taught you.
8. **Render:** `cd remotion && npx remotion render src/index.ts Reel out/reel.mp4 --props=public/edit.json`
   Sharper upload (1440×2560): add `--scale=2`, then downscale:
   `npx remotion ffmpeg -i out/reel.mp4 -vf scale=1440:2560:flags=lanczos -c:v libx264 -crf 16 -c:a copy out/reel_2k.mp4`

## Working rules

- Keep the creator's words. Tighten for speaking, don't rewrite their voice.
- Change only what the note asks for. If a fix needs a trade-off, say so in one line.
- Never put facts on screen that you haven't confirmed with the creator.
- Never cover the speaker's face with text. The type sits low, over the black gradient.
- Keep every render as a numbered draft (`draft_v1`, `draft_v2`, ...). Don't overwrite or delete their files.

## Script shape (feeds, not films)

The classic arc (setup → build-up → climax → wrap-up) loses people on a feed: they swipe during the setup and leave during the wrap-up. Instead:

- **Payoff first.** Open with the result or the boldest claim, in the first 2 seconds.
- **Hint every payoff** before it lands ("I'll show you how, and at the end…").
- **But / therefore,** never "and then". Each line should turn or push the previous one.
- **No gap after a payoff** — the next hook starts right away.
- **One peak, late.** The strongest line sits near the end.
- **No recap.** Don't summarise what they just watched.
- **Loop ending.** The last line should run straight back into the first one.
- **A reason to send it** (useful, surprising, or a "send this to…" moment). Only real ones.

## The edit file

```jsonc
{
  "fps": 30, "width": 1080, "height": 1920, "durationInFrames": 1650,
  "audio": "voice.mp3",                  // optional; otherwise the video's own sound plays
  "music": { "src": "bed.mp3", "volume": 0.08 },   // optional
  "overlay": { "from": 0.58, "strength": 0.95 },  // black gradient: where it starts, how dark
  "scenes": [
    { "start": 0, "dur": 9.2, "kind": "speaker", "src": "talking_head.mp4" },
    { "start": 9.2, "dur": 3.1, "kind": "inset", "src": "screen.mp4", "from": 4.0, "label": "BEFORE",
      "inset": { "left": 240, "top": 210, "w": 600, "h": 1067 } },
    { "start": 12.3, "dur": 6, "kind": "speaker", "src": "talking_head.mp4", "from": 12.3,
      "mask": "talking_head_mask.webm", "maskWord": { "text": "SYSTEM", "at": 15.8 } }
  ],
  "pages": [
    { "before": [{"w":"this","s":0.0}, ...], "key": [{"w":"editing","s":1.9},{"w":"app.","s":2.3}],
      "after": [], "start": 0.0, "end": 2.9, "edge": "left" }
  ]
}
```

- Times are seconds from the start of the reel. `from` is where to start inside a source clip.
- When a speaker clip continues after a cut-in, set its `from` to the cut-in's end time so the lips stay in sync.
- Scenes may overlap; later ones draw on top.
- Each word in a page has its spoken time `s`; it fades in at that moment.
- Media files go in `remotion/public/`.

## The look (Style C)

- One typeface, Inter Tight. Keyword weight 900, small words 600 (skip a weight so the contrast is obvious).
- Small words are 1/3 of the keyword size, stacked above or below the keyword, aligned to one edge (`edge` alternates left/right page to page).
- White only. Each word fades from 0 to 100% as it's said; unsaid words are invisible but keep their space so nothing jumps.
- Black gradient over the bottom ~40% so the type always reads.
- Long keywords shrink automatically to fit the width.
- **Word behind the speaker** (use once per video, on the peak line): run `python tools/matte.py remotion/public/clip.mp4 remotion/public/clip_mask.webm`, then add `mask` + `maskWord` to that scene. The word is drawn between the footage and the cut-out, so their head overlaps it.
- Components live in `remotion/src/style/StyleC.tsx`; change the look there.

## Picking keywords

The keyword is the one word a viewer would remember from that line: the noun or verb that carries the meaning ("code", "system", "free"), or a short phrase ("editing app."). Keep pages to about 6 words. Put the keyword where it's said, so the big word lands on the beat.
