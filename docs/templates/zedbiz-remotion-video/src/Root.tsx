import React from 'react';
import {Composition} from 'remotion';
import {ZedBizVideo} from './Video';
import type {ZedBizVideoProps} from './types';

const defaultProps: ZedBizVideoProps = {
  width: 1080,
  height: 1920,
  fps: 30,
  backgroundColor: '#101820',
  scenes: [
    {type: 'color', durationInFrames: 90, backgroundColor: '#101820'},
  ],
  captions: [
    {startFrame: 10, endFrame: 80, text: 'ZedBiz video production'},
  ],
  musicVolume: 0.12,
  logoPosition: 'top-right',
  captionAccentColor: '#f4b400',
  captionTextColor: '#ffffff',
  captionBackgroundColor: 'rgba(0, 0, 0, 0.72)',
};

export const RemotionRoot: React.FC = () => {
  return (
    <Composition
      id="ZedBizVideo"
      component={ZedBizVideo}
      durationInFrames={90}
      fps={30}
      width={1080}
      height={1920}
      defaultProps={defaultProps}
      calculateMetadata={({props}) => {
        const durationInFrames = Math.max(
          1,
          props.scenes.reduce((sum, scene) => sum + scene.durationInFrames, 0),
          ...props.captions.map((caption) => caption.endFrame),
        );
        return {
          durationInFrames,
          fps: props.fps,
          width: props.width,
          height: props.height,
        };
      }}
    />
  );
};
