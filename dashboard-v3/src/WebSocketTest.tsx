import { useState, useEffect } from 'react';
import WebSocketClient from './WebSocketClient';

/**
 * Simple component to test WebSocket connection
 */
function WebSocketTest() {
  const [connected, setConnected] = useState(false);
  const [messages, setMessages] = useState<string[]>([]);
  const [inputText, setInputText] = useState('');

  useEffect(() => {
    // Create a WebSocket client
    const client = new WebSocketClient('ws://localhost:8765');

    client.onConnect = () => {
      console.log('Connected to WebSocket server');
      setConnected(true);
      addMessage('Connected to WebSocket server');
    };

    client.onDisconnect = () => {
      console.log('Disconnected from WebSocket server');
      setConnected(false);
      addMessage('Disconnected from WebSocket server');
    };

    client.onEvent = (event) => {
      console.log('Received event:', event);
      addMessage(`Received: ${JSON.stringify(event)}`);
    };

    client.onError = (error) => {
      console.error('WebSocket error:', error);
      addMessage(`Error: ${error}`);
    };

    // Connect to the WebSocket server
    client.connect();

    // Clean up on unmount
    return () => {
      client.disconnect();
    };
  }, []);

  // Add a message to the messages list
  const addMessage = (message: string) => {
    setMessages((prev) => [message, ...prev].slice(0, 100));
  };

  // Send a message to the WebSocket server
  const sendMessage = () => {
    if (!(window as any).wsClient) {
      console.error('WebSocket client not initialized');
      addMessage('Error: WebSocket client not initialized');
      return;
    }

    if ((window as any).wsClient.isConnected()) {
      const message = {
        type: 'text_input',
        data: { text: inputText },
        timestamp: new Date().toISOString()
      };

      try {
        console.log('Sending message:', message);
        (window as any).wsClient.socket.send(JSON.stringify(message));
        addMessage(`Sent: ${JSON.stringify(message)}`);
        setInputText('');
      } catch (error) {
        console.error('Error sending message:', error);
        addMessage(`Error sending message: ${error}`);
      }
    } else {
      console.error('WebSocket not connected');
      addMessage('Error: WebSocket not connected');
    }
  };

  return (
    <div className="p-4 bg-dark-800 text-white min-h-screen">
      <h1 className="text-2xl font-bold mb-4">WebSocket Test</h1>
      
      <div className="mb-4">
        <div className="flex items-center mb-2">
          <div className={`w-3 h-3 rounded-full mr-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
      
      <div className="mb-4">
        <div className="flex">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            className="flex-1 px-3 py-2 bg-dark-600 border border-dark-500 rounded-l-md text-white"
            placeholder="Type a message..."
          />
          <button
            onClick={sendMessage}
            className="px-4 py-2 bg-primary-600 hover:bg-primary-700 rounded-r-md"
            disabled={!connected || !inputText.trim()}
          >
            Send
          </button>
        </div>
      </div>
      
      <div className="bg-dark-700 rounded-md p-4 h-96 overflow-y-auto">
        {messages.length === 0 ? (
          <div className="text-gray-400">No messages yet</div>
        ) : (
          messages.map((message, index) => (
            <div key={index} className="mb-2 text-sm">
              {message}
            </div>
          ))
        )}
      </div>
    </div>
  );
}

export default WebSocketTest;
