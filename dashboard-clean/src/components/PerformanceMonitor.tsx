import React from 'react';
import { usePerformanceMetrics } from '../store/selectors';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

const PerformanceMonitor: React.FC = () => {
  const { metrics } = usePerformanceMetrics();
  
  // Prepare data for the chart
  const chartData = [
    { name: 'STT', value: metrics.sttLatency },
    { name: 'LLM', value: metrics.llmLatency },
    { name: 'TTS', value: metrics.ttsLatency },
    { name: 'Total', value: metrics.totalLatency }
  ];
  
  return (
    <div className="card p-4 h-96 flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Performance Metrics</h2>
      
      <div className="grid grid-cols-2 gap-4 mb-4">
        <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(59, 130, 246, 0.2)' }}>
          <div className="text-sm opacity-70">STT Latency</div>
          <div className="text-2xl font-semibold">{metrics.sttLatency.toFixed(2)} ms</div>
        </div>
        
        <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(16, 227, 176, 0.2)' }}>
          <div className="text-sm opacity-70">LLM Latency</div>
          <div className="text-2xl font-semibold">{metrics.llmLatency.toFixed(2)} ms</div>
        </div>
        
        <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(157, 92, 255, 0.2)' }}>
          <div className="text-sm opacity-70">TTS Latency</div>
          <div className="text-2xl font-semibold">{metrics.ttsLatency.toFixed(2)} ms</div>
        </div>
        
        <div className="p-3 rounded-lg" style={{ backgroundColor: 'rgba(255, 199, 44, 0.2)' }}>
          <div className="text-sm opacity-70">Total Latency</div>
          <div className="text-2xl font-semibold">{metrics.totalLatency.toFixed(2)} ms</div>
        </div>
      </div>
      
      <div className="flex-1">
        <ResponsiveContainer width="100%" height="100%">
          <BarChart data={chartData} margin={{ top: 20, right: 30, left: 20, bottom: 20 }}>
            <XAxis dataKey="name" stroke="var(--text-color)" />
            <YAxis stroke="var(--text-color)" />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: 'var(--card-background)', 
                border: '1px solid var(--border-color)',
                color: 'var(--text-color)'
              }} 
            />
            <Bar dataKey="value" fill="var(--color-primary-500)" />
          </BarChart>
        </ResponsiveContainer>
      </div>
      
      <div className="mt-4 flex justify-end">
        <button 
          className="btn btn-secondary"
          onClick={() => {
            // Simulate updating metrics with random values
            const sttLatency = Math.random() * 100 + 50;
            const llmLatency = Math.random() * 500 + 200;
            const ttsLatency = Math.random() * 200 + 100;
            const totalLatency = sttLatency + llmLatency + ttsLatency;
            
            usePerformanceMetrics.getState().updateMetrics({
              sttLatency,
              llmLatency,
              ttsLatency,
              totalLatency
            });
          }}
        >
          Simulate Update
        </button>
      </div>
    </div>
  );
};

export default PerformanceMonitor;
