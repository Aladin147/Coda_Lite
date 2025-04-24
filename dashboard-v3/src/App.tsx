import { useCallback, useState, useEffect } from 'react';
import Layout from './components/Layout';
import Avatar from './components/Avatar';
import ConversationView from './components/ConversationView';
import PerformanceMonitor from './components/PerformanceMonitor';
import MemoryViewer from './components/MemoryViewer';
import VoiceControls from './components/VoiceControls';
import TextInput from './components/TextInput';
import ConnectionStatus from './components/ConnectionStatus';
import WebSocketDebugger from './components/WebSocketDebugger';
import WebSocketClient from './WebSocketClient';

function App() {
  // State for the application
  const [connected, setConnected] = useState(false);
  const [reconnecting, setReconnecting] = useState(false);
  const [reconnectAttempts, setReconnectAttempts] = useState(0);
  const [showDebugger, setShowDebugger] = useState(false);
  const [events, setEvents] = useState<any[]>([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    stt: 0,
    llm: 0,
    tts: 0,
    total: 0,
    stt_audio: 0,
    tts_audio: 0,
    tool_seconds: 0,
    memory_seconds: 0
  });
  const [systemMetrics, setSystemMetrics] = useState({
    memory_mb: 0,
    cpu_percent: 0,
    gpu_vram_mb: 0
  });
  const [memories, setMemories] = useState<any[]>([]);
  const [messages, setMessages] = useState<any[]>([]);
  const [mode, setMode] = useState<'idle' | 'listening' | 'thinking' | 'speaking' | 'error'>('idle');
  const [emotion, setEmotion] = useState<'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused'>('neutral');

  // Initialize WebSocket connection
  useEffect(() => {
    console.log('Initializing WebSocket connection');
    const client = new WebSocketClient('ws://localhost:8765');

    client.onConnect = () => {
      console.log('Connected to WebSocket server');
      setConnected(true);
      setReconnecting(false);
      setReconnectAttempts(0);
    };

    client.onDisconnect = () => {
      console.log('Disconnected from WebSocket server');
      setConnected(false);
    };

    client.onEvent = (event) => {
      console.log('Received event:', event);

      // Add event to events list
      const newEvent = {
        type: event.type,
        data: event.data,
        timestamp: event.timestamp
      };

      setEvents(prevEvents => [newEvent, ...prevEvents].slice(0, 100));

      // Process different event types
      switch (event.type) {
        case 'latency_trace':
          setPerformanceMetrics({
            stt: event.data.stt_seconds || 0,
            llm: event.data.llm_seconds || 0,
            tts: event.data.tts_seconds || 0,
            total: event.data.total_seconds || 0,
            stt_audio: event.data.stt_audio_duration || 0,
            tts_audio: event.data.tts_audio_duration || 0,
            tool_seconds: event.data.tool_seconds || 0,
            memory_seconds: event.data.memory_seconds || 0
          });
          break;
        case 'system_metrics':
          setSystemMetrics({
            memory_mb: event.data.memory_mb || 0,
            cpu_percent: event.data.cpu_percent || 0,
            gpu_vram_mb: event.data.gpu_vram_mb || 0
          });
          break;
        case 'memory_store':
          setMemories(prev => {
            const newMemories = [...prev];
            const existingIndex = newMemories.findIndex(m => m.memory_id === event.data.memory_id);

            if (existingIndex >= 0) {
              newMemories[existingIndex] = event.data;
            } else {
              newMemories.push(event.data);
            }

            return newMemories.slice(0, 100);
          });
          break;
        case 'conversation_message':
          setMessages(prev => {
            const newMessages = [...prev];
            const existingIndex = newMessages.findIndex(m => m.message_id === event.data.message_id);

            if (existingIndex >= 0) {
              newMessages[existingIndex] = event.data;
            } else {
              newMessages.push(event.data);
            }

            return newMessages.slice(0, 100);
          });
          break;
        case 'mode_change':
          setMode(event.data.mode);
          break;
        case 'emotion_change':
          setEmotion(event.data.emotion);
          break;
      }
    };

    // Connect to the WebSocket server
    client.connect();

    // Clean up on unmount
    return () => {
      client.disconnect();
    };
  }, []);

  // Function to send messages to the WebSocket server
  const sendMessage = useCallback((type: string, data: any = {}) => {
    // Check if the WebSocket client exists
    if (!(window as any).wsClient) {
      console.error('WebSocket client not initialized');
      return;
    }

    // Use the instrumented sendMessage method
    try {
      const messageId = (window as any).wsClient.sendMessage(type, data);
      console.log(`App: Message ${messageId} sent via WebSocketClient`);

      // Track the message source for debugging
      console.log(`App: Message source trace:`, {
        component: 'App',
        function: 'sendMessage',
        type,
        data,
        stack: new Error().stack
      });
    } catch (error) {
      console.error('App: Error sending message:', error);
    }
  }, []);

  // Toggle WebSocket debugger
  const toggleDebugger = useCallback(() => {
    setShowDebugger(prev => !prev);
  }, []);

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

  // Handler for text input
  const handleSendTextMessage = useCallback((text: string) => {
    console.log('Sending text message:', text);
    sendMessage('text_input', { text });
    console.log('Text message sent');
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

          <TextInput
            connected={connected}
            onSendMessage={handleSendTextMessage}
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

                    <button
                      onClick={toggleDebugger}
                      className="mt-4 px-3 py-1 bg-primary-600 hover:bg-primary-700 rounded-md transition-colors text-sm w-full"
                    >
                      {showDebugger ? 'Hide WebSocket Debugger' : 'Show WebSocket Debugger'}
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <ConversationView messages={messages} />

          {/* WebSocket Debugger (conditionally rendered) */}
          {showDebugger ? (
            <div className="mt-6">
              <WebSocketDebugger events={events} />
            </div>
          ) : null}
        </div>
      </div>
    </Layout>
  );
}

export default App;
