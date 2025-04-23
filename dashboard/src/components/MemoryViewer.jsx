import React from 'react';

function MemoryViewer({ memories }) {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleString();
  };
  
  const getMemoryTypeColor = (type) => {
    switch (type) {
      case 'conversation':
        return '#3a86ff';
      case 'fact':
        return '#8338ec';
      case 'preference':
        return '#06d6a0';
      default:
        return '#6c757d';
    }
  };
  
  return (
    <div className="memory-viewer">
      {memories.length === 0 ? (
        <div className="card">
          <div className="card-title">No memories stored yet</div>
        </div>
      ) : (
        memories.map((memory) => (
          <div key={memory.id} className="memory-item">
            <div className="memory-header">
              <span className="memory-type" style={{ color: getMemoryTypeColor(memory.type) }}>
                {memory.type.charAt(0).toUpperCase() + memory.type.slice(1)}
              </span>
              <span className="memory-importance">
                Importance: {memory.importance.toFixed(2)}
              </span>
            </div>
            <div className="memory-content">
              {memory.content}
            </div>
            <div className="memory-timestamp">
              {formatTimestamp(memory.timestamp)}
            </div>
          </div>
        ))
      )}
    </div>
  );
}

export default MemoryViewer;
