import { useState, useEffect } from 'react';
import '../styles/Avatar.css';

/**
 * Avatar component that displays Coda's avatar with speaking animation
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 */
function Avatar({ events }) {
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    // Get the latest event
    const latestEvent = events[0];
    
    // Update speaking state based on TTS events
    if (latestEvent.type === 'tts_start') {
      setIsSpeaking(true);
    } else if (latestEvent.type === 'tts_result' || latestEvent.type === 'tts_error') {
      setIsSpeaking(false);
    }
  }, [events]);
  
  return (
    <div className="avatar-container">
      <div className={`avatar ${isSpeaking ? 'speaking' : ''}`}>
        <div className="avatar-image">
          <svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
            <circle cx="50" cy="50" r="45" fill="#3a86ff" />
            <circle cx="50" cy="50" r="35" fill="#ffffff" />
            <circle cx="50" cy="50" r="25" fill="#3a86ff" />
          </svg>
        </div>
        
        {isSpeaking && (
          <div className="pulse-rings">
            <div className="ring ring-1"></div>
            <div className="ring ring-2"></div>
            <div className="ring ring-3"></div>
          </div>
        )}
      </div>
      <div className="avatar-status">
        {isSpeaking ? 'Speaking...' : 'Listening'}
      </div>
    </div>
  );
}

export default Avatar;
