import React from "react";
import { AbsoluteFill, Audio, Img, OffthreadVideo, Sequence, staticFile, useCurrentFrame, useVideoConfig } from "remotion";
import { BlackOverlay, Lockup, MaskWord, Page, TYPE } from "./style/StyleC";

/*
  The whole edit lives in public/edit.json. This component just draws it.

  scene kinds
    "speaker"  full-screen video (a talking head, any footage)
    "inset"    a smaller video or image window on black (screen recordings, other clips)
    "black"    plain black (type only)
  optional on any scene
    mask + maskWord   a giant word behind the person (mask = alpha video made by the skill's tools/matte.py)
*/

export type Scene = {
  start: number; // seconds into the reel
  dur: number;
  kind: "speaker" | "inset" | "black";
  src?: string; // file in public/ (video .mp4/.mov/.webm, or image .jpg/.png for "inset")
  from?: number; // seconds into the source clip to start at
  muted?: boolean; // default true: the reel's sound comes from "audio"
  inset?: { left: number; top: number; w: number; h: number };
  label?: string; // small caption above an inset, e.g. "BEFORE"
  mask?: string; // alpha video of the person, same timing as src
  maskWord?: { text: string; at: number };
};

export type EditProps = {
  fps: number;
  width: number;
  height: number;
  durationInFrames: number;
  audio?: string; // voice-over / mixed track in public/
  music?: { src: string; volume: number };
  overlay?: { from: number; strength: number };
  captions?: { top: number; size: number }; // vertical centre of the type (of 1920) and max keyword size
  scenes: Scene[];
  pages: Page[];
};

const isImage = (s: string) => /\.(png|jpe?g|webp)$/i.test(s);

const Media: React.FC<{ src: string; from?: number; muted?: boolean; transparent?: boolean }> = ({ src, from = 0, muted = true, transparent }) => {
  const { fps } = useVideoConfig();
  const style: React.CSSProperties = { width: "100%", height: "100%", objectFit: "cover" };
  if (isImage(src)) return <Img src={staticFile(src)} style={style} />;
  return <OffthreadVideo src={staticFile(src)} startFrom={Math.round(from * fps)} muted={muted} transparent={transparent} style={style} />;
};

const SceneView: React.FC<{ sc: Scene; t: number }> = ({ sc, t }) => {
  const box = sc.inset ?? { left: 240, top: 210, w: 600, h: 1067 };
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {sc.kind === "speaker" && sc.src && <Media src={sc.src} from={sc.from} muted={sc.muted ?? true} />}
      {sc.kind === "inset" && sc.src && (
        <>
          {sc.label && (
            <div style={{ position: "absolute", left: box.left, top: box.top - 60, width: box.w, textAlign: "center", fontFamily: TYPE,
              fontWeight: 600, fontSize: 30, letterSpacing: "0.12em", color: "rgba(255,255,255,0.7)" }}>{sc.label}</div>
          )}
          <div style={{ position: "absolute", left: box.left, top: box.top, width: box.w, height: box.h, overflow: "hidden", borderRadius: 18,
            boxShadow: "0 30px 80px rgba(0,0,0,0.6)" }}>
            <Media src={sc.src} from={sc.from} muted={sc.muted ?? true} />
          </div>
        </>
      )}
      {sc.mask && sc.maskWord && (
        <>
          <MaskWord text={sc.maskWord.text} at={sc.maskWord.at} t={t} />
          <AbsoluteFill><Media src={sc.mask} from={sc.from} transparent /></AbsoluteFill>
        </>
      )}
    </AbsoluteFill>
  );
};

export const Reel: React.FC<EditProps> = ({ scenes, pages, audio, music, overlay, captions }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const t = frame / fps;
  const page = pages.find((p) => t >= p.start - 0.06 && t < p.end);
  return (
    <AbsoluteFill style={{ background: "#000" }}>
      {scenes.map((sc, i) => (
        <Sequence key={i} from={Math.round(sc.start * fps)} durationInFrames={Math.max(1, Math.round(sc.dur * fps))} layout="none">
          <SceneView sc={sc} t={t} />
        </Sequence>
      ))}
      <BlackOverlay from={overlay?.from} strength={overlay?.strength} />
      {page && <Lockup key={page.start} p={page} t={t} y={captions?.top} base={captions?.size} />}
      {audio && <Audio src={staticFile(audio)} />}
      {music && <Audio src={staticFile(music.src)} volume={music.volume} loop />}
    </AbsoluteFill>
  );
};
