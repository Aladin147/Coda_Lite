import React, { useEffect, useState } from 'react';

const MinimalTest: React.FC = () => {
  const [status, setStatus] = useState<string>('Disconnected');
  const [socket, setSocket] = useState<WebSocket | null>(null);
  const [error, setError] = useState<string | null>(null);
  
  useEffect(() => {
    // Clean up function
    const cleanup = () => {
      if (socket) {
        console.log('Closing socket');
        socket.close();
      }
    };
    
    try {
      console.log('Creating WebSocket connection');
      const ws = new WebSocket('ws://localhost:8765');
      
      ws.onopen = () => {
        console.log('WebSocket connected');
        setStatus('Connected');
        setError(null);
      };
      
      ws.onclose = (event) => {
        console.log(`WebSocket disconnected: ${event.code} ${event.reason}`);
        setStatus('Disconnected');
      };
      
      ws.onerror = (event) => {
        console.error('WebSocket error:', event);
        setStatus('Error');
        setError('Failed to connect to WebSocket server');
      };
      
      setSocket(ws);
    } catch (err) {
      console.error('Error creating WebSocket:', err);
      setStatus('Error');
      setError(`Error creating WebSocket: ${err instanceof Error ? err.message : String(err)}`);
    }
    
    // Clean up on unmount
    return cleanup;
  }, []);
  
  return (
    <div style={{ 
      padding: '20px', 
      backgroundColor: '#121212', 
      color: 'white',
      minHeight: '100vh',
      fontFamily: 'system-ui, sans-serif'
    }}>
      <h1>Minimal WebSocket Test</h1>
      
      <div style={{ 
        padding: '20px', 
        backgroundColor: '#1e1e1e', 
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>WebSocket Status</h2>
        <div style={{ 
          display: 'flex', 
          alignItems: 'center',
          marginTop: '10px'
        }}>
          <span style={{ marginRight: '10px' }}>Status:</span>
          <span style={{ 
            width: '12px', 
            height: '12px', 
            borderRadius: '50%', 
            backgroundColor: 
              status === 'Connected' ? '#10e3b0' : 
              status === 'Error' ? '#ff5c7c' : 
              '#ffc72c',
            display: 'inline-block',
            marginRight: '10px'
          }}></span>
          <span>{status}</span>
        </div>
        
        {error && (
          <div style={{ 
            marginTop: '20px', 
            padding: '10px', 
            backgroundColor: 'rgba(255, 92, 124, 0.2)', 
            borderRadius: '4px',
            color: '#ff5c7c'
          }}>
            {error}
          </div>
        )}
      </div>
    </div>
  );
};

export default MinimalTest;
