import React, { useState, useMemo } from 'react';
import { WebSocketProvider, useWebSocket } from './services/WebSocketProvider';
import ErrorBoundary from './components/ErrorBoundary';
import Layout from './components/Layout';
import Avatar from './components/Avatar';
import ConversationView from './components/ConversationView';
import PerformanceMonitor from './components/PerformanceMonitor';
import MemoryViewer from './components/MemoryViewer';
import VoiceControls from './components/VoiceControls';

// Connection control component
const ConnectionControl: React.FC = () => {
  const { connected, connect, disconnect } = useWebSocket();

  // Memoize button styles to prevent unnecessary re-renders
  const connectButtonStyle = useMemo(() => ({
    opacity: connected ? 0.5 : 1,
    cursor: connected ? 'not-allowed' : 'pointer'
  }), [connected]);

  const disconnectButtonStyle = useMemo(() => ({
    opacity: !connected ? 0.5 : 1,
    cursor: !connected ? 'not-allowed' : 'pointer'
  }), [connected]);

  // Memoize status indicator color
  const statusColor = useMemo(() =>
    connected ? 'var(--color-success-500)' : 'var(--color-danger-500)'
  , [connected]);

  // Memoize status text
  const statusText = useMemo(() =>
    connected ? 'Connected' : 'Disconnected'
  , [connected]);

  return (
    <div className="card p-4 mb-6">
      <h2 className="text-xl font-semibold mb-4">Connection Control</h2>
      <div className="flex space-x-4">
        <button
          className="btn flex-1"
          onClick={connect}
          disabled={connected}
          style={connectButtonStyle}
        >
          Connect
        </button>
        <button
          className="btn btn-danger flex-1"
          onClick={disconnect}
          disabled={!connected}
          style={disconnectButtonStyle}
        >
          Disconnect
        </button>
      </div>
      <div className="mt-4 flex items-center">
        <span className="mr-2">Status:</span>
        <span
          className="inline-block w-3 h-3 rounded-full mr-2"
          style={{ backgroundColor: statusColor }}
        ></span>
        <span>{statusText}</span>
      </div>
    </div>
  );
};

// Main dashboard content
const DashboardContent: React.FC = () => {
  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* First column */}
      <div className="flex flex-col space-y-6">
        <div className="card p-6 flex justify-center">
          {/* Avatar component disabled temporarily */}
          <div className="flex flex-col items-center">
            <div className="avatar avatar-idle">
              <span className="text-4xl">C</span>
            </div>
            <div className="mt-4 text-center">
              <div className="font-semibold">
                Mode: <span className="font-normal">idle</span>
              </div>
              <div className="font-semibold">
                Emotion: <span className="font-normal">neutral</span>
              </div>
            </div>
          </div>
        </div>
        <VoiceControls />
      </div>

      {/* Second column */}
      <div className="lg:col-span-2 flex flex-col space-y-6">
        <ConversationView />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <PerformanceMonitor />
          <MemoryViewer />
        </div>
      </div>
    </div>
  );
};

function App() {
  return (
    <ErrorBoundary>
      <WebSocketProvider autoConnect={true}>
        <Layout>
          <ConnectionControl />
          <DashboardContent />
        </Layout>
      </WebSocketProvider>
    </ErrorBoundary>
  );
}

export default App;
