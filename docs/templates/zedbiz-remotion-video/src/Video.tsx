import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Img,
  OffthreadVideo,
  Sequence,
  interpolate,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';
import type {Caption, Scene, ZedBizVideoProps} from './types';

const resolveAsset = (src: string): string => {
  if (/^(https?:|data:|file:)/i.test(src)) return src;
  return staticFile(src.replace(/^\/+/, ''));
};

const sceneStarts = (scenes: Scene[]): number[] => {
  let cursor = 0;
  return scenes.map((scene) => {
    const start = cursor;
    cursor += scene.durationInFrames;
    return start;
  });
};

const CaptionLayer: React.FC<{
  captions: Caption[];
  accent: string;
  color: string;
  background: string;
}> = ({captions, accent, color, background}) => {
  const frame = useCurrentFrame();
  const active = captions.find(
    (caption) => frame >= caption.startFrame && frame < caption.endFrame,
  );
  if (!active) return null;

  const opacity = interpolate(
    frame,
    [active.startFrame, active.startFrame + 4, active.endFrame - 4, active.endFrame],
    [0, 1, 1, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );
  const rise = interpolate(
    frame,
    [active.startFrame, active.startFrame + 6],
    [24, 0],
    {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'},
  );

  return (
    <AbsoluteFill style={{justifyContent: 'flex-end', alignItems: 'center'}}>
      <div
        style={{
          marginBottom: '11%',
          maxWidth: '86%',
          padding: '22px 34px',
          borderRadius: 22,
          borderLeft: `10px solid ${accent}`,
          background,
          color,
          fontFamily: 'Arial, Helvetica, sans-serif',
          fontSize: 58,
          fontWeight: 800,
          lineHeight: 1.08,
          textAlign: 'center',
          boxShadow: '0 12px 36px rgba(0,0,0,0.34)',
          opacity,
          transform: `translateY(${rise}px)`,
        }}
      >
        {active.text}
      </div>
    </AbsoluteFill>
  );
};

const logoStyle = (position: NonNullable<ZedBizVideoProps['logoPosition']>) => {
  const vertical = position.startsWith('top') ? {top: 44} : {bottom: 44};
  const horizontal = position.endsWith('left') ? {left: 44} : {right: 44};
  return {...vertical, ...horizontal};
};

export const ZedBizVideo: React.FC<ZedBizVideoProps> = (props) => {
  const {width} = useVideoConfig();
  const starts = sceneStarts(props.scenes);

  return (
    <AbsoluteFill style={{backgroundColor: props.backgroundColor}}>
      {props.scenes.map((scene, index) => (
        <Sequence
          key={`${index}-${scene.src ?? scene.backgroundColor ?? scene.type}`}
          from={starts[index]}
          durationInFrames={scene.durationInFrames}
        >
          <AbsoluteFill
            style={{backgroundColor: scene.backgroundColor ?? props.backgroundColor}}
          >
            {scene.type === 'image' && scene.src ? (
              <Img
                src={resolveAsset(scene.src)}
                style={{width: '100%', height: '100%', objectFit: scene.fit ?? 'cover'}}
              />
            ) : null}
            {scene.type === 'video' && scene.src ? (
              <OffthreadVideo
                src={resolveAsset(scene.src)}
                volume={scene.volume ?? 0}
                style={{width: '100%', height: '100%', objectFit: scene.fit ?? 'cover'}}
              />
            ) : null}
          </AbsoluteFill>
        </Sequence>
      ))}

      {props.voiceoverSrc ? <Audio src={resolveAsset(props.voiceoverSrc)} /> : null}
      {props.musicSrc ? (
        <Audio src={resolveAsset(props.musicSrc)} volume={props.musicVolume ?? 0.12} loop />
      ) : null}

      {props.logoSrc ? (
        <Img
          src={resolveAsset(props.logoSrc)}
          style={{
            position: 'absolute',
            width: Math.round(width * 0.18),
            height: 'auto',
            ...logoStyle(props.logoPosition ?? 'top-right'),
          }}
        />
      ) : null}

      <CaptionLayer
        captions={props.captions}
        accent={props.captionAccentColor ?? '#f4b400'}
        color={props.captionTextColor ?? '#ffffff'}
        background={props.captionBackgroundColor ?? 'rgba(0,0,0,0.72)'}
      />
    </AbsoluteFill>
  );
};
