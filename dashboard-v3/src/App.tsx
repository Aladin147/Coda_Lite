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
import { MemoryDebugPanel } from './components/MemoryDebug';
import WebSocketClient from './WebSocketClient';
import { useMemoryDebugStore } from './store/memoryDebugStore';

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

  // Memory debug state
  const { addOperation, updateStats, setSearchResults } = useMemoryDebugStore();

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
          console.log('Received latency_trace event:', event.data);

          // Extract metrics with proper fallbacks and conversions
          const sttSeconds = parseFloat(event.data.stt_seconds || event.data.component_times?.stt || 0);
          const llmSeconds = parseFloat(event.data.llm_seconds || event.data.component_times?.llm || 0);
          const ttsSeconds = parseFloat(event.data.tts_seconds || event.data.component_times?.tts || 0);
          const toolSeconds = parseFloat(event.data.tool_seconds || event.data.component_times?.tools || 0);
          const memorySeconds = parseFloat(event.data.memory_seconds || event.data.component_times?.memory || 0);

          // Calculate total if not provided
          const totalSeconds = parseFloat(
            event.data.total_processing_seconds ||
            event.data.total_seconds ||
            (sttSeconds + llmSeconds + ttsSeconds + toolSeconds + memorySeconds) ||
            0
          );

          // Audio durations
          const sttAudioDuration = parseFloat(event.data.stt_audio_duration || event.data.audio_durations?.stt || 0);
          const ttsAudioDuration = parseFloat(event.data.tts_audio_duration || event.data.audio_durations?.tts || 0);

          // Update metrics with properly parsed values
          setPerformanceMetrics({
            stt: sttSeconds,
            llm: llmSeconds,
            tts: ttsSeconds,
            total: totalSeconds,
            stt_audio: sttAudioDuration,
            tts_audio: ttsAudioDuration,
            tool_seconds: toolSeconds,
            memory_seconds: memorySeconds
          });

          console.log('Updated performance metrics:', {
            stt: sttSeconds,
            llm: llmSeconds,
            tts: ttsSeconds,
            total: totalSeconds,
            stt_audio: sttAudioDuration,
            tts_audio: ttsAudioDuration,
            tool_seconds: toolSeconds,
            memory_seconds: memorySeconds
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
          console.log('Received memory_store event:', event.data);
          setMemories(prev => {
            const newMemories = [...prev];
            const existingIndex = newMemories.findIndex(m => m.id === event.data.memory_id);

            // Format the memory data to match the expected format in MemoryViewer
            const newMemory = {
              id: event.data.memory_id,
              content: event.data.content_preview || '',
              type: event.data.memory_type || 'unknown',
              importance: event.data.importance || 0,
              timestamp: event.timestamp || new Date().toISOString()
            };

            if (existingIndex >= 0) {
              newMemories[existingIndex] = newMemory;
            } else {
              newMemories.push(newMemory);
            }

            console.log('Updated memories:', newMemories);
            return newMemories.slice(0, 100);
          });
          break;

        case 'memory_retrieve':
          console.log('Received memory_retrieve event:', event.data);
          // If the event contains results, add them to the memories list
          if (event.data.results && Array.isArray(event.data.results)) {
            setMemories(prev => {
              const newMemories = [...prev];

              // Process each result and add it to the memories list
              event.data.results.forEach(result => {
                const memoryId = result.id || `mem-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
                const existingIndex = newMemories.findIndex(m => m.id === memoryId);

                // Format the memory data
                const memory = {
                  id: memoryId,
                  content: result.content || '',
                  type: result.metadata?.source_type || 'retrieved',
                  importance: result.metadata?.importance || result.score || 0.5,
                  timestamp: result.metadata?.timestamp || event.timestamp || new Date().toISOString()
                };

                if (existingIndex >= 0) {
                  newMemories[existingIndex] = memory;
                } else {
                  newMemories.push(memory);
                }
              });

              console.log('Updated memories after retrieval:', newMemories);
              return newMemories.slice(0, 100);
            });
          }
          break;
        case 'conversation_turn':
          // Add deduplication logic based on content and timestamp
          setMessages(prev => {
            // Generate a unique ID if one doesn't exist
            const messageId = event.data.turn_id || `msg-${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;

            const newMessage = {
              id: messageId,
              role: event.data.role,
              content: event.data.content,
              timestamp: event.timestamp || new Date().toISOString()
            };

            // Check for duplicates based on content and role (within a short time window)
            const isDuplicate = prev.some(m =>
              m.role === newMessage.role &&
              m.content === newMessage.content &&
              // Only consider it a duplicate if it's within 5 seconds
              Math.abs(new Date(m.timestamp).getTime() - new Date(newMessage.timestamp).getTime()) < 5000
            );

            // If it's a duplicate, don't add it
            if (isDuplicate) {
              console.log('Detected duplicate message, ignoring:', newMessage);
              return prev;
            }

            // Check if we already have this exact message ID
            const existingIndex = prev.findIndex(m => m.id === messageId);

            // Create a new array to avoid state mutation issues
            const newMessages = [...prev];

            if (existingIndex >= 0) {
              newMessages[existingIndex] = newMessage;
            } else {
              newMessages.push(newMessage);
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

        // Memory debug events
        case 'memory_debug_operation':
          console.log('Received memory_debug_operation event:', event.data);
          addOperation({
            timestamp: event.timestamp || new Date().toISOString(),
            operation_type: event.data.operation_type,
            details: event.data.details
          });
          break;

        case 'memory_debug_stats':
          console.log('Received memory_debug_stats event:', event.data);
          updateStats(event.data.stats);
          break;

        case 'memory_debug_search':
          console.log('Received memory_debug_search event:', event.data);
          const searchResults = event.data.results.map((result: any) => ({
            id: result.id,
            content: result.content,
            type: result.metadata?.source_type || result.type || 'unknown',
            importance: result.metadata?.importance || result.importance || 0.5,
            timestamp: result.metadata?.timestamp || event.timestamp || new Date().toISOString(),
            similarity: result.similarity || result.score || 0
          }));
          setSearchResults(searchResults, event.data.query);
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

          {/* Memory Debug Panel */}
          <MemoryDebugPanel />

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
