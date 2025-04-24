import React, { useMemo } from 'react';
import { useCodaMode } from '../store/selectors';

const Avatar: React.FC = () => {
  const { mode, emotionContext } = useCodaMode();

  // Use useMemo to calculate avatar classes only when dependencies change
  const avatarClasses = useMemo(() => {
    let baseClass = 'avatar';

    // Add mode-specific class
    switch (mode) {
      case 'listening':
        baseClass += ' avatar-listening';
        break;
      case 'thinking':
        baseClass += ' avatar-thinking';
        break;
      case 'speaking':
        baseClass += ' avatar-speaking';
        break;
      case 'error':
        baseClass += ' avatar-error';
        break;
      default: // idle
        baseClass += ' avatar-idle';
        break;
    }

    // Add emotion-specific class if needed
    if (emotionContext === 'concerned' && mode === 'idle') {
      baseClass = baseClass.replace('avatar-idle', 'avatar-thinking');
    } else if (emotionContext === 'witty' && mode === 'idle') {
      baseClass = baseClass.replace('avatar-idle', 'avatar-speaking');
    } else if (emotionContext === 'playful' && mode === 'idle') {
      baseClass += ' animate-bounce';
    }

    return baseClass;
  }, [mode, emotionContext]);

  return (
    <div className="flex flex-col items-center">
      <div className={avatarClasses}>
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
