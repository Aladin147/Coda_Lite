import { useState, useEffect } from 'react';
import WebSocketClient from './WebSocketClient';
import Dashboard from './components/Dashboard';
import EventLog from './components/EventLog';
import PerformanceMonitor from './components/PerformanceMonitor';
import MemoryViewer from './components/MemoryViewer';
import Header from './components/Header';
import Avatar from './components/Avatar';
import ToolDisplay from './components/ToolDisplay';
import ConversationView from './components/ConversationView';
import VoiceControls from './components/VoiceControls';
import SystemInfo from './components/SystemInfo';
import ConsolidatedDashboard from './components/ConsolidatedDashboard';

function App() {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
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
  const [memories, setMemories] = useState([]);

  // Store for accumulating data between TTS end events
  const [currentMetrics, setCurrentMetrics] = useState({
    performance: {
      stt: 0,
      llm: 0,
      tts: 0,
      total: 0,
      stt_audio: 0,
      tts_audio: 0,
      tool_seconds: 0,
      memory_seconds: 0
    },
    system: {
      memory_mb: 0,
      cpu_percent: 0,
      gpu_vram_mb: 0
    },
    memories: []
  });

  useEffect(() => {
    const client = new WebSocketClient('ws://localhost:8765');

    client.onConnect = () => {
      console.log('Connected to WebSocket server');
      setConnected(true);
    };

    client.onDisconnect = () => {
      console.log('Disconnected from WebSocket server');
      setConnected(false);
    };

    client.onEvent = (event) => {
      // Add event to events list
      const newEvent = {
        type: event.type,
        data: event.data,
        timestamp: event.timestamp
      };

      setEvents(prevEvents => [newEvent, ...prevEvents].slice(0, 100));

      // Process specific event types for data storage
      switch (event.type) {
        case 'latency_trace':
          // Store metrics for later update
          setCurrentMetrics(prev => ({
            ...prev,
            performance: {
              stt: event.data.stt_seconds,
              llm: event.data.llm_seconds,
              tts: event.data.tts_seconds,
              total: event.data.total_seconds,
              stt_audio: event.data.stt_audio_duration || 0,
              tts_audio: event.data.tts_audio_duration || 0,
              tool_seconds: event.data.tool_seconds || 0,
              memory_seconds: event.data.memory_seconds || 0
            }
          }));

          // Also update immediately for real-time feedback
          setPerformanceMetrics({
            stt: event.data.stt_seconds,
            llm: event.data.llm_seconds,
            tts: event.data.tts_seconds,
            total: event.data.total_seconds,
            stt_audio: event.data.stt_audio_duration || 0,
            tts_audio: event.data.tts_audio_duration || 0,
            tool_seconds: event.data.tool_seconds || 0,
            memory_seconds: event.data.memory_seconds || 0
          });
          break;

        case 'system_metrics':
          // Store metrics for later update
          setCurrentMetrics(prev => ({
            ...prev,
            system: {
              memory_mb: event.data.memory_mb,
              cpu_percent: event.data.cpu_percent,
              gpu_vram_mb: event.data.gpu_vram_mb || 0
            }
          }));

          // Also update immediately for real-time feedback
          setSystemMetrics({
            memory_mb: event.data.memory_mb,
            cpu_percent: event.data.cpu_percent,
            gpu_vram_mb: event.data.gpu_vram_mb || 0
          });
          break;

        case 'memory_store':
          const newMemory = {
            id: event.data.memory_id,
            content: event.data.content_preview,
            type: event.data.memory_type,
            importance: event.data.importance,
            timestamp: event.timestamp
          };

          // Store for later update
          setCurrentMetrics(prev => ({
            ...prev,
            memories: [newMemory, ...prev.memories].slice(0, 50)
          }));

          // Also update immediately for real-time feedback
          setMemories(prevMemories => [newMemory, ...prevMemories].slice(0, 50));
          break;

        case 'tts_end':
          // Comprehensive update of all metrics at once
          console.log('TTS end event received - updating all dashboard components');

          // We already have the latest metrics from the individual events
          // This is where we would do any additional processing if needed
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

  const sendMessage = (type, data) => {
    // Create a WebSocket client if it doesn't exist
    if (!window.wsClient) {
      console.error('WebSocket client not initialized');
      return;
    }

    // Send the message if connected
    if (window.wsClient.isConnected()) {
      const message = {
        type,
        data,
        timestamp: new Date().toISOString()
      };

      try {
        window.wsClient.socket.send(JSON.stringify(message));
      } catch (error) {
        console.error('Error sending message:', error);
      }
    } else {
      console.error('WebSocket not connected');
    }
  };

  return (
    <div className="app">
      <Header
        connected={connected}
      />
      <main className="content">
        <ConsolidatedDashboard
          connected={connected}
          events={events}
          performanceMetrics={performanceMetrics}
          systemMetrics={systemMetrics}
          memories={memories}
          sendMessage={sendMessage}
        />
      </main>
      <footer className="app-footer">
        <SystemInfo events={events || []} />
      </footer>
    </div>
  );
}

export default App;
