import React from 'react';
import { useMemoryDebugStats } from '../../store/memoryDebugStore';

/**
 * Memory Statistics Display component
 * 
 * This component displays:
 * - Short-term memory statistics
 * - Long-term memory statistics
 * - Memory operations statistics
 * - Memory type distribution
 */
const MemoryStatsDisplay: React.FC = () => {
  const { stats } = useMemoryDebugStats();

  if (!stats) {
    return (
      <div className="flex items-center justify-center h-64 text-gray-400">
        <p>No memory statistics available yet.</p>
      </div>
    );
  }

  // Format timestamp
  const formatTime = (timestamp: number) => {
    try {
      const date = new Date(timestamp * 1000);
      return date.toLocaleTimeString();
    } catch (e) {
      return 'Unknown';
    }
  };

  // Calculate memory usage percentage
  const shortTermUsage = stats.short_term.max_turns > 0
    ? (stats.short_term.turn_count / stats.short_term.max_turns) * 100
    : 0;

  const longTermUsage = stats.long_term.max_memories > 0
    ? (stats.long_term.memory_count / stats.long_term.max_memories) * 100
    : 0;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {/* Short-term memory stats */}
        <div className="bg-dark-700 p-3 rounded-lg">
          <h3 className="text-md font-semibold mb-2">Short-term Memory</h3>
          
          <div className="mb-2">
            <div className="flex justify-between text-sm mb-1">
              <span>Conversation Turns</span>
              <span>{stats.short_term.turn_count} / {stats.short_term.max_turns}</span>
            </div>
            <div className="w-full bg-dark-600 rounded-full h-2">
              <div 
                className="bg-primary-500 h-2 rounded-full" 
                style={{ width: `${Math.min(shortTermUsage, 100)}%` }}
              ></div>
            </div>
          </div>
          
          <div className="text-xs text-gray-400">
            {shortTermUsage.toFixed(1)}% of capacity used
          </div>
        </div>

        {/* Long-term memory stats */}
        <div className="bg-dark-700 p-3 rounded-lg">
          <h3 className="text-md font-semibold mb-2">Long-term Memory</h3>
          
          <div className="mb-2">
            <div className="flex justify-between text-sm mb-1">
              <span>Memories Stored</span>
              <span>{stats.long_term.memory_count} / {stats.long_term.max_memories}</span>
            </div>
            <div className="w-full bg-dark-600 rounded-full h-2">
              <div 
                className="bg-primary-500 h-2 rounded-full" 
                style={{ width: `${Math.min(longTermUsage, 100)}%` }}
              ></div>
            </div>
          </div>
          
          <div className="text-xs text-gray-400">
            {longTermUsage.toFixed(1)}% of capacity used
          </div>
        </div>
      </div>

      {/* Memory type distribution */}
      {stats.long_term.memory_types && Object.keys(stats.long_term.memory_types).length > 0 && (
        <div className="bg-dark-700 p-3 rounded-lg">
          <h3 className="text-md font-semibold mb-3">Memory Type Distribution</h3>
          
          <div className="grid grid-cols-2 gap-3">
            {Object.entries(stats.long_term.memory_types).map(([type, count]) => (
              <div key={type} className="flex items-center">
                <div className="w-3 h-3 rounded-full mr-2" style={{ backgroundColor: getMemoryTypeColor(type) }}></div>
                <div className="flex-1">
                  <div className="flex justify-between text-sm">
                    <span>{type}</span>
                    <span>{count}</span>
                  </div>
                  <div className="w-full bg-dark-600 rounded-full h-1.5 mt-1">
                    <div 
                      className="h-1.5 rounded-full" 
                      style={{ 
                        width: `${(count / stats.long_term.memory_count) * 100}%`,
                        backgroundColor: getMemoryTypeColor(type)
                      }}
                    ></div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Operations stats */}
      {stats.debug && (
        <div className="bg-dark-700 p-3 rounded-lg">
          <h3 className="text-md font-semibold mb-2">Operations</h3>
          
          <div className="grid grid-cols-2 gap-x-4 gap-y-2 mb-2">
            <div className="flex justify-between text-sm">
              <span>Total Operations</span>
              <span>{stats.debug.operations_count}</span>
            </div>
            
            <div className="flex justify-between text-sm">
              <span>Last Update</span>
              <span>{formatTime(stats.debug.last_update)}</span>
            </div>
          </div>
          
          {stats.debug.operations_by_type && Object.keys(stats.debug.operations_by_type).length > 0 && (
            <div className="mt-3">
              <h4 className="text-sm font-medium mb-2">Operations by Type</h4>
              <div className="grid grid-cols-2 gap-2">
                {Object.entries(stats.debug.operations_by_type)
                  .sort((a, b) => b[1] - a[1]) // Sort by count descending
                  .map(([type, count]) => (
                    <div key={type} className="flex justify-between text-xs">
                      <span className="text-gray-300">{type}</span>
                      <span>{count}</span>
                    </div>
                  ))
                }
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

// Helper function to get color for memory type
const getMemoryTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    fact: '#4ade80', // green
    preference: '#60a5fa', // blue
    conversation: '#f472b6', // pink
    persona: '#a78bfa', // purple
    default: '#94a3b8' // gray
  };
  
  return colors[type.toLowerCase()] || colors.default;
};

export default MemoryStatsDisplay;
