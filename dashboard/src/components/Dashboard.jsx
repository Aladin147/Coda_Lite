import React, { useState, useEffect } from 'react';
import '../styles/Dashboard.css';

function Dashboard({ connected, performanceMetrics, systemMetrics, events }) {
  const [componentTimings, setComponentTimings] = useState({
    stt: { process: 0 },
    llm: { generate_response: 0 },
    tts: { synthesize: 0 },
    tool: { execute: 0 },
    memory: { retrieve: 0 }
  });

  // Process component timing events
  useEffect(() => {
    if (!events || events.length === 0) return;

    const timingEvents = events.filter(e => e.type === 'component_timing');
    if (timingEvents.length === 0) return;

    // Process the timing events
    const newTimings = { ...componentTimings };

    timingEvents.forEach(event => {
      const { component, operation, duration_seconds } = event.data;

      if (!newTimings[component]) {
        newTimings[component] = {};
      }

      newTimings[component][operation] = duration_seconds;
    });

    setComponentTimings(newTimings);
  }, [events]);

  // Calculate the real total conversation time (including speaking and thinking)
  const calculateTotalTime = () => {
    // Processing time (excluding audio playback/recording)
    const processingTime = performanceMetrics.total;

    // Audio durations
    const userSpeakingTime = performanceMetrics.stt_audio;
    const codaSpeakingTime = performanceMetrics.tts_audio;

    // Total time is user speaking + processing + Coda speaking
    // This avoids double-counting the processing time
    return userSpeakingTime + processingTime + codaSpeakingTime;
  };

  // Format time with appropriate units (ms for small values, s for larger values)
  const formatTime = (seconds) => {
    if (seconds < 0.01) {
      return `${(seconds * 1000).toFixed(0)}ms`;
    } else if (seconds < 0.1) {
      return `${(seconds * 1000).toFixed(1)}ms`;
    } else {
      return `${seconds.toFixed(2)}s`;
    }
  };

  return (
    <div className="dashboard">
      <div className="metrics-group">
        <div className="metrics-section">
          <h4>Processing Time</h4>
          <div className="metric">
            <span className="metric-label">STT Processing</span>
            <span className="metric-value">{formatTime(performanceMetrics.stt)}</span>
          </div>
          <div className="metric">
            <span className="metric-label">LLM Generation</span>
            <span className="metric-value">{formatTime(performanceMetrics.llm)}</span>
          </div>
          <div className="metric">
            <span className="metric-label">TTS Synthesis</span>
            <span className="metric-value">{formatTime(performanceMetrics.tts)}</span>
          </div>
          {performanceMetrics.tool_seconds > 0 && (
            <div className="metric">
              <span className="metric-label">Tool Execution</span>
              <span className="metric-value">{formatTime(performanceMetrics.tool_seconds)}</span>
            </div>
          )}
          {performanceMetrics.memory_seconds > 0 && (
            <div className="metric">
              <span className="metric-label">Memory Operations</span>
              <span className="metric-value">{formatTime(performanceMetrics.memory_seconds)}</span>
            </div>
          )}
          <div className="metric total-metric">
            <span className="metric-label">Total Processing</span>
            <span className="metric-value">{formatTime(performanceMetrics.total)}</span>
          </div>
        </div>

        <div className="metrics-section">
          <h4>Audio Duration</h4>
          <div className="metric">
            <span className="metric-label">User Speaking</span>
            <span className="metric-value">{formatTime(performanceMetrics.stt_audio)}</span>
          </div>
          <div className="metric">
            <span className="metric-label">Coda Speaking</span>
            <span className="metric-value">{formatTime(performanceMetrics.tts_audio)}</span>
          </div>
          <div className="metric total-metric">
            <span className="metric-label">Total Conversation</span>
            <span className="metric-value">{formatTime(calculateTotalTime())}</span>
          </div>
        </div>
      </div>

      <div className="metrics-section system-metrics">
        <h4>System Resources</h4>
        <div className="metric">
          <span className="metric-label">Memory Usage</span>
          <span className="metric-value">{systemMetrics.memory_mb.toFixed(1)} MB</span>
        </div>
        <div className="metric">
          <span className="metric-label">CPU Usage</span>
          <span className="metric-value">{systemMetrics.cpu_percent.toFixed(1)}%</span>
        </div>
        {systemMetrics.gpu_vram_mb > 0 && (
          <div className="metric">
            <span className="metric-label">GPU VRAM</span>
            <span className="metric-value">{systemMetrics.gpu_vram_mb.toFixed(1)} MB</span>
          </div>
        )}
      </div>
    </div>
  );
}

export default Dashboard;
