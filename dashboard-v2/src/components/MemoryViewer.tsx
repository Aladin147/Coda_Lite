import React from 'react';
import { useEvents } from '../store/selectors';

interface Memory {
  id: string;
  content: string;
  timestamp: number;
  type: string;
}

const MemoryViewer: React.FC = () => {
  const { events } = useEvents();
  
  // Extract memory events
  const memoryEvents = events.filter(event => 
    event.type === 'memory_created' || 
    event.type === 'memory_accessed'
  );
  
  // Convert memory events to memory objects
  const memories: Memory[] = memoryEvents.map(event => ({
    id: event.memoryId || `memory-${event.timestamp}`,
    content: event.content || '',
    timestamp: event.timestamp,
    type: event.type
  }));
  
  return (
    <div className="h-full overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Memory</h2>
      
      {memories.length === 0 ? (
        <p className="text-gray-500 dark:text-gray-400">No memories yet.</p>
      ) : (
        <div className="space-y-3">
          {memories.map((memory) => (
            <div 
              key={memory.id} 
              className={`p-3 rounded-lg border ${
                memory.type === 'memory_accessed' 
                  ? 'border-yellow-300 bg-yellow-50 dark:bg-yellow-900/20 dark:border-yellow-700' 
                  : 'border-green-300 bg-green-50 dark:bg-green-900/20 dark:border-green-700'
              }`}
            >
              <div className="text-sm font-medium mb-1">
                {memory.type === 'memory_accessed' ? 'Accessed' : 'Created'} at {new Date(memory.timestamp).toLocaleTimeString()}
              </div>
              <div className="text-sm">{memory.content}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default MemoryViewer;
