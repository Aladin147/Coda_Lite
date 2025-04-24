import React, { useState, useEffect } from 'react';
import '../styles/MemoryDebugPanel.css';

/**
 * MemoryDebugPanel component for debugging memory system
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 * @param {Function} props.sendMessage - Function to send WebSocket messages
 */
function MemoryDebugPanel({ events, sendMessage }) {
  const [memoryStats, setMemoryStats] = useState({
    shortTerm: { count: 0, lastUpdated: null },
    longTerm: { count: 0, lastUpdated: null },
    retrievalStats: { 
      totalQueries: 0, 
      successfulQueries: 0,
      averageRetrievalTime: 0
    }
  });
  
  const [memoryOperations, setMemoryOperations] = useState([]);
  const [selectedMemory, setSelectedMemory] = useState(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  // Process memory-related events
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    // Filter memory-related events
    const memoryEvents = events.filter(e => 
      e.type === 'memory_store' || 
      e.type === 'memory_retrieved' ||
      e.type === 'memory_added' ||
      e.type === 'memory_update' ||
      (e.type === 'component_timing' && e.data?.component === 'memory')
    );
    
    if (memoryEvents.length === 0) return;
    
    // Process memory events
    memoryEvents.forEach(event => {
      // Update memory stats based on event type
      if (event.type === 'memory_store') {
        setMemoryStats(prev => ({
          ...prev,
          longTerm: {
            count: prev.longTerm.count + 1,
            lastUpdated: new Date().toISOString()
          }
        }));
        
        // Add to operations list
        setMemoryOperations(prev => [
          {
            id: `op-${Date.now()}-${Math.random()}`,
            type: 'store',
            timestamp: event.timestamp,
            details: {
              memoryId: event.data.memory_id,
              memoryType: event.data.memory_type,
              importance: event.data.importance
            }
          },
          ...prev
        ].slice(0, 50));
      }
      
      if (event.type === 'memory_retrieved') {
        setMemoryStats(prev => ({
          ...prev,
          retrievalStats: {
            totalQueries: prev.retrievalStats.totalQueries + 1,
            successfulQueries: prev.retrievalStats.successfulQueries + (event.data.success ? 1 : 0),
            averageRetrievalTime: 
              (prev.retrievalStats.averageRetrievalTime * prev.retrievalStats.totalQueries + 
               (event.data.retrieval_time || 0)) / (prev.retrievalStats.totalQueries + 1)
          }
        }));
        
        // Add to operations list
        setMemoryOperations(prev => [
          {
            id: `op-${Date.now()}-${Math.random()}`,
            type: 'retrieve',
            timestamp: event.timestamp,
            details: {
              query: event.data.query,
              resultCount: event.data.results?.length || 0,
              success: event.data.success
            }
          },
          ...prev
        ].slice(0, 50));
      }
      
      if (event.type === 'memory_added') {
        setMemoryStats(prev => ({
          ...prev,
          shortTerm: {
            count: prev.shortTerm.count + 1,
            lastUpdated: new Date().toISOString()
          }
        }));
        
        // Add to operations list
        setMemoryOperations(prev => [
          {
            id: `op-${Date.now()}-${Math.random()}`,
            type: 'add',
            timestamp: event.timestamp,
            details: {
              content: event.data.content_preview,
              memoryType: event.data.memory_type
            }
          },
          ...prev
        ].slice(0, 50));
      }
    });
  }, [events]);
  
  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  // Handle memory search
  const handleSearch = () => {
    if (!searchQuery.trim()) return;
    
    // Send memory search request
    sendMessage('memory_search', {
      query: searchQuery,
      limit: 10
    });
    
    // Add to operations list
    setMemoryOperations(prev => [
      {
        id: `op-${Date.now()}-${Math.random()}`,
        type: 'search',
        timestamp: new Date().toISOString(),
        details: {
          query: searchQuery
        }
      },
      ...prev
    ].slice(0, 50));
  };
  
  // Handle memory inspection
  const inspectMemory = (memoryId) => {
    // Send memory inspection request
    sendMessage('memory_inspect', {
      memory_id: memoryId
    });
  };
  
  return (
    <div className="memory-debug-panel">
      <div className="memory-debug-header">
        <h3>Memory System Debug</h3>
      </div>
      
      <div className="memory-stats-container">
        <div className="memory-stat-card">
          <h4>Short-Term Memory</h4>
          <div className="memory-stat">
            <span className="stat-label">Items</span>
            <span className="stat-value">{memoryStats.shortTerm.count}</span>
          </div>
          <div className="memory-stat">
            <span className="stat-label">Last Updated</span>
            <span className="stat-value">{memoryStats.shortTerm.lastUpdated ? formatTime(memoryStats.shortTerm.lastUpdated) : 'Never'}</span>
          </div>
        </div>
        
        <div className="memory-stat-card">
          <h4>Long-Term Memory</h4>
          <div className="memory-stat">
            <span className="stat-label">Items</span>
            <span className="stat-value">{memoryStats.longTerm.count}</span>
          </div>
          <div className="memory-stat">
            <span className="stat-label">Last Updated</span>
            <span className="stat-value">{memoryStats.longTerm.lastUpdated ? formatTime(memoryStats.longTerm.lastUpdated) : 'Never'}</span>
          </div>
        </div>
        
        <div className="memory-stat-card">
          <h4>Retrieval Stats</h4>
          <div className="memory-stat">
            <span className="stat-label">Total Queries</span>
            <span className="stat-value">{memoryStats.retrievalStats.totalQueries}</span>
          </div>
          <div className="memory-stat">
            <span className="stat-label">Success Rate</span>
            <span className="stat-value">
              {memoryStats.retrievalStats.totalQueries > 0 
                ? `${((memoryStats.retrievalStats.successfulQueries / memoryStats.retrievalStats.totalQueries) * 100).toFixed(1)}%` 
                : 'N/A'}
            </span>
          </div>
          <div className="memory-stat">
            <span className="stat-label">Avg. Retrieval Time</span>
            <span className="stat-value">
              {memoryStats.retrievalStats.averageRetrievalTime > 0 
                ? `${memoryStats.retrievalStats.averageRetrievalTime.toFixed(2)}s` 
                : 'N/A'}
            </span>
          </div>
        </div>
      </div>
      
      <div className="memory-search-container">
        <h4>Memory Search</h4>
        <div className="memory-search-form">
          <input 
            type="text" 
            placeholder="Search memories..." 
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSearch()}
          />
          <button onClick={handleSearch}>Search</button>
        </div>
      </div>
      
      <div className="memory-operations-container">
        <h4>Recent Memory Operations</h4>
        <div className="memory-operations-list">
          {memoryOperations.length > 0 ? (
            memoryOperations.map(operation => (
              <div key={operation.id} className={`memory-operation ${operation.type}`}>
                <div className="operation-header">
                  <span className="operation-type">{operation.type}</span>
                  <span className="operation-time">{formatTime(operation.timestamp)}</span>
                </div>
                <div className="operation-details">
                  {operation.type === 'store' && (
                    <>
                      <div className="detail-item">
                        <span className="detail-label">Memory ID:</span>
                        <span className="detail-value">{operation.details.memoryId}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Type:</span>
                        <span className="detail-value">{operation.details.memoryType}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Importance:</span>
                        <span className="detail-value">{operation.details.importance?.toFixed(2) || 'N/A'}</span>
                      </div>
                    </>
                  )}
                  
                  {operation.type === 'retrieve' && (
                    <>
                      <div className="detail-item">
                        <span className="detail-label">Query:</span>
                        <span className="detail-value">{operation.details.query}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Results:</span>
                        <span className="detail-value">{operation.details.resultCount}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Success:</span>
                        <span className="detail-value">{operation.details.success ? 'Yes' : 'No'}</span>
                      </div>
                    </>
                  )}
                  
                  {operation.type === 'add' && (
                    <>
                      <div className="detail-item">
                        <span className="detail-label">Content:</span>
                        <span className="detail-value">{operation.details.content}</span>
                      </div>
                      <div className="detail-item">
                        <span className="detail-label">Type:</span>
                        <span className="detail-value">{operation.details.memoryType}</span>
                      </div>
                    </>
                  )}
                  
                  {operation.type === 'search' && (
                    <>
                      <div className="detail-item">
                        <span className="detail-label">Query:</span>
                        <span className="detail-value">{operation.details.query}</span>
                      </div>
                    </>
                  )}
                </div>
              </div>
            ))
          ) : (
            <div className="no-operations">
              <p>No memory operations recorded yet.</p>
              <p>Operations will appear here as the memory system is used.</p>
            </div>
          )}
        </div>
      </div>
      
      {selectedMemory && (
        <div className="memory-detail-modal">
          <div className="modal-content">
            <div className="modal-header">
              <h4>Memory Details</h4>
              <button onClick={() => setSelectedMemory(null)}>Close</button>
            </div>
            <div className="modal-body">
              <pre>{JSON.stringify(selectedMemory, null, 2)}</pre>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default MemoryDebugPanel;
