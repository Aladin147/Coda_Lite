import React from 'react';

function Dashboard({ connected, performanceMetrics, systemMetrics }) {
  return (
    <div className="dashboard">
      <div className="metrics-group">
        <div className="metrics-section">
          <h4>Processing Time</h4>
          <div className="metric">
            <span className="metric-label">STT Processing</span>
            <span className="metric-value">{performanceMetrics.stt.toFixed(2)}s</span>
          </div>
          <div className="metric">
            <span className="metric-label">LLM Generation</span>
            <span className="metric-value">{performanceMetrics.llm.toFixed(2)}s</span>
          </div>
          <div className="metric">
            <span className="metric-label">TTS Synthesis</span>
            <span className="metric-value">{performanceMetrics.tts.toFixed(2)}s</span>
          </div>
          <div className="metric total-metric">
            <span className="metric-label">Total Processing</span>
            <span className="metric-value">{performanceMetrics.total.toFixed(2)}s</span>
          </div>
        </div>

        <div className="metrics-section">
          <h4>Audio Duration</h4>
          <div className="metric">
            <span className="metric-label">User Speaking</span>
            <span className="metric-value">{performanceMetrics.stt_audio.toFixed(2)}s</span>
          </div>
          <div className="metric">
            <span className="metric-label">Coda Speaking</span>
            <span className="metric-value">{performanceMetrics.tts_audio.toFixed(2)}s</span>
          </div>
          <div className="metric total-metric">
            <span className="metric-label">Total Conversation</span>
            <span className="metric-value">{(performanceMetrics.total + performanceMetrics.stt_audio + performanceMetrics.tts_audio).toFixed(2)}s</span>
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
