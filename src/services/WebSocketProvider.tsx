import React, { createContext, useContext, useEffect, useState } from 'react';
import { WebSocketService, WebSocketObserver } from './websocket';
import { useConnectionState, useEvents } from '../store/selectors';
import { CodaEvent } from '../types/events';

// Create a context for the WebSocket service
const WebSocketContext = createContext<WebSocketService | null>(null);

// Props for the WebSocketProvider component
interface WebSocketProviderProps {
  url?: string;
  children: React.ReactNode;
}

/**
 * WebSocketProvider component that provides the WebSocket service to the application
 */
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({ 
  url = 'ws://localhost:8765',
  children 
}) => {
  // Create the WebSocket service
  const [service] = useState(() => new WebSocketService(url));
  
  // Get the connection state and event handlers from the store
  const { setConnected } = useConnectionState();
  const { processEvent } = useEvents();
  
  // Connect to the WebSocket server on mount
  useEffect(() => {
    // Create an observer to handle WebSocket events
    const observer: WebSocketObserver = {
      onConnect: () => {
        setConnected(true);
      },
      onDisconnect: () => {
        setConnected(false);
      },
      onEvent: (event: CodaEvent) => {
        processEvent(event);
      },
      onError: (error: Error) => {
        console.error('WebSocket error:', error);
      }
    };
    
    // Add the observer to the service
    service.addObserver(observer);
    
    // Connect to the WebSocket server
    service.connect();
    
    // Clean up on unmount
    return () => {
      service.removeObserver(observer);
      service.disconnect();
    };
  }, [service, setConnected, processEvent]);
  
  return (
    <WebSocketContext.Provider value={service}>
      {children}
    </WebSocketContext.Provider>
  );
};

/**
 * Hook to use the WebSocket service
 */
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);
  
  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }
  
  return context;
};
