import { useState, useEffect } from 'react';
import '../styles/VoiceControls.css';

/**
 * VoiceControls component that provides push-to-talk, text input, and demo functionality
 * @param {Object} props - Component props
 * @param {Function} props.sendMessage - Function to send WebSocket messages
 * @param {boolean} props.connected - Whether the WebSocket is connected
 */
function VoiceControls({ sendMessage, connected }) {
  const [isPushingToTalk, setIsPushingToTalk] = useState(false);
  const [textInput, setTextInput] = useState('');
  const [showTextInput, setShowTextInput] = useState(false);

  // Use effect to add global event listeners to prevent scrolling
  useEffect(() => {
    // Function to prevent default behavior for all touch events when PTT is active
    const preventDefaultForTouch = (e) => {
      if (isPushingToTalk) {
        e.preventDefault();
      }
    };

    // Add event listeners
    document.addEventListener('touchmove', preventDefaultForTouch, { passive: false });
    document.addEventListener('touchstart', preventDefaultForTouch, { passive: false });
    document.addEventListener('touchend', preventDefaultForTouch, { passive: false });

    // Add/remove ptt-active class to body
    if (isPushingToTalk) {
      document.body.classList.add('ptt-active');
    } else {
      document.body.classList.remove('ptt-active');
    }

    // Clean up event listeners on unmount
    return () => {
      document.removeEventListener('touchmove', preventDefaultForTouch);
      document.removeEventListener('touchstart', preventDefaultForTouch);
      document.removeEventListener('touchend', preventDefaultForTouch);
      document.body.classList.remove('ptt-active');
    };
  }, [isPushingToTalk]);

  const handlePushToTalk = (event) => {
    // Prevent default behavior to stop scrolling
    if (event) event.preventDefault();
    event.stopPropagation();

    if (!connected) return;

    setIsPushingToTalk(true);
    sendMessage('stt_start', { mode: 'push_to_talk' });
  };

  const handleStopListening = (event) => {
    // Prevent default behavior to stop scrolling
    if (event) {
      event.preventDefault();
      event.stopPropagation();
    }

    if (!connected) return;

    setIsPushingToTalk(false);
    sendMessage('stt_stop', {});
  };

  const handleDemoFlow = (event) => {
    if (event) event.preventDefault();

    if (!connected) return;

    sendMessage('demo_flow', {});
  };

  const handleTextInputChange = (event) => {
    setTextInput(event.target.value);
  };

  const handleTextInputSubmit = (event) => {
    event.preventDefault();

    if (!connected || !textInput.trim()) return;

    // Send the text input as a direct message
    sendMessage('text_input', { text: textInput.trim() });

    // Clear the input field
    setTextInput('');
  };

  const toggleTextInput = () => {
    setShowTextInput(!showTextInput);
  };

  return (
    <>
      {/* Fixed position push-to-talk button */}
      <button
        className={`push-to-talk-btn ${isPushingToTalk ? 'active' : ''} ${!connected ? 'disabled' : ''}`}
        onMouseDown={handlePushToTalk}
        onMouseUp={handleStopListening}
        onMouseLeave={isPushingToTalk ? handleStopListening : undefined}
        onTouchStart={handlePushToTalk}
        onTouchEnd={handleStopListening}
        onTouchMove={(e) => e.preventDefault()}
        disabled={!connected}
      >
        {isPushingToTalk ? 'Listening...' : 'Push to Talk'}
      </button>

      <div className="voice-controls">
        <div className="input-controls">
          {/* Placeholder for the push-to-talk button to maintain layout */}
          <div className="push-to-talk-placeholder"></div>

          <button
            className={`text-input-toggle ${showTextInput ? 'active' : ''}`}
            onClick={toggleTextInput}
          >
            {showTextInput ? 'Hide Text Input' : 'Show Text Input'}
          </button>

          <button
            className={`demo-btn ${!connected ? 'disabled' : ''}`}
            onClick={handleDemoFlow}
            disabled={!connected}
          >
            Run Demo Flow
          </button>
        </div>

        {showTextInput && (
          <form className="text-input-form" onSubmit={handleTextInputSubmit}>
            <input
              type="text"
              value={textInput}
              onChange={handleTextInputChange}
              placeholder="Type your message here..."
              disabled={!connected}
              className={!connected ? 'disabled' : ''}
            />
            <button
              type="submit"
              disabled={!connected || !textInput.trim()}
              className={!connected || !textInput.trim() ? 'disabled' : ''}
            >
              Send
            </button>
          </form>
        )}

        <div className="controls-help">
          {connected ? (
            <p>{showTextInput ? 'Type your message or use Push to Talk' : 'Hold the Push to Talk button while speaking'}</p>
          ) : (
            <p>Connect to Coda to enable controls</p>
          )}
        </div>
      </div>
    </>
  );
}

export default VoiceControls;
