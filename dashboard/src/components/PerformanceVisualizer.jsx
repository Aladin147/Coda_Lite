import React, { useState, useEffect, useRef } from 'react';
import '../styles/PerformanceVisualizer.css';

/**
 * PerformanceVisualizer component for visualizing performance metrics
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 */
function PerformanceVisualizer({ events }) {
  const [performanceData, setPerformanceData] = useState([]);
  const [selectedMetric, setSelectedMetric] = useState('total');
  const [timeRange, setTimeRange] = useState('5m');
  const canvasRef = useRef(null);
  
  // Process performance events
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    // Filter latency trace events
    const latencyEvents = events.filter(e => e.type === 'latency_trace');
    if (latencyEvents.length === 0) return;
    
    // Extract performance data
    const data = latencyEvents.map(event => ({
      timestamp: new Date(event.timestamp),
      stt: event.data.stt_seconds || 0,
      llm: event.data.llm_seconds || 0,
      tts: event.data.tts_seconds || 0,
      total: event.data.total_seconds || 0,
      tool: event.data.tool_seconds || 0,
      memory: event.data.memory_seconds || 0,
      stt_audio: event.data.stt_audio_duration || 0,
      tts_audio: event.data.tts_audio_duration || 0
    }));
    
    // Sort by timestamp
    data.sort((a, b) => a.timestamp - b.timestamp);
    
    setPerformanceData(data);
  }, [events]);
  
  // Draw the performance chart
  useEffect(() => {
    if (!canvasRef.current || performanceData.length === 0) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const width = canvas.width;
    const height = canvas.height;
    
    // Clear the canvas
    ctx.clearRect(0, 0, width, height);
    
    // Filter data by time range
    const now = new Date();
    let cutoff = new Date();
    
    switch (timeRange) {
      case '1m':
        cutoff.setMinutes(now.getMinutes() - 1);
        break;
      case '5m':
        cutoff.setMinutes(now.getMinutes() - 5);
        break;
      case '15m':
        cutoff.setMinutes(now.getMinutes() - 15);
        break;
      case '1h':
        cutoff.setHours(now.getHours() - 1);
        break;
      case 'all':
      default:
        cutoff = new Date(0); // Beginning of time
        break;
    }
    
    const filteredData = performanceData.filter(d => d.timestamp >= cutoff);
    
    if (filteredData.length === 0) {
      // Draw "No data" message
      ctx.font = '14px Arial';
      ctx.fillStyle = 'var(--text-secondary)';
      ctx.textAlign = 'center';
      ctx.fillText('No data available for the selected time range', width / 2, height / 2);
      return;
    }
    
    // Get min and max values
    const values = filteredData.map(d => d[selectedMetric]);
    const maxValue = Math.max(...values) * 1.1; // Add 10% padding
    
    // Calculate scales
    const xScale = width / (filteredData.length - 1 || 1);
    const yScale = height / maxValue;
    
    // Draw axes
    ctx.strokeStyle = 'var(--border-color)';
    ctx.lineWidth = 1;
    
    // X-axis
    ctx.beginPath();
    ctx.moveTo(0, height);
    ctx.lineTo(width, height);
    ctx.stroke();
    
    // Y-axis
    ctx.beginPath();
    ctx.moveTo(0, 0);
    ctx.lineTo(0, height);
    ctx.stroke();
    
    // Draw grid lines
    ctx.strokeStyle = 'var(--border-color)';
    ctx.lineWidth = 0.5;
    ctx.setLineDash([5, 5]);
    
    // Horizontal grid lines
    const numGridLines = 5;
    for (let i = 1; i <= numGridLines; i++) {
      const y = height - (i * height / numGridLines);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(width, y);
      ctx.stroke();
      
      // Draw y-axis labels
      ctx.font = '10px Arial';
      ctx.fillStyle = 'var(--text-secondary)';
      ctx.textAlign = 'left';
      ctx.fillText(`${(i * maxValue / numGridLines).toFixed(2)}s`, 5, y - 5);
    }
    
    // Reset line dash
    ctx.setLineDash([]);
    
    // Draw data line
    ctx.strokeStyle = getMetricColor(selectedMetric);
    ctx.lineWidth = 2;
    ctx.beginPath();
    
    filteredData.forEach((d, i) => {
      const x = i * xScale;
      const y = height - (d[selectedMetric] * yScale);
      
      if (i === 0) {
        ctx.moveTo(x, y);
      } else {
        ctx.lineTo(x, y);
      }
    });
    
    ctx.stroke();
    
    // Draw data points
    ctx.fillStyle = getMetricColor(selectedMetric);
    
    filteredData.forEach((d, i) => {
      const x = i * xScale;
      const y = height - (d[selectedMetric] * yScale);
      
      ctx.beginPath();
      ctx.arc(x, y, 3, 0, Math.PI * 2);
      ctx.fill();
    });
    
    // Draw average line
    const avgValue = values.reduce((sum, val) => sum + val, 0) / values.length;
    const avgY = height - (avgValue * yScale);
    
    ctx.strokeStyle = 'var(--text-secondary)';
    ctx.lineWidth = 1;
    ctx.setLineDash([5, 5]);
    ctx.beginPath();
    ctx.moveTo(0, avgY);
    ctx.lineTo(width, avgY);
    ctx.stroke();
    
    // Draw average label
    ctx.font = '10px Arial';
    ctx.fillStyle = 'var(--text-secondary)';
    ctx.textAlign = 'left';
    ctx.fillText(`Avg: ${avgValue.toFixed(2)}s`, 5, avgY - 5);
    
    // Reset line dash
    ctx.setLineDash([]);
    
  }, [performanceData, selectedMetric, timeRange]);
  
  // Get color for metric
  const getMetricColor = (metric) => {
    switch (metric) {
      case 'stt':
        return 'var(--info-color)';
      case 'llm':
        return 'var(--primary-color)';
      case 'tts':
        return 'var(--success-color)';
      case 'total':
        return 'var(--warning-color)';
      case 'tool':
        return 'var(--secondary-color)';
      case 'memory':
        return 'var(--danger-color)';
      case 'stt_audio':
        return 'var(--info-color-light)';
      case 'tts_audio':
        return 'var(--success-color-light)';
      default:
        return 'var(--text-color)';
    }
  };
  
  // Get statistics for the selected metric
  const getStats = () => {
    if (performanceData.length === 0) {
      return { avg: 0, min: 0, max: 0, count: 0 };
    }
    
    // Filter data by time range
    const now = new Date();
    let cutoff = new Date();
    
    switch (timeRange) {
      case '1m':
        cutoff.setMinutes(now.getMinutes() - 1);
        break;
      case '5m':
        cutoff.setMinutes(now.getMinutes() - 5);
        break;
      case '15m':
        cutoff.setMinutes(now.getMinutes() - 15);
        break;
      case '1h':
        cutoff.setHours(now.getHours() - 1);
        break;
      case 'all':
      default:
        cutoff = new Date(0); // Beginning of time
        break;
    }
    
    const filteredData = performanceData.filter(d => d.timestamp >= cutoff);
    
    if (filteredData.length === 0) {
      return { avg: 0, min: 0, max: 0, count: 0 };
    }
    
    const values = filteredData.map(d => d[selectedMetric]);
    const avg = values.reduce((sum, val) => sum + val, 0) / values.length;
    const min = Math.min(...values);
    const max = Math.max(...values);
    
    return { avg, min, max, count: filteredData.length };
  };
  
  // Format time with appropriate units
  const formatTime = (seconds) => {
    if (seconds < 0.01) {
      return `${(seconds * 1000).toFixed(0)}ms`;
    } else if (seconds < 0.1) {
      return `${(seconds * 1000).toFixed(1)}ms`;
    } else {
      return `${seconds.toFixed(2)}s`;
    }
  };
  
  // Get stats for display
  const stats = getStats();
  
  return (
    <div className="performance-visualizer">
      <div className="visualizer-header">
        <h3>Performance Trends</h3>
        <div className="visualizer-controls">
          <select
            value={selectedMetric}
            onChange={(e) => setSelectedMetric(e.target.value)}
            className="metric-selector"
          >
            <option value="total">Total Processing</option>
            <option value="stt">STT Processing</option>
            <option value="llm">LLM Generation</option>
            <option value="tts">TTS Synthesis</option>
            <option value="tool">Tool Execution</option>
            <option value="memory">Memory Operations</option>
            <option value="stt_audio">User Speaking</option>
            <option value="tts_audio">Coda Speaking</option>
          </select>
          
          <select
            value={timeRange}
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-selector"
          >
            <option value="1m">Last Minute</option>
            <option value="5m">Last 5 Minutes</option>
            <option value="15m">Last 15 Minutes</option>
            <option value="1h">Last Hour</option>
            <option value="all">All Time</option>
          </select>
        </div>
      </div>
      
      <div className="stats-container">
        <div className="stat-card">
          <div className="stat-label">Average</div>
          <div className="stat-value" style={{ color: getMetricColor(selectedMetric) }}>
            {formatTime(stats.avg)}
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Minimum</div>
          <div className="stat-value" style={{ color: getMetricColor(selectedMetric) }}>
            {formatTime(stats.min)}
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Maximum</div>
          <div className="stat-value" style={{ color: getMetricColor(selectedMetric) }}>
            {formatTime(stats.max)}
          </div>
        </div>
        
        <div className="stat-card">
          <div className="stat-label">Data Points</div>
          <div className="stat-value">
            {stats.count}
          </div>
        </div>
      </div>
      
      <div className="chart-container">
        <canvas 
          ref={canvasRef}
          width={800}
          height={300}
          className="performance-chart"
        />
      </div>
    </div>
  );
}

export default PerformanceVisualizer;
