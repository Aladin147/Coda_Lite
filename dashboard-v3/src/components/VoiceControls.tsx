import React, { useState, useCallback, memo } from 'react';

interface VoiceControlsProps {
  connected: boolean;
  onStartListening: () => void;
  onStopListening: () => void;
  onRunDemo: () => void;
}

const VoiceControls: React.FC<VoiceControlsProps> = ({
  connected,
  onStartListening,
  onStopListening,
  onRunDemo
}) => {
  const [isListening, setIsListening] = useState(false);

  // Start listening with memoized callback
  const handleMouseDown = useCallback(() => {
    if (!connected) return;
    
    setIsListening(true);
    onStartListening();
  }, [connected, onStartListening]);

  // Stop listening with memoized callback
  const handleMouseUp = useCallback(() => {
    if (!connected || !isListening) return;
    
    setIsListening(false);
    onStopListening();
  }, [connected, isListening, onStopListening]);

  // Handle mouse leave with memoized callback
  const handleMouseLeave = useCallback(() => {
    if (!connected || !isListening) return;
    
    setIsListening(false);
    onStopListening();
  }, [connected, isListening, onStopListening]);

  // Run demo with memoized callback
  const handleRunDemo = useCallback(() => {
    if (!connected) return;
    
    onRunDemo();
  }, [connected, onRunDemo]);

  return (
    <div className="card p-4">
      <h2 className="text-xl font-bold mb-4">Voice Controls</h2>

      <div className="space-y-4">
        <div className="bg-dark-600 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Push to Talk</h3>

          <button
            className={`w-full h-16 flex items-center justify-center rounded-lg transition-colors ${
              isListening
                ? 'bg-red-500 hover:bg-red-600'
                : 'bg-blue-500 hover:bg-blue-600'
            } ${!connected ? 'opacity-50 cursor-not-allowed' : ''}`}
            onMouseDown={handleMouseDown}
            onMouseUp={handleMouseUp}
            onMouseLeave={handleMouseLeave}
            disabled={!connected}
          >
            <span className="mr-2">
              {isListening ? 'Release to Stop' : 'Hold to Speak'}
            </span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-6 w-6"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M19 11a7 7 0 01-7 7m0 0a7 7 0 01-7-7m7 7v4m0 0H8m4 0h4m-4-8a3 3 0 01-3-3V5a3 3 0 116 0v6a3 3 0 01-3 3z"
              />
            </svg>
          </button>
        </div>

        <div className="bg-dark-600 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-3">Demo</h3>

          <button
            className={`w-full py-3 flex items-center justify-center rounded-lg bg-purple-500 hover:bg-purple-600 transition-colors ${
              !connected ? 'opacity-50 cursor-not-allowed' : ''
            }`}
            onClick={handleRunDemo}
            disabled={!connected}
          >
            <span className="mr-2">Run Demo</span>
            <svg
              xmlns="http://www.w3.org/2000/svg"
              className="h-5 w-5"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z"
              />
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
              />
            </svg>
          </button>

          <p className="text-sm text-gray-400 mt-2">
            Simulates the complete voice interaction flow: STT → LLM → TTS
          </p>
        </div>
      </div>
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(VoiceControls);
