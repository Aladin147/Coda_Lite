import React from 'react';

function Dashboard({ connected, performanceMetrics, systemMetrics }) {
  return (
    <div className="dashboard">
      <div className="card">
        <div className="card-title">
          <span>Connection Status</span>
        </div>
        <div className="connection-status">
          <div className={`status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`}></div>
          <span>{connected ? 'Connected to Coda' : 'Disconnected from Coda'}</span>
        </div>
      </div>
      
      <div className="card">
        <div className="card-title">
          <span>Performance Metrics</span>
        </div>
        <div className="metric">
          <span className="metric-label">STT Latency</span>
          <span className="metric-value">{performanceMetrics.stt.toFixed(2)}s</span>
        </div>
        <div className="metric">
          <span className="metric-label">LLM Latency</span>
          <span className="metric-value">{performanceMetrics.llm.toFixed(2)}s</span>
        </div>
        <div className="metric">
          <span className="metric-label">TTS Latency</span>
          <span className="metric-value">{performanceMetrics.tts.toFixed(2)}s</span>
        </div>
        <div className="metric">
          <span className="metric-label">Total Latency</span>
          <span className="metric-value">{performanceMetrics.total.toFixed(2)}s</span>
        </div>
      </div>
      
      <div className="card">
        <div className="card-title">
          <span>System Metrics</span>
        </div>
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
