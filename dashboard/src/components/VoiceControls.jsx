import { useState } from 'react';
import '../styles/VoiceControls.css';

/**
 * VoiceControls component that provides push-to-talk and demo functionality
 * @param {Object} props - Component props
 * @param {Function} props.sendMessage - Function to send WebSocket messages
 * @param {boolean} props.connected - Whether the WebSocket is connected
 */
function VoiceControls({ sendMessage, connected }) {
  const [isPushingToTalk, setIsPushingToTalk] = useState(false);
  
  const handlePushToTalk = () => {
    if (!connected) return;
    
    setIsPushingToTalk(true);
    sendMessage('stt_start', { mode: 'push_to_talk' });
  };
  
  const handleStopListening = () => {
    if (!connected) return;
    
    setIsPushingToTalk(false);
    sendMessage('stt_stop', {});
  };
  
  const handleDemoFlow = () => {
    if (!connected) return;
    
    sendMessage('demo_flow', {});
  };
  
  return (
    <div className="voice-controls">
      <button 
        className={`push-to-talk-btn ${isPushingToTalk ? 'active' : ''} ${!connected ? 'disabled' : ''}`}
        onMouseDown={handlePushToTalk}
        onMouseUp={handleStopListening}
        onMouseLeave={isPushingToTalk ? handleStopListening : undefined}
        onTouchStart={handlePushToTalk}
        onTouchEnd={handleStopListening}
        disabled={!connected}
      >
        {isPushingToTalk ? 'Listening...' : 'Push to Talk'}
      </button>
      
      <button 
        className={`demo-btn ${!connected ? 'disabled' : ''}`}
        onClick={handleDemoFlow}
        disabled={!connected}
      >
        Run Demo Flow
      </button>
      
      <div className="controls-help">
        {connected ? (
          <p>Hold the Push to Talk button while speaking</p>
        ) : (
          <p>Connect to Coda to enable voice controls</p>
        )}
      </div>
    </div>
  );
}

export default VoiceControls;
