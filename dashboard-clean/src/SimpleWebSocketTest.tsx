import React, { useEffect, useState } from 'react';

const SimpleWebSocketTest: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [messages, setMessages] = useState<string[]>([]);
  
  useEffect(() => {
    // Create a WebSocket connection
    console.log('Creating WebSocket connection');
    const socket = new WebSocket('ws://localhost:8765');
    
    // Set up event handlers
    socket.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setError(null);
      addMessage('Connected to WebSocket server');
    };
    
    socket.onclose = (event) => {
      console.log(`WebSocket disconnected: ${event.code} ${event.reason}`);
      setConnected(false);
      addMessage(`Disconnected: ${event.code} ${event.reason}`);
    };
    
    socket.onerror = (event) => {
      console.error('WebSocket error:', event);
      setError('Failed to connect to WebSocket server');
      addMessage('WebSocket error occurred');
    };
    
    socket.onmessage = (event) => {
      console.log('WebSocket message received:', event.data);
      try {
        const data = JSON.parse(event.data);
        addMessage(`Received: ${JSON.stringify(data, null, 2)}`);
      } catch (err) {
        addMessage(`Received non-JSON message: ${event.data}`);
      }
    };
    
    // Clean up on unmount
    return () => {
      console.log('Closing WebSocket connection');
      socket.close();
    };
  }, []);
  
  // Add a message to the messages list
  const addMessage = (message: string) => {
    setMessages((prev) => [message, ...prev].slice(0, 100));
  };
  
  return (
    <div style={{ 
      backgroundColor: '#121212', 
      color: 'white',
      minHeight: '100vh',
      fontFamily: 'system-ui, sans-serif',
      padding: '20px'
    }}>
      <h1 style={{ fontSize: '24px', fontWeight: 'bold', marginBottom: '20px' }}>
        Simple WebSocket Test
      </h1>
      
      <div style={{ 
        backgroundColor: '#1e1e1e', 
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px'
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '10px' }}>
          Connection Status
        </h2>
        
        <div style={{ display: 'flex', alignItems: 'center', marginBottom: '10px' }}>
          <div style={{ 
            width: '12px', 
            height: '12px', 
            borderRadius: '50%', 
            backgroundColor: connected ? '#10e3b0' : '#ff5c7c',
            marginRight: '10px'
          }}></div>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
        
        {error && (
          <div style={{ 
            backgroundColor: 'rgba(255, 92, 124, 0.2)', 
            color: '#ff5c7c',
            padding: '10px',
            borderRadius: '4px',
            marginTop: '10px'
          }}>
            {error}
          </div>
        )}
      </div>
      
      <div style={{ 
        backgroundColor: '#1e1e1e', 
        borderRadius: '8px',
        padding: '20px'
      }}>
        <h2 style={{ fontSize: '18px', fontWeight: 'bold', marginBottom: '10px' }}>
          Messages
        </h2>
        
        <div style={{ 
          backgroundColor: '#2d3748', 
          borderRadius: '4px',
          padding: '10px',
          height: '300px',
          overflowY: 'auto',
          fontFamily: 'monospace'
        }}>
          {messages.length === 0 ? (
            <div style={{ opacity: 0.5, textAlign: 'center', marginTop: '20px' }}>
              No messages yet
            </div>
          ) : (
            messages.map((message, index) => (
              <div key={index} style={{ 
                borderBottom: '1px solid #4a5568',
                paddingBottom: '5px',
                marginBottom: '5px'
              }}>
                {message}
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
};

export default SimpleWebSocketTest;
