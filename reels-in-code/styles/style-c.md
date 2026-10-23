# Style C (default)

Typographic and clean: footage full screen, a black gradient low, and big keyword captions that fade in word by word.

- One typeface, Inter Tight. Keyword weight 900, small words 600 (skip a weight so the contrast is obvious).
- Small words are 1/3 of the keyword size, stacked above or below the keyword, aligned to one edge (`edge` alternates left/right page to page).
- White only. Each word fades from 0 to 100% as it's said; unsaid words are invisible but keep their space so nothing jumps.
- Black gradient over the bottom ~40% so the type always reads.
- Long keywords shrink automatically to fit the width.
- **Word behind the speaker** (use once per video, on the peak line): run `python <skill>/tools/matte.py public/clip.mp4 public/clip_mask.webm`, then add `mask` + `maskWord` to that scene. The word is drawn between the footage and the cut-out, so their head overlaps it.
- Components live in `remotion/src/style/StyleC.tsx`; change the look there.

## Picking keywords

The keyword is the one word a viewer would remember from that line: the noun or verb that carries the meaning ("code", "system", "free"), or a short phrase ("editing app."). Keep pages to about 6 words. Put the keyword where it's said, so the big word lands on the beat.

## Adding another style

When a creator wants a different look, write `styles/<name>.md` the same way (typeface, weights, sizes, colours, caption behaviour, overlays, what never to do) and implement it as a new file in the project's `src/style/`, swapping it in `src/Reel.tsx`. Keep Style C untouched so it stays available.
