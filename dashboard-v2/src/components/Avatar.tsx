import React, { useMemo, useRef, useEffect, useState } from 'react';
import { useCodaMode, useEvents } from '../store/selectors';

const Avatar: React.FC = () => {
  const { mode, emotionContext } = useCodaMode();
  const { events } = useEvents();
  const [isSpeaking, setIsSpeaking] = useState(false);
  const lastHandledType = useRef<string | null>(null);

  // Process TTS events to update speaking state
  useEffect(() => {
    if (!events || events.length === 0) return;

    // Find the latest TTS-related event
    const latest = events.find(e =>
      e.type === 'tts_start' ||
      e.type === 'tts_result' ||
      e.type === 'tts_error'
    );

    // If no TTS event found, do nothing
    if (!latest) return;

    // If this event type is the same as the last one we processed, do nothing
    if (lastHandledType.current === latest.type) return;

    // Update our ref to track the last event type we processed
    lastHandledType.current = latest.type;

    // Update speaking state based on TTS events
    if (latest.type === 'tts_start') {
      setIsSpeaking(true);
    } else {
      setIsSpeaking(false);
    }
  }, [events]);

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
      <div className={`${avatarClasses} ${isSpeaking ? 'talking' : ''}`}>
        <span className="text-4xl">C</span>
      </div>
      <div className="mt-4 text-center">
        <div className="font-semibold">
          Mode: <span className="font-normal">{mode}</span>
        </div>
        <div className="font-semibold">
          Emotion: <span className="font-normal">{emotionContext}</span>
        </div>
        <div className="font-semibold">
          Status: <span className="font-normal">{isSpeaking ? 'Speaking' : 'Idle'}</span>
        </div>
      </div>
    </div>
  );
};

export default Avatar;
