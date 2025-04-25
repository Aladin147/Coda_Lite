import React, { useState, useEffect } from 'react';
import '../styles/MemoryViewer.css';

function MemoryViewer({ memories, events }) {
  const [displayedMemories, setDisplayedMemories] = useState([]);
  const [newMemoryAdded, setNewMemoryAdded] = useState(false);

  // Process memory events from the events array
  useEffect(() => {
    if (!events || events.length === 0) {
      // If no events but we have memories passed directly, use those
      if (memories && memories.length > 0) {
        setDisplayedMemories(memories);
      }
      return;
    }

    // Extract memory events
    const memoryEvents = events.filter(e =>
      e.type === 'memory_store' ||
      e.type === 'memory_retrieved' ||
      e.type === 'memory_added'
    );

    if (memoryEvents.length === 0) return;

    // Process memory events
    const newMemories = memoryEvents.map(e => ({
      id: e.data.memory_id || `memory-${Date.now()}-${Math.random()}`,
      content: e.data.content_preview || e.data.content || 'Memory content not available',
      type: e.data.memory_type || 'unknown',
      importance: e.data.importance || 0.5,
      timestamp: e.timestamp || Date.now() / 1000,
      isNew: true
    }));

    if (newMemories.length > 0) {
      setDisplayedMemories(prev => {
        // Combine with existing memories, remove duplicates, and sort by timestamp (newest first)
        const combined = [...prev, ...newMemories];
        const uniqueMemories = Array.from(
          new Map(combined.map(m => [m.id, m])).values()
        );
        return uniqueMemories.sort((a, b) => b.timestamp - a.timestamp);
      });

      // Set flag to highlight new memories
      setNewMemoryAdded(true);

      // Clear the highlight after 3 seconds
      setTimeout(() => {
        setNewMemoryAdded(false);
        setDisplayedMemories(prev =>
          prev.map(m => ({ ...m, isNew: false }))
        );
      }, 3000);
    }
  }, [events, memories]);

  const formatTimestamp = (timestamp) => {
    try {
      // Handle both seconds and milliseconds timestamps
      const date = timestamp > 1000000000000
        ? new Date(timestamp)
        : new Date(timestamp * 1000);
      return date.toLocaleString();
    } catch (e) {
      console.error('Error formatting timestamp:', timestamp, e);
      return 'Invalid date';
    }
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
    <div className={`memory-viewer ${newMemoryAdded ? 'has-new-memory' : ''}`}>
      {displayedMemories.length === 0 ? (
        <div className="memory-empty">
          <div className="memory-empty-message">No memories stored yet</div>
          <div className="memory-empty-description">
            Memories will appear here when Coda stores information from your conversation.
          </div>
        </div>
      ) : (
        displayedMemories.map((memory) => (
          <div
            key={memory.id}
            className={`memory-item ${memory.isNew ? 'memory-new' : ''}`}
          >
            <div className="memory-header">
              <span className="memory-type" style={{ color: getMemoryTypeColor(memory.type) }}>
                {memory.type.charAt(0).toUpperCase() + memory.type.slice(1)}
              </span>
              <span className="memory-importance">
                Importance: {typeof memory.importance === 'number' ? memory.importance.toFixed(2) : '0.50'}
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
