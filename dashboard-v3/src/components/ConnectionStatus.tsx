import React, { memo } from 'react';

interface ConnectionStatusProps {
  connected: boolean;
  reconnecting: boolean;
  reconnectAttempts: number;
}

const ConnectionStatus: React.FC<ConnectionStatusProps> = ({
  connected,
  reconnecting,
  reconnectAttempts
}) => {
  return (
    <div className="flex items-center">
      <span 
        className={`inline-block w-3 h-3 rounded-full mr-2 ${
          connected 
            ? 'bg-green-500' 
            : reconnecting 
              ? 'bg-yellow-500 animate-pulse' 
              : 'bg-red-500'
        }`}
      ></span>
      <span className="text-sm">
        {connected 
          ? 'Connected' 
          : reconnecting 
            ? `Reconnecting (Attempt ${reconnectAttempts})` 
            : 'Disconnected'
        }
      </span>
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(ConnectionStatus);
