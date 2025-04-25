import React, { createContext, useContext, useEffect, useState, useCallback, useRef } from 'react';
import { WebSocketService, WebSocketObserver } from './websocket';
import { useConnectionStore } from '../store/connectionStore';
import { useEventStore } from '../store/eventStore';
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
  const { setConnected, setReconnecting, setReconnectAttempts } = useConnectionStore();
  const { addEvent } = useEventStore();

  // Create stable callback functions using useCallback
  const handleConnect = useCallback(() => {
    setConnected(true);
    setReconnecting(false);
    setReconnectAttempts(0);
  }, [setConnected, setReconnecting, setReconnectAttempts]);

  const handleDisconnect = useCallback(() => {
    setConnected(false);
  }, [setConnected]);

  const handleReconnecting = useCallback((attempt: number) => {
    setReconnecting(true);
    setReconnectAttempts(attempt);
  }, [setReconnecting, setReconnectAttempts]);

  const handleEvent = useCallback((event: CodaEvent) => {
    addEvent(event);
  }, [addEvent]);

  const handleError = useCallback((error: Error) => {
    console.error('WebSocket error:', error);
    // Optionally add error to a store or display a notification
  }, []);

  // Store the observer in a ref to maintain reference stability
  const observerRef = useRef<WebSocketObserver | null>(null);

  // Connect to the WebSocket server on mount
  useEffect(() => {
    // Create an observer to handle WebSocket events
    observerRef.current = {
      onConnect: handleConnect,
      onDisconnect: handleDisconnect,
      onReconnecting: handleReconnecting,
      onEvent: handleEvent,
      onError: handleError
    };

    // Add the observer to the service
    service.addObserver(observerRef.current);

    // Connect to the WebSocket server
    service.connect();

    // Clean up on unmount
    return () => {
      if (observerRef.current) {
        service.removeObserver(observerRef.current);
      }
      service.disconnect();
    };
  }, [
    service,
    handleConnect,
    handleDisconnect,
    handleReconnecting,
    handleEvent,
    handleError
  ]);

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
