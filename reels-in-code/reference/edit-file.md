# The edit file: public/edit.json

```jsonc
{
  "fps": 30, "width": 1080, "height": 1920, "durationInFrames": 1650,
  "audio": "voice.mp3",                  // optional; otherwise the video's own sound plays
  "music": { "src": "bed.mp3", "volume": 0.08 },   // optional
  "overlay": { "from": 0.58, "strength": 0.95 },  // black gradient: where it starts, how dark
  "captions": { "top": 1565, "size": 178 },        // where the type sits (of 1920) and the max keyword size
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
- When a talking clip continues after a cut-in, its `from` = (cut-in end) − (when that clip first started on the reel), so lips stay in sync.
- Scenes may overlap; later ones draw on top.
- Each word in a page has its spoken time `s`; it fades in at that moment.
- Media files go in `public/`.

- Sound: `audio` plays one track for the whole reel (a voice-over or a mixed file). With several talking clips and no separate voice-over, set `"muted": false` on each talking scene so its own sound plays.
- Pages: `edge` alternates "right"/"left" page to page. A page shows from `start` until `end` (normally the next page's start).
- Long keywords shrink automatically to fit the width.

## Common edits

| Note | Change |
|------|--------|
| "captions too high / covering my chin" | `captions.top` up (e.g. 1565 → 1620) |
| "text too big" | `captions.size` down |
| "gradient too dark" | `overlay.strength` down, or `overlay.from` up |
| "show the screen recording when I say X" | add an `inset` scene starting at X's time |
| "cut the pause after line 3" | shift every later scene and page time back by the pause length (and `from` for clips that continue) |
| "big word behind me on 'system'" | run matte.py on that clip, add `mask` + `maskWord` at the word's time |
