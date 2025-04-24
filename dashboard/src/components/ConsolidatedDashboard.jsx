import React, { useState } from 'react';
import Dashboard from './Dashboard';
import MemoryViewer from './MemoryViewer';
import ConversationView from './ConversationView';
import ToolDisplay from './ToolDisplay';
import EventLog from './EventLog';
import VoiceControls from './VoiceControls';
import Avatar from './Avatar';
import MemoryDebugPanel from './MemoryDebugPanel';
import EventInspector from './EventInspector';
import PerformanceVisualizer from './PerformanceVisualizer';
import '../styles/ConsolidatedDashboard.css';

/**
 * ConsolidatedDashboard component that displays all critical metrics on a single page
 * @param {Object} props - Component props
 * @param {boolean} props.connected - Whether the WebSocket is connected
 * @param {Array} props.events - Array of WebSocket events
 * @param {Object} props.performanceMetrics - Performance metrics data
 * @param {Object} props.systemMetrics - System metrics data
 * @param {Array} props.memories - Memory data
 * @param {Function} props.sendMessage - Function to send WebSocket messages
 */
function ConsolidatedDashboard({
  connected,
  events,
  performanceMetrics,
  systemMetrics,
  memories,
  sendMessage
}) {
  const [showEventLog, setShowEventLog] = useState(true);
  const [showMemoryDebug, setShowMemoryDebug] = useState(false);
  const [eventView, setEventView] = useState('log'); // 'log' or 'inspector'
  const [performanceView, setPerformanceView] = useState('metrics'); // 'metrics' or 'visualizer'
  return (
    <div className="consolidated-dashboard">
      <div className="dashboard-grid">
        {/* Row 1: Avatar and Controls */}
        <div className="grid-item avatar-section">
          <div className="section-header">
            <h3 className="section-title">Coda</h3>
          </div>
          <Avatar events={events || []} />
        </div>
        <div className="grid-item controls-section">
          <div className="section-header">
            <h3 className="section-title">Controls</h3>
          </div>
          <VoiceControls sendMessage={sendMessage} connected={connected} />
        </div>

        {/* Row 2: Performance Metrics and Memory */}
        <div className="grid-item performance-section">
          <div className="section-header">
            <h3 className="section-title">Performance Metrics</h3>
            <button
              className="toggle-button"
              onClick={() => setPerformanceView(performanceView === 'metrics' ? 'visualizer' : 'metrics')}
            >
              {performanceView === 'metrics' ? 'Show Trends' : 'Show Metrics'}
            </button>
          </div>
          {performanceView === 'metrics' ? (
            <Dashboard
              connected={connected}
              performanceMetrics={performanceMetrics}
              systemMetrics={systemMetrics}
              events={events || []}
            />
          ) : (
            <PerformanceVisualizer
              events={events || []}
            />
          )}
        </div>
        <div className="grid-item memory-section">
          <div className="section-header">
            <h3 className="section-title">Memory</h3>
            <button
              className="toggle-button"
              onClick={() => setShowMemoryDebug(!showMemoryDebug)}
            >
              {showMemoryDebug ? 'Basic View' : 'Debug View'}
            </button>
          </div>
          {showMemoryDebug ? (
            <MemoryDebugPanel
              events={events || []}
              sendMessage={sendMessage}
            />
          ) : (
            <MemoryViewer
              memories={(memories || []).slice(0, 5)}
              events={events || []}
            />
          )}
        </div>

        {/* Row 3: Conversation and Tools */}
        <div className="grid-item conversation-section">
          <ConversationView events={events || []} />
        </div>
        <div className="grid-item tools-section">
          <ToolDisplay events={events || []} />
        </div>

        {/* Row 4: Event Log */}
        <div className={`grid-item events-section ${showEventLog ? '' : 'hidden'}`}>
          <div className="section-header">
            <h3 className="section-title">Recent Events</h3>
            <div className="button-group">
              <button
                className={`toggle-button ${eventView === 'log' ? 'active' : ''}`}
                onClick={() => setEventView('log')}
              >
                Log
              </button>
              <button
                className={`toggle-button ${eventView === 'inspector' ? 'active' : ''}`}
                onClick={() => setEventView('inspector')}
              >
                Inspector
              </button>
              <button
                className="toggle-button"
                onClick={() => setShowEventLog(!showEventLog)}
              >
                {showEventLog ? 'Hide' : 'Show'}
              </button>
            </div>
          </div>
          {eventView === 'log' ? (
            <EventLog events={(events || []).slice(0, 10)} />
          ) : (
            <EventInspector events={events || []} />
          )}
        </div>
      </div>
    </div>
  );
}

export default ConsolidatedDashboard;
