import React, { memo } from 'react';

interface AvatarProps {
  mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';
}

const Avatar: React.FC<AvatarProps> = ({ mode, emotion }) => {
  // Get the appropriate background color based on mode
  const getBgColor = () => {
    switch (mode) {
      case 'idle':
        return 'bg-blue-500';
      case 'listening':
        return 'bg-green-500';
      case 'thinking':
        return 'bg-purple-500';
      case 'speaking':
        return 'bg-yellow-500';
      case 'error':
        return 'bg-red-500';
      default:
        return 'bg-blue-500';
    }
  };

  // Get the appropriate animation based on mode
  const getAnimation = () => {
    switch (mode) {
      case 'idle':
        return '';
      case 'listening':
        return 'animate-pulse';
      case 'thinking':
        return 'animate-pulse-slow';
      case 'speaking':
        return 'animate-bounce-slow';
      case 'error':
        return '';
      default:
        return '';
    }
  };

  return (
    <div className="flex flex-col items-center">
      <div 
        className={`${getBgColor()} ${getAnimation()} rounded-full w-24 h-24 flex items-center justify-center text-white`}
      >
        <span className="text-4xl">C</span>
      </div>
      <div className="mt-4 text-center">
        <div className="font-semibold">
          Mode: <span className="font-normal">{mode}</span>
        </div>
        <div className="font-semibold">
          Emotion: <span className="font-normal">{emotion}</span>
        </div>
      </div>
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(Avatar);
