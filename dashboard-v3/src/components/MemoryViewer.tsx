import React, { memo } from 'react';

interface Memory {
  id: string;
  content: string;
  type: string;
  importance: number;
  timestamp: string;
}

interface MemoryViewerProps {
  memories: Memory[];
}

const MemoryViewer: React.FC<MemoryViewerProps> = ({ memories }) => {
  return (
    <div className="card p-4 h-64 overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Memory</h2>
      
      {memories.length === 0 ? (
        <div className="flex items-center justify-center h-32 text-gray-400">
          <p>No memories stored yet.</p>
        </div>
      ) : (
        <div className="space-y-3">
          {memories.map((memory) => (
            <div 
              key={memory.id}
              className="bg-dark-600 p-3 rounded-lg"
            >
              <div className="flex justify-between items-start mb-1">
                <span className="text-sm font-semibold bg-dark-500 px-2 py-0.5 rounded">
                  {memory.type}
                </span>
                <div className="flex items-center">
                  <span className="text-xs text-gray-400 mr-2">
                    Importance: {memory.importance.toFixed(1)}
                  </span>
                  <span className="text-xs text-gray-400">
                    {new Date(memory.timestamp).toLocaleTimeString()}
                  </span>
                </div>
              </div>
              <p className="text-sm">{memory.content}</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(MemoryViewer);
