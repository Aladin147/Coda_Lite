import React, { useMemo } from 'react';
import { useCodaMode } from '../store/selectors';

const Avatar: React.FC = () => {
  const { mode, emotionContext } = useCodaMode();

  // Use useMemo to prevent unnecessary recalculations
  const avatarClass = useMemo(() => {
    let baseClass = 'avatar';

    // Add mode-specific class
    if (mode === 'listening') {
      return `${baseClass} avatar-listening`;
    } else if (mode === 'thinking') {
      return `${baseClass} avatar-thinking`;
    } else if (mode === 'speaking') {
      return `${baseClass} avatar-speaking`;
    } else if (mode === 'error') {
      return `${baseClass} avatar-error`;
    } else {
      return `${baseClass} avatar-idle`;
    }
  }, [mode]);

  return (
    <div className="flex flex-col items-center">
      <div className={avatarClass}>
        <span className="text-4xl">C</span>
      </div>
      <div className="mt-4 text-center">
        <div className="font-semibold">
          Mode: <span className="font-normal">{mode}</span>
        </div>
        <div className="font-semibold">
          Emotion: <span className="font-normal">{emotionContext}</span>
        </div>
      </div>
    </div>
  );
};

export default Avatar;
