// Owner: Member D (WBS 5.1.2) — HTML5 video player exposing seek() to the timeline.
// TODO(D, 5.1.2): handle loading/error states; keyboard shortcuts; keep direction LTR in Arabic.
import { forwardRef, useImperativeHandle, useRef } from "react";

export interface VideoPlayerHandle {
  seek: (seconds: number) => void;
}

export interface VideoPlayerProps {
  src: string;
  onTimeUpdate?: (seconds: number) => void;
}

export const VideoPlayer = forwardRef<VideoPlayerHandle, VideoPlayerProps>(function VideoPlayer(
  { src, onTimeUpdate }, ref,
) {
  const video = useRef<HTMLVideoElement>(null);
  useImperativeHandle(ref, () => ({
    seek: (s: number) => {
      if (video.current) video.current.currentTime = s;
    },
  }));
  return (
    <div className="video-player">
      <video ref={video} src={src} controls width="100%"
        onTimeUpdate={(e) => onTimeUpdate?.(e.currentTarget.currentTime)} />
    </div>
  );
});
