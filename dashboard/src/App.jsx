import { useState, useEffect } from 'react';
import WebSocketClient from './WebSocketClient';
import Dashboard from './components/Dashboard';
import EventLog from './components/EventLog';
import PerformanceMonitor from './components/PerformanceMonitor';
import MemoryViewer from './components/MemoryViewer';
import Header from './components/Header';

function App() {
  const [connected, setConnected] = useState(false);
  const [events, setEvents] = useState([]);
  const [performanceMetrics, setPerformanceMetrics] = useState({
    stt: 0,
    llm: 0,
    tts: 0,
    total: 0
  });
  const [systemMetrics, setSystemMetrics] = useState({
    memory_mb: 0,
    cpu_percent: 0,
    gpu_vram_mb: 0
  });
  const [memories, setMemories] = useState([]);
  const [activeTab, setActiveTab] = useState('dashboard');

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
      setEvents(prevEvents => [event, ...prevEvents].slice(0, 100));
      
      // Process specific event types
      switch (event.type) {
        case 'latency_trace':
          setPerformanceMetrics({
            stt: event.data.stt_seconds,
            llm: event.data.llm_seconds,
            tts: event.data.tts_seconds,
            total: event.data.total_seconds
          });
          break;
          
        case 'system_metrics':
          setSystemMetrics({
            memory_mb: event.data.memory_mb,
            cpu_percent: event.data.cpu_percent,
            gpu_vram_mb: event.data.gpu_vram_mb || 0
          });
          break;
          
        case 'memory_store':
          setMemories(prevMemories => [
            {
              id: event.data.memory_id,
              content: event.data.content_preview,
              type: event.data.memory_type,
              importance: event.data.importance,
              timestamp: event.timestamp
            },
            ...prevMemories
          ].slice(0, 50));
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

  const renderContent = () => {
    switch (activeTab) {
      case 'dashboard':
        return <Dashboard 
          connected={connected} 
          performanceMetrics={performanceMetrics}
          systemMetrics={systemMetrics}
        />;
      case 'events':
        return <EventLog events={events} />;
      case 'performance':
        return <PerformanceMonitor 
          performanceMetrics={performanceMetrics}
          systemMetrics={systemMetrics}
        />;
      case 'memory':
        return <MemoryViewer memories={memories} />;
      default:
        return <Dashboard />;
    }
  };

  return (
    <div className="app">
      <Header 
        connected={connected} 
        activeTab={activeTab}
        onTabChange={setActiveTab}
      />
      <main className="content">
        {renderContent()}
      </main>
    </div>
  );
}

export default App;
