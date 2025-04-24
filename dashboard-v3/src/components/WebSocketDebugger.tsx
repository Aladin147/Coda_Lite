import React, { useState, useEffect, useRef } from 'react';
import { CodaEvent } from '../types/events';

interface WebSocketDebuggerProps {
  maxEvents?: number;
  events?: any[];
}

/**
 * WebSocketDebugger component for monitoring WebSocket communication
 *
 * This component displays:
 * - Connection status
 * - Raw WebSocket messages
 * - Event statistics
 * - Manual reconnect button
 * - Event filtering options
 */
const WebSocketDebugger: React.FC<WebSocketDebuggerProps> = ({ maxEvents = 100, events = [] }) => {
  const [isConnected, setIsConnected] = useState(false);
  const [filter, setFilter] = useState('');
  const [autoScroll, setAutoScroll] = useState(true);
  const [eventCounts, setEventCounts] = useState<Record<string, number>>({});
  const [expandedEvents, setExpandedEvents] = useState<Record<string, boolean>>({});
  const [showRawJson, setShowRawJson] = useState(false);
  const eventsEndRef = useRef<HTMLDivElement>(null);

  // Update connection status based on window.wsClient
  useEffect(() => {
    const checkConnection = () => {
      const isConnected = !!(window as any).wsClient?.isConnected();
      setIsConnected(isConnected);
    };

    // Check connection status initially
    checkConnection();

    // Set up interval to check connection status
    const interval = setInterval(checkConnection, 1000);

    return () => {
      clearInterval(interval);
    };
  }, []);

  // Update event counts when events change
  useEffect(() => {
    const counts: Record<string, number> = {};

    events.forEach(event => {
      const type = event.type;
      counts[type] = (counts[type] || 0) + 1;
    });

    setEventCounts(counts);
  }, [events]);

  // Auto-scroll to bottom when new events arrive
  useEffect(() => {
    if (autoScroll && eventsEndRef.current && typeof eventsEndRef.current.scrollIntoView === 'function') {
      eventsEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [events, autoScroll]);

  // Filter events based on search term
  const filteredEvents = filter
    ? events.filter(event =>
        event.type.toLowerCase().includes(filter.toLowerCase()) ||
        JSON.stringify(event.data).toLowerCase().includes(filter.toLowerCase())
      )
    : events;

  // Toggle event expansion
  const toggleEventExpansion = (eventId: string) => {
    setExpandedEvents(prev => ({
      ...prev,
      [eventId]: !prev[eventId]
    }));
  };

  // Handle manual reconnect
  const handleReconnect = () => {
    if (!(window as any).wsClient) return;

    (window as any).wsClient.disconnect();
    setTimeout(() => {
      (window as any).wsClient.connect();
    }, 500);
  };

  // Clear events
  const handleClearEvents = () => {
    // We can't clear events directly since they're passed as props
    // But we can clear the event counts display
    setEventCounts({});
  };

  // Send a test message
  const handleSendTestMessage = () => {
    if (!(window as any).wsClient || !(window as any).wsClient.isConnected()) return;

    const message = {
      type: 'test_message',
      data: { timestamp: new Date().toISOString() },
      timestamp: new Date().toISOString()
    };

    try {
      (window as any).wsClient.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending test message:', error);
    }
  };

  // Send a test text input message
  const handleSendTextInputTest = () => {
    if (!(window as any).wsClient || !(window as any).wsClient.isConnected()) return;

    const message = {
      type: 'text_input',
      data: { text: 'Hello from WebSocket debugger!' },
      timestamp: new Date().toISOString()
    };

    try {
      (window as any).wsClient.socket.send(JSON.stringify(message));
    } catch (error) {
      console.error('Error sending text input test:', error);
    }
  };

  // Format timestamp
  const formatTimestamp = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (e) {
      return timestamp;
    }
  };

  return (
    <div className="card p-4 bg-dark-700 text-white">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">WebSocket Debugger</h2>
        <div className="flex items-center space-x-2">
          <div className={`w-3 h-3 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`}></div>
          <span>{isConnected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-4">
        <div className="bg-dark-600 p-3 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Connection</h3>
          <div className="space-y-2">
            <div className="flex justify-between">
              <span>Status:</span>
              <span className={isConnected ? 'text-green-500' : 'text-red-500'}>
                {isConnected ? 'Connected' : 'Disconnected'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Connection:</span>
              <span className="text-gray-300">
                {(window as any).wsClient ?
                  ((window as any).wsClient.socket ?
                    ((window as any).wsClient.socket.readyState === WebSocket.OPEN ? 'Open' :
                     (window as any).wsClient.socket.readyState === WebSocket.CONNECTING ? 'Connecting' :
                     (window as any).wsClient.socket.readyState === WebSocket.CLOSING ? 'Closing' : 'Closed')
                    : 'No Socket')
                  : 'Not Initialized'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Client ID:</span>
              <span className="text-gray-300">
                {(window as any).wsClient ? (window as any).wsClient.clientId : 'N/A'}
              </span>
            </div>
            <div className="flex justify-between">
              <span>Messages Sent:</span>
              <span className="text-gray-300">
                {(window as any).wsClient ? (window as any).wsClient.messageCounter : 0}
              </span>
            </div>
            <div className="flex justify-between">
              <span>URL:</span>
              <span className="text-gray-300">ws://localhost:8765</span>
            </div>
            <div className="flex justify-between">
              <span>Events:</span>
              <span>{events.length}</span>
            </div>
            <button
              onClick={handleReconnect}
              className="w-full mt-2 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
            >
              Reconnect
            </button>
          </div>
        </div>

        <div className="bg-dark-600 p-3 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Event Types</h3>
          <div className="max-h-40 overflow-y-auto">
            {Object.entries(eventCounts)
              .sort((a, b) => b[1] - a[1])
              .map(([type, count]) => (
                <div key={type} className="flex justify-between py-1 border-b border-dark-500">
                  <span className="text-sm">{type}</span>
                  <span className="text-sm font-mono">{count}</span>
                </div>
              ))}
          </div>
        </div>

        <div className="bg-dark-600 p-3 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Controls</h3>
          <div className="space-y-2">
            <div className="flex items-center">
              <input
                type="checkbox"
                id="autoScroll"
                checked={autoScroll}
                onChange={(e) => setAutoScroll(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="autoScroll">Auto-scroll</label>
            </div>
            <div className="flex items-center">
              <input
                type="checkbox"
                id="showRawJson"
                checked={showRawJson}
                onChange={(e) => setShowRawJson(e.target.checked)}
                className="mr-2"
              />
              <label htmlFor="showRawJson">Show raw JSON</label>
            </div>
            <div className="flex space-x-2">
              <button
                onClick={handleClearEvents}
                className="flex-1 px-3 py-1 bg-red-600 hover:bg-red-700 rounded-md transition-colors"
              >
                Clear Events
              </button>
              <button
                onClick={handleSendTestMessage}
                className="flex-1 px-3 py-1 bg-green-600 hover:bg-green-700 rounded-md transition-colors"
              >
                Test Message
              </button>
            </div>
            <div className="flex space-x-2 mt-2">
              <button
                onClick={handleSendTextInputTest}
                className="flex-1 px-3 py-1 bg-blue-600 hover:bg-blue-700 rounded-md transition-colors"
              >
                Test Text Input
              </button>
            </div>
            <div className="flex space-x-2 mt-2">
              <button
                onClick={() => {
                  if ((window as any).wsClient && (window as any).wsClient.sentMessages) {
                    console.table(
                      Array.from((window as any).wsClient.sentMessages.entries())
                        .map(([id, data]) => ({
                          id,
                          type: data.message.type,
                          data: JSON.stringify(data.message.data),
                          sentAt: new Date(data.sentAt).toLocaleTimeString(),
                          fingerprint: data.fingerprint
                        }))
                    );
                  } else {
                    console.log('No message history available');
                  }
                }}
                className="flex-1 px-3 py-1 bg-purple-600 hover:bg-purple-700 rounded-md transition-colors"
              >
                Show Message History
              </button>
            </div>
          </div>
        </div>
      </div>

      <div className="mb-4">
        <input
          type="text"
          placeholder="Filter events..."
          value={filter}
          onChange={(e) => setFilter(e.target.value)}
          className="w-full px-3 py-2 bg-dark-600 border border-dark-500 rounded-md focus:outline-none focus:ring-1 focus:ring-primary-500"
        />
      </div>

      <div className="bg-dark-800 rounded-lg p-2 h-96 overflow-y-auto font-mono text-sm">
        {filteredEvents.length === 0 ? (
          <div className="text-center text-gray-400 py-4">No events to display</div>
        ) : (
          filteredEvents.map((event, index) => {
            const eventId = `${event.type}-${index}`;
            const isExpanded = expandedEvents[eventId] || false;

            return (
              <div
                key={index}
                className="mb-1 p-2 bg-dark-700 rounded hover:bg-dark-600 cursor-pointer"
                onClick={() => toggleEventExpansion(eventId)}
              >
                <div className="flex justify-between items-start">
                  <div className="flex items-center">
                    <span className={`mr-2 ${isExpanded ? 'transform rotate-90' : ''}`}>▶</span>
                    <span className="font-semibold text-primary-400">{event.type}</span>
                  </div>
                  <span className="text-xs text-gray-400">
                    {event.timestamp ? formatTimestamp(event.timestamp) : 'No timestamp'}
                  </span>
                </div>

                {isExpanded && (
                  <div className="mt-2 pl-6 border-l-2 border-dark-500">
                    {showRawJson ? (
                      <pre className="whitespace-pre-wrap break-all text-xs">
                        {JSON.stringify(event, null, 2)}
                      </pre>
                    ) : (
                      <div>
                        {event.data && Object.entries(event.data).map(([key, value]) => (
                          <div key={key} className="flex flex-col mb-1">
                            <span className="text-gray-400">{key}:</span>
                            <span className="pl-2 break-all">
                              {typeof value === 'object'
                                ? JSON.stringify(value)
                                : String(value)}
                            </span>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
              </div>
            );
          })
        )}
        <div ref={eventsEndRef} />
      </div>
    </div>
  );
};

export default WebSocketDebugger;
