import { useCallback } from 'react';
import { WebSocketProvider, useWebSocket } from './services/WebSocketProvider';
import Layout from './components/Layout';
import Avatar from './components/Avatar';
import ConversationView from './components/ConversationView';
import PerformanceMonitor from './components/PerformanceMonitor';
import MemoryViewer from './components/MemoryViewer';
import VoiceControls from './components/VoiceControls';
import ConnectionStatus from './components/ConnectionStatus';
import { useConnectionStore } from './store/connectionStore';
import { useEventStore } from './store/eventStore';

function App() {
  return (
    <WebSocketProvider>
      <AppContent />
    </WebSocketProvider>
  );
}

// Inner component that uses the WebSocket context
function AppContent() {
  // Get the WebSocket service
  const webSocketService = useWebSocket();

  // Get state from stores
  const { connected, reconnecting, reconnectAttempts } = useConnectionStore();
  const {
    performanceMetrics,
    systemMetrics,
    memories,
    messages,
    mode,
    emotion
  } = useEventStore();

  // Function to send messages to the WebSocket server - memoized to prevent infinite re-renders
  const sendMessage = useCallback((type: string, data: any) => {
    if (!webSocketService) return;

    const message = {
      type,
      data,
      timestamp: new Date().toISOString()
    };

    webSocketService.send(message);
  }, [webSocketService]);

  // Handlers for voice controls
  const handleStartListening = useCallback(() => {
    sendMessage('stt_start', {});
  }, [sendMessage]);

  const handleStopListening = useCallback(() => {
    sendMessage('stt_stop', {});
  }, [sendMessage]);

  const handleRunDemo = useCallback(() => {
    sendMessage('demo_flow', {
      text: "Tell me a short joke about programming."
    });
  }, [sendMessage]);

  return (
    <Layout>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* First column */}
        <div className="space-y-6">
          <div className="card p-4">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-xl font-bold">Coda</h2>
              <ConnectionStatus
                connected={connected}
                reconnecting={reconnecting}
                reconnectAttempts={reconnectAttempts}
              />
            </div>

            <Avatar mode={mode} emotion={emotion} />
          </div>

          <VoiceControls
            connected={connected}
            onStartListening={handleStartListening}
            onStopListening={handleStopListening}
            onRunDemo={handleRunDemo}
          />
        </div>

        {/* Second column */}
        <div className="lg:col-span-2 space-y-6">
          <PerformanceMonitor
            performanceMetrics={performanceMetrics}
            systemMetrics={systemMetrics}
          />

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <MemoryViewer memories={memories} />

            <div className="card p-4 h-64">
              <div className="h-full">
                <h2 className="text-xl font-bold mb-4">Settings</h2>

                <div className="space-y-4">
                  <div>
                    <h3 className="text-lg font-semibold mb-2">About</h3>
                    <p className="text-sm text-gray-300">
                      Coda Dashboard v3.0
                    </p>
                    <p className="text-xs mt-1 text-gray-400">
                      Built with React, Tailwind CSS, and WebSockets
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <ConversationView messages={messages} />
        </div>
      </div>
    </Layout>
  );
}

export default App;
