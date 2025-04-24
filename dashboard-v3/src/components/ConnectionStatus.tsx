import React, { memo, useState, useEffect } from 'react';

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
  const [showDetails, setShowDetails] = useState(false);
  const [lastConnected, setLastConnected] = useState<Date | null>(null);
  const [connectionTime, setConnectionTime] = useState<string>('');

  // Update the last connected time when connection status changes
  useEffect(() => {
    if (connected) {
      setLastConnected(new Date());
    }
  }, [connected]);

  // Update the connection time display
  useEffect(() => {
    if (!connected || !lastConnected) return;

    const timer = setInterval(() => {
      const now = new Date();
      const diff = now.getTime() - lastConnected.getTime();

      // Format the time difference
      const seconds = Math.floor(diff / 1000) % 60;
      const minutes = Math.floor(diff / (1000 * 60)) % 60;
      const hours = Math.floor(diff / (1000 * 60 * 60));

      let timeString = '';
      if (hours > 0) {
        timeString = `${hours}h ${minutes}m ${seconds}s`;
      } else if (minutes > 0) {
        timeString = `${minutes}m ${seconds}s`;
      } else {
        timeString = `${seconds}s`;
      }

      setConnectionTime(timeString);
    }, 1000);

    return () => clearInterval(timer);
  }, [connected, lastConnected]);

  // Get the appropriate status color and animation
  const getStatusStyles = () => {
    if (connected) {
      return 'bg-green-500 shadow-lg shadow-green-500/30';
    } else if (reconnecting) {
      return 'bg-yellow-500 animate-pulse shadow-lg shadow-yellow-500/30';
    } else {
      return 'bg-red-500 shadow-lg shadow-red-500/30';
    }
  };

  // Get the appropriate status text and icon
  const getStatusContent = () => {
    if (connected) {
      return {
        text: 'Connected',
        detailText: `Connected for ${connectionTime}`,
        icon: (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M12 5l7 7-7 7" />
          </svg>
        )
      };
    } else if (reconnecting) {
      return {
        text: 'Reconnecting',
        detailText: `Attempt ${reconnectAttempts}`,
        icon: (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 animate-spin" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
        )
      };
    } else {
      return {
        text: 'Disconnected',
        detailText: 'Check Coda server',
        icon: (
          <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        )
      };
    }
  };

  const statusStyles = getStatusStyles();
  const statusContent = getStatusContent();

  return (
    <div
      className="relative"
      onMouseEnter={() => setShowDetails(true)}
      onMouseLeave={() => setShowDetails(false)}
    >
      <div className="flex items-center bg-dark-600 rounded-full px-3 py-1 cursor-pointer transition-all hover:bg-dark-500">
        <span
          className={`inline-block w-3 h-3 rounded-full mr-2 ${statusStyles}`}
        ></span>
        <span className="text-sm font-medium">
          {statusContent.text}
        </span>
        <span className="ml-1 text-gray-400">
          {statusContent.icon}
        </span>
      </div>

      {/* Tooltip with connection details */}
      {showDetails && (
        <div className="absolute right-0 mt-2 w-48 bg-dark-700 rounded-md shadow-lg z-10 p-3 text-sm">
          <div className="font-medium mb-1">{statusContent.text}</div>
          <div className="text-xs text-gray-300">{statusContent.detailText}</div>

          {reconnecting && (
            <div className="mt-2 w-full bg-dark-600 rounded-full h-1.5">
              <div
                className="bg-yellow-500 h-1.5 rounded-full"
                style={{ width: `${Math.min(reconnectAttempts * 10, 100)}%` }}
              ></div>
            </div>
          )}

          {!connected && !reconnecting && (
            <button
              className="mt-2 w-full text-xs bg-dark-600 hover:bg-dark-500 rounded px-2 py-1 transition-colors"
              onClick={() => window.location.reload()}
            >
              Refresh Page
            </button>
          )}
        </div>
      )}
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(ConnectionStatus);
