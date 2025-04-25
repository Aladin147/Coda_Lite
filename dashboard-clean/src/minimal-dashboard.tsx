import React, { useEffect, useState } from 'react';
import { createRoot } from 'react-dom/client';

// Simple component to display connection status
const ConnectionStatus: React.FC<{ connected: boolean }> = ({ connected }) => (
  <div style={{ 
    display: 'flex', 
    alignItems: 'center',
    marginBottom: '10px'
  }}>
    <span style={{ marginRight: '10px' }}>Status:</span>
    <span style={{ 
      width: '12px', 
      height: '12px', 
      borderRadius: '50%', 
      backgroundColor: connected ? '#10e3b0' : '#ff5c7c',
      display: 'inline-block',
      marginRight: '10px'
    }}></span>
    <span>{connected ? 'Connected' : 'Disconnected'}</span>
  </div>
);

// Simple component to display messages
const MessageLog: React.FC<{ messages: string[] }> = ({ messages }) => (
  <div style={{ 
    backgroundColor: '#2d3748', 
    borderRadius: '4px',
    padding: '10px',
    height: '200px',
    overflowY: 'auto',
    fontFamily: 'monospace',
    marginBottom: '20px'
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
);

// Main dashboard component
const MinimalDashboard: React.FC = () => {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [socket, setSocket] = useState<WebSocket | null>(null);
  
  // Function to add a message to the log
  const addMessage = (message: string) => {
    setMessages(prev => [message, ...prev].slice(0, 100));
  };
  
  // Function to connect to the WebSocket server
  const connect = () => {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
      addMessage('Already connected or connecting');
      return;
    }
    
    addMessage('Connecting to WebSocket server...');
    
    try {
      const ws = new WebSocket('ws://localhost:8765');
      
      ws.onopen = () => {
        addMessage('Connected to WebSocket server');
        setConnected(true);
      };
      
      ws.onclose = (event) => {
        addMessage(`Disconnected: ${event.code} ${event.reason}`);
        setConnected(false);
        setSocket(null);
      };
      
      ws.onerror = () => {
        addMessage('WebSocket error occurred');
        setConnected(false);
      };
      
      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          addMessage(`Received: ${JSON.stringify(data, null, 2)}`);
        } catch (err) {
          addMessage(`Received non-JSON message: ${event.data}`);
        }
      };
      
      setSocket(ws);
    } catch (err) {
      addMessage(`Error creating WebSocket: ${err instanceof Error ? err.message : String(err)}`);
    }
  };
  
  // Function to disconnect from the WebSocket server
  const disconnect = () => {
    if (!socket) {
      addMessage('Not connected');
      return;
    }
    
    addMessage('Disconnecting...');
    socket.close();
  };
  
  // Function to send a message to the WebSocket server
  const sendMessage = () => {
    if (!socket || socket.readyState !== WebSocket.OPEN) {
      addMessage('Cannot send message, not connected');
      return;
    }
    
    const message = {
      type: 'test',
      data: { message: 'Hello from dashboard' },
      timestamp: Date.now()
    };
    
    addMessage(`Sending: ${JSON.stringify(message, null, 2)}`);
    socket.send(JSON.stringify(message));
  };
  
  return (
    <div style={{ padding: '20px', maxWidth: '800px', margin: '0 auto' }}>
      <h1 style={{ marginBottom: '20px' }}>Minimal Dashboard</h1>
      
      <div style={{ 
        backgroundColor: '#1e1e1e', 
        borderRadius: '8px',
        padding: '20px',
        marginBottom: '20px'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '15px' }}>Connection</h2>
        <ConnectionStatus connected={connected} />
        
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button 
            onClick={connect}
            disabled={connected}
            style={{
              backgroundColor: connected ? '#3b82f680' : '#3b82f6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: connected ? 'not-allowed' : 'pointer',
              opacity: connected ? 0.7 : 1
            }}
          >
            Connect
          </button>
          
          <button 
            onClick={disconnect}
            disabled={!connected}
            style={{
              backgroundColor: !connected ? '#ef444480' : '#ef4444',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: !connected ? 'not-allowed' : 'pointer',
              opacity: !connected ? 0.7 : 1
            }}
          >
            Disconnect
          </button>
          
          <button 
            onClick={sendMessage}
            disabled={!connected}
            style={{
              backgroundColor: !connected ? '#8b5cf680' : '#8b5cf6',
              color: 'white',
              border: 'none',
              borderRadius: '4px',
              padding: '8px 16px',
              cursor: !connected ? 'not-allowed' : 'pointer',
              opacity: !connected ? 0.7 : 1
            }}
          >
            Send Test Message
          </button>
        </div>
      </div>
      
      <div style={{ 
        backgroundColor: '#1e1e1e', 
        borderRadius: '8px',
        padding: '20px'
      }}>
        <h2 style={{ marginTop: 0, marginBottom: '15px' }}>Messages</h2>
        <MessageLog messages={messages} />
      </div>
    </div>
  );
};

// Render the app
const rootElement = document.getElementById('root');
if (rootElement) {
  const root = createRoot(rootElement);
  root.render(
    <React.StrictMode>
      <MinimalDashboard />
    </React.StrictMode>
  );
} else {
  console.error('Root element not found');
}
