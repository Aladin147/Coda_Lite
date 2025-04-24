import React, { useState, useEffect } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

function PerformanceMonitor({ performanceMetrics, systemMetrics }) {
  const [latencyHistory, setLatencyHistory] = useState([]);
  const [systemHistory, setSystemHistory] = useState([]);

  useEffect(() => {
    // Add current performance metrics to history
    if (performanceMetrics.total > 0) {
      const timestamp = new Date().toLocaleTimeString();
      setLatencyHistory(prev => {
        const newHistory = [...prev, {
          timestamp,
          stt: performanceMetrics.stt,
          llm: performanceMetrics.llm,
          tts: performanceMetrics.tts,
          total: performanceMetrics.total,
          stt_audio: performanceMetrics.stt_audio,
          tts_audio: performanceMetrics.tts_audio
        }];

        // Keep only the last 20 data points
        if (newHistory.length > 20) {
          return newHistory.slice(newHistory.length - 20);
        }
        return newHistory;
      });
    }
  }, [performanceMetrics]);

  useEffect(() => {
    // Add current system metrics to history
    if (systemMetrics.memory_mb > 0) {
      const timestamp = new Date().toLocaleTimeString();
      setSystemHistory(prev => {
        const newHistory = [...prev, {
          timestamp,
          memory: systemMetrics.memory_mb,
          cpu: systemMetrics.cpu_percent,
          gpu: systemMetrics.gpu_vram_mb
        }];

        // Keep only the last 20 data points
        if (newHistory.length > 20) {
          return newHistory.slice(newHistory.length - 20);
        }
        return newHistory;
      });
    }
  }, [systemMetrics]);

  return (
    <div className="performance-monitor">
      <div className="card">
        <div className="card-title">
          <span>Latency Metrics</span>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={latencyHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis />
              <Tooltip />
              <Legend />
              <Line type="monotone" dataKey="stt" stroke="#8884d8" name="STT Processing" />
              <Line type="monotone" dataKey="llm" stroke="#82ca9d" name="LLM Generation" />
              <Line type="monotone" dataKey="tts" stroke="#ffc658" name="TTS Synthesis" />
              <Line type="monotone" dataKey="total" stroke="#ff8042" name="Total Processing" />
              <Line type="monotone" dataKey="stt_audio" stroke="#b388ff" name="User Speaking" strokeDasharray="5 5" />
              <Line type="monotone" dataKey="tts_audio" stroke="#ffb74d" name="Coda Speaking" strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      <div className="card">
        <div className="card-title">
          <span>System Metrics</span>
        </div>
        <div className="chart-container">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={systemHistory}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="timestamp" />
              <YAxis yAxisId="left" />
              <YAxis yAxisId="right" orientation="right" />
              <Tooltip />
              <Legend />
              <Line yAxisId="left" type="monotone" dataKey="memory" stroke="#8884d8" name="Memory (MB)" />
              <Line yAxisId="right" type="monotone" dataKey="cpu" stroke="#82ca9d" name="CPU (%)" />
              {systemMetrics.gpu_vram_mb > 0 && (
                <Line yAxisId="left" type="monotone" dataKey="gpu" stroke="#ffc658" name="GPU VRAM (MB)" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>
    </div>
  );
}

export default PerformanceMonitor;
