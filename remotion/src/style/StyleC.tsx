import React from "react";
import { AbsoluteFill, continueRender, delayRender, Easing, interpolate, staticFile } from "remotion";

/*
  Style C — typographic reels.
  One typeface (Inter Tight), two weights that skip a step (900 keyword / 600 small words),
  small words at 1/3 of the keyword size, white only, words fade in as they are spoken,
  a black gradient behind the type, and an optional giant word behind the speaker.
*/

export const TYPE = '"Inter Tight", "Helvetica Neue", Helvetica, Arial, sans-serif';

// Fonts ship in public/fonts (SIL Open Font License), so renders work offline.
if (typeof document !== "undefined") {
  const handle = delayRender("Inter Tight");
  Promise.all(
    (["600", "900"] as const).map((w) =>
      new FontFace("Inter Tight", `url(${staticFile(`fonts/InterTight-${w}.woff2`)}) format("woff2")`, { weight: w }).load().then((f) => document.fonts.add(f)),
    ),
  )
    .catch((e) => console.error(e))
    .finally(() => continueRender(handle));
}

export type Word = { w: string; s: number }; // word + time it is spoken (seconds from start of the reel)
export type Page = { before: Word[]; key: Word[]; after: Word[]; start: number; end: number; edge: "left" | "right" };

/** Black gradient over the lower part of the frame, where the type sits. */
export const BlackOverlay: React.FC<{ from?: number; strength?: number }> = ({ from = 0.58, strength = 0.95 }) => (
  <AbsoluteFill
    style={{
      background: `linear-gradient(180deg, rgba(0,0,0,0) ${from * 100}%, rgba(0,0,0,${strength * 0.75}) ${(from + 0.2) * 100}%, rgba(0,0,0,${strength}) 100%)`,
    }}
  />
);

/* ---- keyword size: shrink long keywords so the lockup always fits the width ---- */
let ctx: CanvasRenderingContext2D | null = null;
const measure = (s: string, weight: number, size: number) => {
  if (!ctx) ctx = document.createElement("canvas").getContext("2d");
  if (!ctx) return s.length * size * 0.55;
  ctx.font = `${weight} ${size}px ${TYPE}`;
  return ctx.measureText(s).width;
};
const join = (ws: Word[]) => ws.map((x) => x.w).join(" ");
export const fitSize = (p: Page, base = 178, maxW = 940) => {
  const kw = measure(join(p.key), 900, base);
  const sw = Math.max(p.before.length ? measure(join(p.before), 600, base / 3) : 0, p.after.length ? measure(join(p.after), 600, base / 3) : 0);
  return Math.floor(Math.min(base, (base * maxW) / Math.max(kw, 1), sw ? (base * maxW) / sw : base));
};

/** A line of words; each word fades from 0 to 100% opacity when it is spoken. Unspoken words keep their space. */
const Line: React.FC<{ ws: Word[]; t: number; size: number; weight: number; track: number }> = ({ ws, t, size, weight, track }) => (
  <div style={{ fontFamily: TYPE, fontWeight: weight, fontSize: size, letterSpacing: `${track}em`, lineHeight: 0.92, whiteSpace: "nowrap" }}>
    {ws.map((x, i) => (
      <span key={i} style={{ color: "#FFFFFF", opacity: interpolate(t, [x.s - 0.04, x.s + 0.16], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp" }) }}>
        {x.w}
        {i < ws.length - 1 ? " " : ""}
      </span>
    ))}
  </div>
);

/** Keyword lockup: small words above, one big keyword, small words below, aligned to one edge. */
export const Lockup: React.FC<{ p: Page; t: number; y?: number; base?: number }> = ({ p, t, y = 1565, base = 178 }) => {
  const size = fitSize(p, base);
  const small = Math.round(size / 3);
  const k = interpolate(t, [p.start - 0.06, p.start + 0.1], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  const side = { marginRight: p.edge === "right" ? size * 0.04 : 0, marginLeft: p.edge === "left" ? size * 0.05 : 0 };
  return (
    <div
      style={{
        position: "absolute", left: 540, top: y, width: "max-content",
        transform: `translate(-50%, -50%) translateY(${(1 - k) * 14}px)`,
        display: "flex", flexDirection: "column", alignItems: p.edge === "right" ? "flex-end" : "flex-start",
        textShadow: "0 3px 24px rgba(0,0,0,0.45)",
      }}
    >
      {p.before.length > 0 && <div style={{ ...side, marginBottom: size * 0.02 }}><Line ws={p.before} t={t} size={small} weight={600} track={-0.02} /></div>}
      <Line ws={p.key} t={t} size={size} weight={900} track={-0.045} />
      {p.after.length > 0 && <div style={{ ...side, marginTop: size * 0.04 }}><Line ws={p.after} t={t} size={small} weight={600} track={-0.02} /></div>}
    </div>
  );
};

/** Giant word placed BETWEEN the background and the speaker's cut-out (render the mask video on top of it). */
export const MaskWord: React.FC<{ text: string; at: number; t: number; top?: number; size?: number }> = ({ text, at, t, top = 300, size = 255 }) => {
  const k = interpolate(t, [at - 0.05, at + 0.2], [0, 1], { extrapolateLeft: "clamp", extrapolateRight: "clamp", easing: Easing.out(Easing.cubic) });
  return (
    <div
      style={{
        position: "absolute", left: 0, top, width: 1080, textAlign: "center",
        fontFamily: TYPE, fontWeight: 900, fontSize: size, letterSpacing: "-0.06em", lineHeight: 1,
        color: "#FFFFFF", opacity: k, transform: `scale(${1.08 - 0.08 * k})`,
      }}
    >
      {text}
    </div>
  );
};
