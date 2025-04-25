import React, { useState, useEffect } from 'react';
import { useEvents } from '../store/selectors';

interface PerformanceMetrics {
  stt: number;
  llm: number;
  tts: number;
  total: number;
}

const PerformanceMonitor: React.FC = () => {
  const { events } = useEvents();
  const [metrics, setMetrics] = useState<PerformanceMetrics>({
    stt: 0,
    llm: 0,
    tts: 0,
    total: 0
  });
  
  // Format time in milliseconds to a readable format
  const formatTime = (ms: number): string => {
    if (ms < 1) return '0ms';
    if (ms < 1000) return `${Math.round(ms)}ms`;
    return `${(ms / 1000).toFixed(2)}s`;
  };
  
  // Calculate performance metrics from events
  useEffect(() => {
    // Find the latest latency trace event
    const latencyEvents = events.filter(event => event.type === 'latency_trace');
    
    if (latencyEvents.length > 0) {
      const latestEvent = latencyEvents[latencyEvents.length - 1];
      
      // Extract metrics from the event
      const stt = latestEvent.stt_ms || 0;
      const llm = latestEvent.llm_ms || 0;
      const tts = latestEvent.tts_ms || 0;
      const total = stt + llm + tts;
      
      setMetrics({ stt, llm, tts, total });
    }
  }, [events]);
  
  return (
    <div className="h-full">
      <h2 className="text-xl font-bold mb-4">Performance</h2>
      
      <div className="space-y-4">
        <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Processing Time</h3>
          
          <div className="space-y-2">
            <div className="flex justify-between items-center">
              <span>Speech Recognition:</span>
              <span className="font-mono">{formatTime(metrics.stt)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span>LLM Generation:</span>
              <span className="font-mono">{formatTime(metrics.llm)}</span>
            </div>
            
            <div className="flex justify-between items-center">
              <span>TTS Synthesis:</span>
              <span className="font-mono">{formatTime(metrics.tts)}</span>
            </div>
            
            <div className="h-px bg-gray-300 dark:bg-gray-600 my-2"></div>
            
            <div className="flex justify-between items-center font-semibold">
              <span>Total Processing:</span>
              <span className="font-mono">{formatTime(metrics.total)}</span>
            </div>
          </div>
        </div>
        
        <div className="bg-gray-100 dark:bg-gray-700 p-4 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Latency Breakdown</h3>
          
          <div className="h-6 w-full bg-gray-200 dark:bg-gray-800 rounded overflow-hidden">
            {metrics.total > 0 && (
              <>
                <div 
                  className="h-full bg-green-500 float-left" 
                  style={{ width: `${(metrics.stt / metrics.total) * 100}%` }}
                  title={`STT: ${formatTime(metrics.stt)}`}
                ></div>
                <div 
                  className="h-full bg-blue-500 float-left" 
                  style={{ width: `${(metrics.llm / metrics.total) * 100}%` }}
                  title={`LLM: ${formatTime(metrics.llm)}`}
                ></div>
                <div 
                  className="h-full bg-purple-500 float-left" 
                  style={{ width: `${(metrics.tts / metrics.total) * 100}%` }}
                  title={`TTS: ${formatTime(metrics.tts)}`}
                ></div>
              </>
            )}
          </div>
          
          <div className="flex justify-between text-xs mt-1">
            <div className="flex items-center">
              <div className="w-3 h-3 bg-green-500 rounded-full mr-1"></div>
              <span>STT</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-blue-500 rounded-full mr-1"></div>
              <span>LLM</span>
            </div>
            <div className="flex items-center">
              <div className="w-3 h-3 bg-purple-500 rounded-full mr-1"></div>
              <span>TTS</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default PerformanceMonitor;
