import { useEffect, useState } from 'react';
import { WebSocketProvider, useWebSocket } from './services/WebSocketProvider';
import Layout from './components/Layout';
import Avatar from './components/Avatar';
import ConversationView from './components/ConversationView';
import PerformanceMonitor from './components/PerformanceMonitor';
import MemoryViewer from './components/MemoryViewer';
import VoiceControls from './components/VoiceControls';
import Debug from './components/Debug';
import { useUIState, useCodaMode, useConnectionState } from './store/selectors';

function App() {
  // We're now always using dark mode, so we don't need the darkMode state
  const { connected } = useConnectionState();
  const { mode, emotionContext, setMode, setEmotionContext } = useCodaMode();
  const [showDebugPanel, setShowDebugPanel] = useState(false);
  const [showDebugScreen, setShowDebugScreen] = useState(false); // Start with debug screen hidden

  // Add keyboard shortcut to toggle debug screen
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Toggle debug screen with Ctrl+Shift+D
      if (e.ctrlKey && e.shiftKey && e.key === 'D') {
        setShowDebugScreen(prev => !prev);
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  return (
    <>
      {showDebugScreen && <Debug />}
      <WebSocketProvider>
        <AppContent
          connected={connected}
          mode={mode}
          emotionContext={emotionContext}
          setMode={setMode}
          setEmotionContext={setEmotionContext}
          showDebugPanel={showDebugPanel}
          setShowDebugPanel={setShowDebugPanel}
        />
      </WebSocketProvider>
    </>
  );
}

// Inner component that uses the WebSocket context
interface AppContentProps {
  connected: boolean;
  mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  emotionContext: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';
  setMode: (mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error') => void;
  setEmotionContext: (emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused') => void;
  showDebugPanel: boolean;
  setShowDebugPanel: (show: boolean) => void;
}

function AppContent({
  connected,
  mode,
  emotionContext,
  setMode,
  setEmotionContext,
  showDebugPanel,
  setShowDebugPanel
}: AppContentProps) {
  // Get the WebSocket service
  const webSocketService = useWebSocket();

  // Function to send messages to the WebSocket server
  const sendMessage = (type: string, data: any) => {
    if (!webSocketService) return;

    const message = {
      type,
      data,
      timestamp: Date.now()
    };

    webSocketService.send(message);
  };

  // Add console log for debugging
  console.log("Rendering AppContent", { connected, mode, emotionContext });

  return (
    <Layout>
        <h1 style={{ color: 'red', fontSize: '24px', margin: '20px', fontWeight: 'bold' }}>
          DEBUG: Dashboard Content Should Appear Below
        </h1>
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* First column */}
          <div className="space-y-6">
            <div className="card p-4">
              <div className="flex justify-between items-center mb-4">
                <h2 className="text-xl font-bold">Coda</h2>
                <div className="flex items-center">
                  <span className={`inline-block w-3 h-3 rounded-full mr-2 ${connected ? 'bg-green-500' : 'bg-red-500'}`}></span>
                  <span className="text-sm">{connected ? 'Connected' : 'Disconnected'}</span>
                </div>
              </div>
              <Avatar />

              {showDebugPanel && (
                <div className="mt-4 p-3 bg-gray-100 dark:bg-gray-700 rounded-lg">
                  <div className="flex justify-between items-center mb-2">
                    <h3 className="font-semibold">Debug Controls</h3>
                    <button
                      onClick={() => setShowDebugPanel(false)}
                      className="text-xs bg-gray-200 dark:bg-gray-600 px-2 py-1 rounded"
                    >
                      Hide
                    </button>
                  </div>

                  <div className="mb-3">
                    <h4 className="text-sm font-medium mb-1">Mode</h4>
                    <div className="flex flex-wrap gap-1">
                      <button onClick={() => setMode('idle')} className={`px-2 py-1 text-xs rounded ${mode === 'idle' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Idle</button>
                      <button onClick={() => setMode('listening')} className={`px-2 py-1 text-xs rounded ${mode === 'listening' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Listening</button>
                      <button onClick={() => setMode('thinking')} className={`px-2 py-1 text-xs rounded ${mode === 'thinking' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Thinking</button>
                      <button onClick={() => setMode('speaking')} className={`px-2 py-1 text-xs rounded ${mode === 'speaking' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Speaking</button>
                      <button onClick={() => setMode('error')} className={`px-2 py-1 text-xs rounded ${mode === 'error' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Error</button>
                    </div>
                  </div>

                  <div>
                    <h4 className="text-sm font-medium mb-1">Emotion</h4>
                    <div className="flex flex-wrap gap-1">
                      <button onClick={() => setEmotionContext('neutral')} className={`px-2 py-1 text-xs rounded ${emotionContext === 'neutral' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Neutral</button>
                      <button onClick={() => setEmotionContext('playful')} className={`px-2 py-1 text-xs rounded ${emotionContext === 'playful' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Playful</button>
                      <button onClick={() => setEmotionContext('supportive')} className={`px-2 py-1 text-xs rounded ${emotionContext === 'supportive' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Supportive</button>
                      <button onClick={() => setEmotionContext('concerned')} className={`px-2 py-1 text-xs rounded ${emotionContext === 'concerned' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Concerned</button>
                      <button onClick={() => setEmotionContext('witty')} className={`px-2 py-1 text-xs rounded ${emotionContext === 'witty' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Witty</button>
                      <button onClick={() => setEmotionContext('focused')} className={`px-2 py-1 text-xs rounded ${emotionContext === 'focused' ? 'bg-blue-500 text-white' : 'bg-gray-200 dark:bg-gray-600'}`}>Focused</button>
                    </div>
                  </div>
                </div>
              )}

              {!showDebugPanel && (
                <button
                  onClick={() => setShowDebugPanel(true)}
                  className="mt-4 text-xs bg-gray-200 dark:bg-gray-700 px-2 py-1 rounded w-full"
                >
                  Show Debug Controls
                </button>
              )}
            </div>

            <div className="card p-4">
              <VoiceControls sendMessage={sendMessage} />
            </div>
          </div>

          {/* Second column */}
          <div className="lg:col-span-2 space-y-6">
            <div className="card p-4 h-64">
              <PerformanceMonitor />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div className="card p-4 h-64">
                <MemoryViewer />
              </div>

              <div className="card p-4 h-64">
                <div className="h-full">
                  <h2 className="text-xl font-bold mb-4">Settings</h2>

                  <div className="space-y-4">
                    <div>
                      <h3 className="text-lg font-semibold mb-2">About</h3>
                      <p className="text-sm" style={{ color: 'var(--text-color)' }}>
                        Coda Dashboard v2.0
                      </p>
                      <p className="text-xs mt-1" style={{ color: 'var(--text-color)' }}>
                        Built with React, Tailwind CSS, and WebSockets
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="card p-4 h-96">
              <ConversationView />
            </div>
          </div>
        </div>
      </Layout>
  );
}

export default App;
