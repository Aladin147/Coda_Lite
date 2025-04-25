import React, { createContext, useContext, useEffect, useState, ReactNode, useCallback, useMemo } from 'react';
import websocketService, { WebSocketMessage } from './websocket';

// Create a context for the WebSocket service
const WebSocketContext = createContext<{
  service: typeof websocketService | null;
  connected: boolean;
  lastMessage: WebSocketMessage | null;
  connect: () => void;
  disconnect: () => void;
}>({
  service: null,
  connected: false,
  lastMessage: null,
  connect: () => {},
  disconnect: () => {}
});

interface WebSocketProviderProps {
  children: ReactNode;
  autoConnect?: boolean;
}

// WebSocket provider component
export const WebSocketProvider: React.FC<WebSocketProviderProps> = ({
  children,
  autoConnect = true // Changed to true to auto-connect like the original dashboard
}) => {
  const [connected, setConnected] = useState<boolean>(false);
  const [lastMessage, setLastMessage] = useState<WebSocketMessage | null>(null);

  // Use callbacks to prevent infinite loops
  const handleConnectionChange = useCallback((isConnected: boolean) => {
    setConnected(isConnected);
  }, []);

  const handleMessage = useCallback((message: WebSocketMessage) => {
    setLastMessage(message);
  }, []);

  // Connect function
  const connect = useCallback(() => {
    console.log('Manually connecting to WebSocket');
    websocketService.connect();
  }, []);

  // Disconnect function
  const disconnect = useCallback(() => {
    console.log('Manually disconnecting from WebSocket');
    websocketService.disconnect();
  }, []);

  // Connect to the WebSocket server on mount
  useEffect(() => {
    console.log('WebSocketProvider: Setting up listeners');

    // Add listeners
    websocketService.addStatusListener(handleConnectionChange);
    websocketService.addMessageListener(handleMessage);

    // Connect if autoConnect is true
    if (autoConnect) {
      console.log('WebSocketProvider: Auto-connecting');
      websocketService.connect();
    }

    // Clean up on unmount
    return () => {
      console.log('WebSocketProvider: Cleaning up');
      websocketService.removeStatusListener(handleConnectionChange);
      websocketService.removeMessageListener(handleMessage);
      websocketService.disconnect();
    };
  }, [autoConnect]); // Remove handleConnectionChange and handleMessage from dependencies

  // Provide a stable context value to prevent unnecessary re-renders
  const contextValue = useMemo(() => ({
    service: websocketService,
    connected,
    lastMessage,
    connect,
    disconnect
  }), [connected, lastMessage, connect, disconnect]);

  return (
    <WebSocketContext.Provider value={contextValue}>
      {children}
    </WebSocketContext.Provider>
  );
};

// Hook to use the WebSocket service
export const useWebSocket = () => {
  const context = useContext(WebSocketContext);

  if (!context) {
    throw new Error('useWebSocket must be used within a WebSocketProvider');
  }

  return context;
};
