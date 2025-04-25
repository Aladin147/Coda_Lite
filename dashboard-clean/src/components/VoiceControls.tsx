import React, { useState } from 'react';
import { useCodaMode } from '../store/selectors';
import { useWebSocket } from '../services/WebSocketProvider';

const VoiceControls: React.FC = () => {
  const { mode, setMode, emotionContext, setEmotionContext } = useCodaMode();
  const { service, connected } = useWebSocket();
  const [isRecording, setIsRecording] = useState(false);
  
  // Function to send a command to the WebSocket server
  const sendCommand = (command: string, data: any = {}) => {
    if (!service || !connected) {
      console.warn('Cannot send command, WebSocket is not connected');
      return;
    }
    
    service.send({
      type: command,
      data,
      timestamp: Date.now()
    });
  };
  
  // Function to start recording
  const startRecording = () => {
    setIsRecording(true);
    setMode('listening');
    sendCommand('start_recording');
    
    // Simulate stopping after 5 seconds
    setTimeout(() => {
      stopRecording();
    }, 5000);
  };
  
  // Function to stop recording
  const stopRecording = () => {
    setIsRecording(false);
    setMode('thinking');
    sendCommand('stop_recording');
    
    // Simulate thinking for 2 seconds, then speaking for 3 seconds
    setTimeout(() => {
      setMode('speaking');
      
      setTimeout(() => {
        setMode('idle');
      }, 3000);
    }, 2000);
  };
  
  // Available emotions
  const emotions: { value: any; label: string }[] = [
    { value: 'neutral', label: 'Neutral' },
    { value: 'playful', label: 'Playful' },
    { value: 'supportive', label: 'Supportive' },
    { value: 'concerned', label: 'Concerned' },
    { value: 'witty', label: 'Witty' },
    { value: 'focused', label: 'Focused' }
  ];
  
  return (
    <div className="card p-4 h-96 flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Voice Controls</h2>
      
      <div className="flex-1 flex flex-col items-center justify-center">
        <button
          className={`w-32 h-32 rounded-full flex items-center justify-center text-white text-4xl ${
            isRecording 
              ? 'bg-red-500 animate-pulse' 
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
          onClick={isRecording ? stopRecording : startRecording}
          disabled={!connected}
          style={{ 
            opacity: connected ? 1 : 0.5,
            cursor: connected ? 'pointer' : 'not-allowed'
          }}
        >
          {isRecording ? '■' : '▶'}
        </button>
        
        <div className="mt-4 text-center">
          <p className="mb-2">
            {isRecording 
              ? 'Recording... Click to stop' 
              : connected 
                ? 'Click to start recording' 
                : 'Connect to enable recording'
            }
          </p>
          <p className="text-sm opacity-70">Current mode: {mode}</p>
        </div>
      </div>
      
      <div className="mt-4">
        <label className="block mb-2">Emotion Context:</label>
        <select
          className="w-full p-2 rounded"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            color: 'var(--text-color)',
            border: '1px solid var(--border-color)'
          }}
          value={emotionContext}
          onChange={(e) => setEmotionContext(e.target.value as any)}
        >
          {emotions.map((emotion) => (
            <option key={emotion.value} value={emotion.value}>
              {emotion.label}
            </option>
          ))}
        </select>
      </div>
      
      <div className="mt-4 flex space-x-2">
        <button 
          className="btn flex-1"
          onClick={() => {
            // Simulate a complete voice interaction flow
            setMode('listening');
            
            setTimeout(() => {
              setMode('thinking');
              
              setTimeout(() => {
                setMode('speaking');
                
                setTimeout(() => {
                  setMode('idle');
                }, 3000);
              }, 2000);
            }, 2000);
          }}
        >
          Demo Flow
        </button>
        
        <button 
          className="btn btn-danger flex-1"
          onClick={() => {
            // Simulate an error
            setMode('error');
            
            setTimeout(() => {
              setMode('idle');
            }, 3000);
          }}
        >
          Test Error
        </button>
      </div>
    </div>
  );
};

export default VoiceControls;
