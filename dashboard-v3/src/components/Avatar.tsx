import React, { memo, useEffect, useState } from 'react';

interface AvatarProps {
  mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';
}

const Avatar: React.FC<AvatarProps> = ({ mode, emotion }) => {
  // State for animation transition
  const [animationClass, setAnimationClass] = useState('');
  const [isTransitioning, setIsTransitioning] = useState(false);

  // Get the appropriate colors based on mode and emotion
  const getColors = () => {
    // Base colors for each mode
    const modeColors = {
      idle: {
        bg: 'bg-blue-500',
        ring: 'ring-blue-300',
        shadow: 'shadow-blue-500/50'
      },
      listening: {
        bg: 'bg-green-500',
        ring: 'ring-green-300',
        shadow: 'shadow-green-500/50'
      },
      thinking: {
        bg: 'bg-purple-500',
        ring: 'ring-purple-300',
        shadow: 'shadow-purple-500/50'
      },
      speaking: {
        bg: 'bg-yellow-500',
        ring: 'ring-yellow-300',
        shadow: 'shadow-yellow-500/50'
      },
      error: {
        bg: 'bg-red-500',
        ring: 'ring-red-300',
        shadow: 'shadow-red-500/50'
      }
    };

    // Emotion modifiers (subtle variations)
    const emotionModifiers = {
      neutral: '',
      playful: 'brightness-110',
      supportive: 'brightness-105',
      concerned: 'brightness-95',
      witty: 'brightness-105',
      focused: 'brightness-90'
    };

    const currentMode = modeColors[mode] || modeColors.idle;
    const emotionModifier = emotionModifiers[emotion] || '';

    return {
      ...currentMode,
      emotionModifier
    };
  };

  // Get the appropriate animation based on mode
  const getAnimation = () => {
    switch (mode) {
      case 'idle':
        return 'animate-pulse-very-slow';
      case 'listening':
        return 'animate-pulse';
      case 'thinking':
        return 'animate-pulse-slow';
      case 'speaking':
        return 'animate-bounce-slow';
      case 'error':
        return 'animate-shake';
      default:
        return 'animate-pulse-very-slow';
    }
  };

  // Get the icon based on mode
  const getIcon = () => {
    switch (mode) {
      case 'idle':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        );
      case 'listening':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 11c0 3.517-1.009 6.799-2.753 9.571m-3.44-2.04l.054-.09A13.916 13.916 0 008 11a4 4 0 118 0c0 1.017-.07 2.019-.203 3m-2.118 6.844A21.88 21.88 0 0015.171 17m3.839 1.132c.645-2.266.99-4.659.99-7.132A8 8 0 008 4.07M3 15.364c.64-1.319 1-2.8 1-4.364 0-1.457.39-2.823 1.07-4" />
          </svg>
        );
      case 'thinking':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
          </svg>
        );
      case 'speaking':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
        );
      case 'error':
        return (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
          </svg>
        );
      default:
        return <span className="text-4xl">C</span>;
    }
  };

  // Get the status text based on mode and emotion
  const getStatusText = () => {
    const modeText = {
      idle: 'Ready',
      listening: 'Listening...',
      thinking: 'Thinking...',
      speaking: 'Speaking...',
      error: 'Error'
    };

    const emotionText = {
      neutral: '',
      playful: 'feeling playful',
      supportive: 'being supportive',
      concerned: 'showing concern',
      witty: 'being witty',
      focused: 'staying focused'
    };

    return {
      mode: modeText[mode] || 'Ready',
      emotion: emotionText[emotion] || ''
    };
  };

  // Handle animation transitions when mode changes
  useEffect(() => {
    setIsTransitioning(true);
    setAnimationClass('scale-110');

    const timer = setTimeout(() => {
      setAnimationClass(getAnimation());
      setIsTransitioning(false);
    }, 300);

    return () => clearTimeout(timer);
  }, [mode]);

  const colors = getColors();
  const statusText = getStatusText();

  return (
    <div className="flex flex-col items-center">
      <div className="relative">
        {/* Outer ring/glow effect */}
        <div className={`absolute inset-0 ${colors.ring} rounded-full blur-md transition-all duration-500 ${isTransitioning ? 'scale-125 opacity-70' : 'scale-110 opacity-50'}`}></div>

        {/* Main avatar circle */}
        <div
          className={`
            ${colors.bg}
            ${animationClass}
            ${colors.emotionModifier}
            rounded-full w-32 h-32
            flex items-center justify-center
            text-white
            shadow-lg ${colors.shadow}
            transition-all duration-300
            ring-2 ${colors.ring}
            z-10 relative
          `}
        >
          {getIcon()}
        </div>

        {/* Mode indicator dots */}
        <div className="absolute -bottom-1 left-1/2 transform -translate-x-1/2 flex space-x-1">
          <div className={`w-2 h-2 rounded-full ${mode === 'idle' ? 'bg-blue-500' : 'bg-gray-600'}`}></div>
          <div className={`w-2 h-2 rounded-full ${mode === 'listening' ? 'bg-green-500' : 'bg-gray-600'}`}></div>
          <div className={`w-2 h-2 rounded-full ${mode === 'thinking' ? 'bg-purple-500' : 'bg-gray-600'}`}></div>
          <div className={`w-2 h-2 rounded-full ${mode === 'speaking' ? 'bg-yellow-500' : 'bg-gray-600'}`}></div>
        </div>
      </div>

      <div className="mt-6 text-center">
        <div className="text-lg font-medium text-white">
          {statusText.mode}
        </div>
        {statusText.emotion && (
          <div className="text-sm text-gray-300 mt-1">
            {statusText.emotion}
          </div>
        )}
      </div>
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(Avatar);
