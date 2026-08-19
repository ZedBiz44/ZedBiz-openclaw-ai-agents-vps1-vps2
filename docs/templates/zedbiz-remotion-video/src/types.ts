export type Scene = {
  type: 'color' | 'image' | 'video';
  durationInFrames: number;
  src?: string;
  backgroundColor?: string;
  fit?: 'cover' | 'contain';
  volume?: number;
};

export type Caption = {
  startFrame: number;
  endFrame: number;
  text: string;
};

export type ZedBizVideoProps = {
  width: number;
  height: number;
  fps: number;
  backgroundColor: string;
  scenes: Scene[];
  captions: Caption[];
  voiceoverSrc?: string;
  musicSrc?: string;
  musicVolume?: number;
  logoSrc?: string;
  logoPosition?: 'top-left' | 'top-right' | 'bottom-left' | 'bottom-right';
  captionAccentColor?: string;
  captionTextColor?: string;
  captionBackgroundColor?: string;
};
