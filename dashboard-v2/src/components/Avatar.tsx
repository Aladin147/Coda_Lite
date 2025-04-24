import React from 'react';
import { useCodaMode } from '../store/selectors';

/**
 * Simplified Avatar component with no event handling or state updates
 */
const Avatar: React.FC = () => {
  const { mode, emotionContext } = useCodaMode();

  // Simple static avatar with no state updates
  return (
    <div className="flex flex-col items-center">
      <div className="avatar bg-blue-500 rounded-full w-24 h-24 flex items-center justify-center text-white">
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
