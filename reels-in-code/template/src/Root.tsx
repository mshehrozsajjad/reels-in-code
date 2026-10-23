import React from "react";
import { Composition } from "remotion";
import { Reel, EditProps } from "./Reel";
import demo from "../public/edit.json";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Reel"
    component={Reel as any}
    defaultProps={demo as unknown as EditProps}
    durationInFrames={60}
    fps={30}
    width={1080}
    height={1920}
    calculateMetadata={({ props }: { props: any }) => ({
      durationInFrames: props.durationInFrames,
      fps: props.fps,
      width: props.width,
      height: props.height,
    })}
  />
);
