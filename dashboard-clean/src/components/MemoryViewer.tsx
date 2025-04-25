import React from 'react';
import { useMemories } from '../store/selectors';

const MemoryViewer: React.FC = () => {
  const { memories, addMemory, clearMemories } = useMemories();
  
  // Format timestamp
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleString([], { 
      month: 'short',
      day: 'numeric',
      hour: '2-digit', 
      minute: '2-digit'
    });
  };
  
  // Get color based on importance
  const getImportanceColor = (importance: number) => {
    if (importance >= 8) return 'var(--color-danger-500)';
    if (importance >= 5) return 'var(--color-warning-500)';
    return 'var(--color-success-500)';
  };
  
  return (
    <div className="card p-4 h-96 flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Memory</h2>
      
      <div className="flex-1 overflow-y-auto mb-4 space-y-3">
        {memories.length === 0 ? (
          <div className="text-center py-8 opacity-50">
            No memories stored
          </div>
        ) : (
          memories.map((memory) => (
            <div 
              key={memory.id} 
              className="p-3 rounded-lg"
              style={{ backgroundColor: 'rgba(255, 255, 255, 0.05)' }}
            >
              <div className="flex justify-between items-start mb-1">
                <div 
                  className="px-2 py-1 rounded text-xs font-semibold"
                  style={{ 
                    backgroundColor: getImportanceColor(memory.importance),
                    color: 'white'
                  }}
                >
                  Importance: {memory.importance}
                </div>
                <span className="text-xs opacity-70">
                  {formatTime(memory.timestamp)}
                </span>
              </div>
              <p className="mt-2">{memory.content}</p>
            </div>
          ))
        )}
      </div>
      
      <div className="flex space-x-2">
        <button 
          className="btn flex-1"
          onClick={() => {
            // Simulate adding a memory
            const memories = [
              "User prefers dark mode interfaces",
              "User mentioned they have a dog named Max",
              "User is interested in machine learning",
              "User is planning a trip to Japan next month",
              "User works as a software developer"
            ];
            
            const randomMemory = memories[Math.floor(Math.random() * memories.length)];
            const randomImportance = Math.floor(Math.random() * 10) + 1;
            
            addMemory({
              content: randomMemory,
              importance: randomImportance
            });
          }}
        >
          Add Test Memory
        </button>
        
        <button 
          className="btn btn-danger"
          onClick={() => {
            if (confirm('Are you sure you want to clear all memories?')) {
              clearMemories();
            }
          }}
        >
          Clear
        </button>
      </div>
    </div>
  );
};

export default MemoryViewer;
