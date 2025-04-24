import React, { memo } from 'react';

interface PerformanceMetrics {
  stt: number;
  llm: number;
  tts: number;
  total: number;
  stt_audio: number;
  tts_audio: number;
  tool_seconds: number;
  memory_seconds: number;
}

interface SystemMetrics {
  memory_mb: number;
  cpu_percent: number;
  gpu_vram_mb: number;
}

interface PerformanceMonitorProps {
  performanceMetrics: PerformanceMetrics;
  systemMetrics: SystemMetrics;
}

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  performanceMetrics,
  systemMetrics
}) => {
  // Format seconds to a readable format with 2 decimal places
  const formatSeconds = (seconds: number) => {
    return seconds.toFixed(2) + 's';
  };

  // Calculate the percentage of each component in the total processing time
  const calculatePercentage = (value: number) => {
    if (!performanceMetrics.total) return 0;
    return (value / performanceMetrics.total) * 100;
  };

  return (
    <div className="card p-4">
      <h2 className="text-xl font-bold mb-4">Performance Metrics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-dark-600 p-3 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">Processing Time</h3>
          
          <div className="space-y-2">
            <div>
              <div className="flex justify-between mb-1">
                <span>Speech-to-Text</span>
                <span>{formatSeconds(performanceMetrics.stt)}</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${calculatePercentage(performanceMetrics.stt)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span>Language Model</span>
                <span>{formatSeconds(performanceMetrics.llm)}</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: `${calculatePercentage(performanceMetrics.llm)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span>Text-to-Speech</span>
                <span>{formatSeconds(performanceMetrics.tts)}</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full" 
                  style={{ width: `${calculatePercentage(performanceMetrics.tts)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span>Tools</span>
                <span>{formatSeconds(performanceMetrics.tool_seconds)}</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-purple-500 h-2 rounded-full" 
                  style={{ width: `${calculatePercentage(performanceMetrics.tool_seconds)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span>Memory</span>
                <span>{formatSeconds(performanceMetrics.memory_seconds)}</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-pink-500 h-2 rounded-full" 
                  style={{ width: `${calculatePercentage(performanceMetrics.memory_seconds)}%` }}
                ></div>
              </div>
            </div>
            
            <div className="mt-3 pt-2 border-t border-dark-500">
              <div className="flex justify-between font-semibold">
                <span>Total Processing</span>
                <span>{formatSeconds(performanceMetrics.total)}</span>
              </div>
            </div>
          </div>
        </div>
        
        <div className="bg-dark-600 p-3 rounded-lg">
          <h3 className="text-lg font-semibold mb-2">System Resources</h3>
          
          <div className="space-y-2">
            <div>
              <div className="flex justify-between mb-1">
                <span>CPU Usage</span>
                <span>{systemMetrics.cpu_percent.toFixed(1)}%</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-blue-500 h-2 rounded-full" 
                  style={{ width: `${systemMetrics.cpu_percent}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span>Memory Usage</span>
                <span>{systemMetrics.memory_mb.toFixed(0)} MB</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-green-500 h-2 rounded-full" 
                  style={{ width: `${Math.min((systemMetrics.memory_mb / 8000) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            
            <div>
              <div className="flex justify-between mb-1">
                <span>GPU VRAM</span>
                <span>{systemMetrics.gpu_vram_mb.toFixed(0)} MB</span>
              </div>
              <div className="w-full bg-dark-500 rounded-full h-2">
                <div 
                  className="bg-yellow-500 h-2 rounded-full" 
                  style={{ width: `${Math.min((systemMetrics.gpu_vram_mb / 8000) * 100, 100)}%` }}
                ></div>
              </div>
            </div>
            
            <div className="mt-3 pt-2 border-t border-dark-500">
              <div className="flex justify-between">
                <span>Audio Duration</span>
                <span>
                  Input: {formatSeconds(performanceMetrics.stt_audio)} | 
                  Output: {formatSeconds(performanceMetrics.tts_audio)}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(PerformanceMonitor);
