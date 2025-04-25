import React from 'react';
import { useCodaMode } from '../../store/selectors';

/**
 * Avatar component that displays Coda's avatar with animations based on mode and emotion
 */
const Avatar: React.FC = () => {
  const { mode, emotionContext } = useCodaMode();
  
  // Determine the avatar color based on the emotion context
  const getAvatarColor = () => {
    switch (emotionContext) {
      case 'playful':
        return 'bg-warning';
      case 'supportive':
        return 'bg-success';
      case 'concerned':
        return 'bg-danger';
      case 'witty':
        return 'bg-secondary';
      case 'focused':
        return 'bg-primary-dark';
      default:
        return 'bg-primary';
    }
  };
  
  // Determine the animation based on the mode
  const getAnimation = () => {
    switch (mode) {
      case 'listening':
        return 'animate-pulse';
      case 'thinking':
        return 'animate-pulse-slow';
      case 'speaking':
        return 'animate-none';
      case 'error':
        return 'animate-none';
      default:
        return 'animate-breathe';
    }
  };
  
  return (
    <div className="flex flex-col items-center justify-center p-4">
      <div className="relative w-32 h-32">
        {/* Avatar core */}
        <div 
          className={`absolute inset-0 rounded-full ${getAvatarColor()} ${getAnimation()} shadow-lg`}
        ></div>
        
        {/* Voice visualization (only visible when speaking) */}
        {mode === 'speaking' && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="flex gap-1">
              {[...Array(5)].map((_, i) => (
                <div 
                  key={i}
                  className="w-1 bg-white rounded-full animate-wave"
                  style={{ 
                    height: '40%', 
                    animationDelay: `${i * 0.1}s`,
                    opacity: 0.7
                  }}
                ></div>
              ))}
            </div>
          </div>
        )}
        
        {/* Mood ring */}
        <div 
          className={`absolute -inset-2 rounded-full ${getAvatarColor()} opacity-20 ${getAnimation()}`}
        ></div>
      </div>
      
      <div className="mt-4 text-center">
        <div className="font-bold">{mode.charAt(0).toUpperCase() + mode.slice(1)}</div>
        <div className="text-sm text-text-secondary">{emotionContext}</div>
      </div>
    </div>
  );
};

export default Avatar;
