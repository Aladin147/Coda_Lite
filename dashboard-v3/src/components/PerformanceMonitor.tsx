import React, { memo, useState, useEffect, useRef } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer,
  PieChart, Pie, Cell, LineChart, Line, CartesianGrid
} from 'recharts';
import {
  formatSeconds,
  calculatePercentage,
  calculateResourcePercentage,
  calculateProcessingTime,
  calculateInteractionTime
} from '../utils/performanceUtils';

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

// Maximum number of history points to keep
const MAX_HISTORY_POINTS = 20;

const PerformanceMonitor: React.FC<PerformanceMonitorProps> = ({
  performanceMetrics,
  systemMetrics
}) => {
  // State for tracking historical data
  const [cpuHistory, setCpuHistory] = useState<Array<{ time: number; value: number }>>([]);
  const [memoryHistory, setMemoryHistory] = useState<Array<{ time: number; value: number }>>([]);
  const [processingHistory, setProcessingHistory] = useState<Array<{ time: number; value: number }>>([]);

  // State for view mode
  const [viewMode, setViewMode] = useState<'basic' | 'detailed'>('basic');

  // Ref to track if metrics have changed
  const prevMetricsRef = useRef<PerformanceMetrics | null>(null);

  // Update history when metrics change
  useEffect(() => {
    // Only update if metrics have changed and are not all zeros
    if (
      performanceMetrics.total > 0 &&
      JSON.stringify(prevMetricsRef.current) !== JSON.stringify(performanceMetrics)
    ) {
      const now = Date.now();

      // Update CPU history
      setCpuHistory(prev => {
        const newHistory = [...prev, { time: now, value: systemMetrics.cpu_percent }];
        return newHistory.slice(-MAX_HISTORY_POINTS);
      });

      // Update memory history
      setMemoryHistory(prev => {
        const newHistory = [...prev, { time: now, value: systemMetrics.memory_mb }];
        return newHistory.slice(-MAX_HISTORY_POINTS);
      });

      // Update processing time history
      setProcessingHistory(prev => {
        const newHistory = [...prev, { time: now, value: performanceMetrics.total }];
        return newHistory.slice(-MAX_HISTORY_POINTS);
      });

      // Update ref
      prevMetricsRef.current = { ...performanceMetrics };
    }
  }, [performanceMetrics, systemMetrics]);

  // Prepare data for pie chart
  const getPieChartData = () => {
    return [
      { name: 'STT', value: performanceMetrics.stt, color: '#10B981' }, // green-500
      { name: 'LLM', value: performanceMetrics.llm, color: '#3B82F6' }, // blue-500
      { name: 'TTS', value: performanceMetrics.tts, color: '#FBBF24' }, // yellow-500
      { name: 'Tools', value: performanceMetrics.tool_seconds, color: '#8B5CF6' }, // purple-500
      { name: 'Memory', value: performanceMetrics.memory_seconds, color: '#EC4899' }, // pink-500
    ].filter(item => item.value > 0); // Only include non-zero values
  };

  // Prepare data for bar chart
  const getBarChartData = () => {
    return [
      { name: 'STT', processing: performanceMetrics.stt, audio: performanceMetrics.stt_audio },
      { name: 'LLM', processing: performanceMetrics.llm, audio: 0 },
      { name: 'TTS', processing: performanceMetrics.tts, audio: performanceMetrics.tts_audio },
      { name: 'Tools', processing: performanceMetrics.tool_seconds, audio: 0 },
      { name: 'Memory', processing: performanceMetrics.memory_seconds, audio: 0 },
    ];
  };

  // Format history data for line charts
  const formatHistoryData = (history: Array<{ time: number; value: number }>) => {
    return history.map((point, index) => ({
      index,
      value: point.value,
      time: new Date(point.time).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })
    }));
  };

  return (
    <div className="card p-4">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Performance Metrics</h2>

        <div className="flex space-x-2">
          <button
            className={`px-3 py-1 rounded-md text-sm transition-colors ${
              viewMode === 'basic'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-600 text-gray-300 hover:bg-dark-500'
            }`}
            onClick={() => setViewMode('basic')}
          >
            Basic
          </button>
          <button
            className={`px-3 py-1 rounded-md text-sm transition-colors ${
              viewMode === 'detailed'
                ? 'bg-primary-600 text-white'
                : 'bg-dark-600 text-gray-300 hover:bg-dark-500'
            }`}
            onClick={() => setViewMode('detailed')}
          >
            Detailed
          </button>
        </div>
      </div>

      {viewMode === 'basic' ? (
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
                    style={{ width: `${calculatePercentage(performanceMetrics.stt, performanceMetrics.total)}%` }}
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
                    style={{ width: `${calculatePercentage(performanceMetrics.llm, performanceMetrics.total)}%` }}
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
                    style={{ width: `${calculatePercentage(performanceMetrics.tts, performanceMetrics.total)}%` }}
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
                    style={{ width: `${calculatePercentage(performanceMetrics.tool_seconds, performanceMetrics.total)}%` }}
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
                    style={{ width: `${calculatePercentage(performanceMetrics.memory_seconds, performanceMetrics.total)}%` }}
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
                    style={{ width: `${calculateResourcePercentage(systemMetrics.memory_mb)}%` }}
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
                    style={{ width: `${calculateResourcePercentage(systemMetrics.gpu_vram_mb)}%` }}
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
      ) : (
        <div className="space-y-6">
          {/* Processing Time Breakdown */}
          <div className="bg-dark-600 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">Processing Time Breakdown</h3>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Pie Chart */}
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={getPieChartData()}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                    >
                      {getPieChartData().map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} />
                      ))}
                    </Pie>
                    <Tooltip
                      formatter={(value: number) => formatSeconds(value)}
                      contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: 'white' }}
                    />
                    <Legend />
                  </PieChart>
                </ResponsiveContainer>
              </div>

              {/* Bar Chart */}
              <div className="h-64">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart
                    data={getBarChartData()}
                    margin={{ top: 10, right: 30, left: 0, bottom: 0 }}
                  >
                    <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                    <XAxis dataKey="name" stroke="#9CA3AF" />
                    <YAxis stroke="#9CA3AF" tickFormatter={(value) => formatSeconds(value)} />
                    <Tooltip
                      formatter={(value: number) => formatSeconds(value)}
                      contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: 'white' }}
                    />
                    <Legend />
                    <Bar dataKey="processing" name="Processing" fill="#3B82F6" />
                    <Bar dataKey="audio" name="Audio" fill="#10B981" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-4">
              <div className="bg-dark-700 p-3 rounded-lg">
                <div className="text-sm text-gray-400">Processing Time</div>
                <div className="text-xl font-semibold">{formatSeconds(performanceMetrics.total)}</div>
              </div>

              <div className="bg-dark-700 p-3 rounded-lg">
                <div className="text-sm text-gray-400">Audio Duration</div>
                <div className="text-xl font-semibold">{formatSeconds(performanceMetrics.stt_audio + performanceMetrics.tts_audio)}</div>
              </div>

              <div className="bg-dark-700 p-3 rounded-lg">
                <div className="text-sm text-gray-400">Total Interaction</div>
                <div className="text-xl font-semibold">{formatSeconds(calculateInteractionTime(performanceMetrics))}</div>
              </div>
            </div>
          </div>

          {/* Historical Performance */}
          <div className="bg-dark-600 p-4 rounded-lg">
            <h3 className="text-lg font-semibold mb-3">Historical Performance</h3>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
              {/* Processing Time History */}
              <div>
                <h4 className="text-md font-medium mb-2">Processing Time History</h4>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={formatHistoryData(processingHistory)}
                      margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="time" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" tickFormatter={(value) => `${value.toFixed(1)}s`} />
                      <Tooltip
                        formatter={(value: number) => `${value.toFixed(2)}s`}
                        contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: 'white' }}
                      />
                      <Line type="monotone" dataKey="value" stroke="#3B82F6" activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              {/* CPU Usage History */}
              <div>
                <h4 className="text-md font-medium mb-2">CPU Usage History</h4>
                <div className="h-48">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart
                      data={formatHistoryData(cpuHistory)}
                      margin={{ top: 5, right: 30, left: 0, bottom: 5 }}
                    >
                      <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
                      <XAxis dataKey="time" stroke="#9CA3AF" />
                      <YAxis stroke="#9CA3AF" tickFormatter={(value) => `${value.toFixed(0)}%`} />
                      <Tooltip
                        formatter={(value: number) => `${value.toFixed(1)}%`}
                        contentStyle={{ backgroundColor: '#1F2937', borderColor: '#374151', color: 'white' }}
                      />
                      <Line type="monotone" dataKey="value" stroke="#10B981" activeDot={{ r: 8 }} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(PerformanceMonitor);
