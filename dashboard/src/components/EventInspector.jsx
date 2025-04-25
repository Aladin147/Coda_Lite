import React, { useState, useEffect } from 'react';
import '../styles/EventInspector.css';

/**
 * EventInspector component for debugging WebSocket events
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 */
function EventInspector({ events }) {
  const [filteredEvents, setFilteredEvents] = useState([]);
  const [selectedEvent, setSelectedEvent] = useState(null);
  const [filters, setFilters] = useState({
    types: [],
    search: '',
    timeRange: 'all'
  });
  const [availableTypes, setAvailableTypes] = useState([]);
  
  // Extract available event types
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    const types = [...new Set(events.map(e => e.type))];
    setAvailableTypes(types.sort());
  }, [events]);
  
  // Apply filters to events
  useEffect(() => {
    if (!events || events.length === 0) {
      setFilteredEvents([]);
      return;
    }
    
    let filtered = [...events];
    
    // Filter by type
    if (filters.types.length > 0) {
      filtered = filtered.filter(e => filters.types.includes(e.type));
    }
    
    // Filter by search text
    if (filters.search.trim()) {
      const searchLower = filters.search.toLowerCase();
      filtered = filtered.filter(e => 
        e.type.toLowerCase().includes(searchLower) ||
        JSON.stringify(e.data).toLowerCase().includes(searchLower)
      );
    }
    
    // Filter by time range
    if (filters.timeRange !== 'all') {
      const now = new Date();
      let cutoff = new Date();
      
      switch (filters.timeRange) {
        case '1m':
          cutoff.setMinutes(now.getMinutes() - 1);
          break;
        case '5m':
          cutoff.setMinutes(now.getMinutes() - 5);
          break;
        case '15m':
          cutoff.setMinutes(now.getMinutes() - 15);
          break;
        case '1h':
          cutoff.setHours(now.getHours() - 1);
          break;
        default:
          break;
      }
      
      filtered = filtered.filter(e => new Date(e.timestamp) >= cutoff);
    }
    
    setFilteredEvents(filtered);
  }, [events, filters]);
  
  // Toggle event type filter
  const toggleTypeFilter = (type) => {
    setFilters(prev => {
      const types = [...prev.types];
      const index = types.indexOf(type);
      
      if (index === -1) {
        types.push(type);
      } else {
        types.splice(index, 1);
      }
      
      return { ...prev, types };
    });
  };
  
  // Clear all filters
  const clearFilters = () => {
    setFilters({
      types: [],
      search: '',
      timeRange: 'all'
    });
  };
  
  // Format timestamp
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  // Get event type color
  const getEventTypeColor = (type) => {
    switch (type) {
      case 'stt_start':
      case 'stt_result':
      case 'stt_end':
        return 'var(--info-color)';
      case 'llm_start':
      case 'llm_result':
      case 'llm_end':
        return 'var(--primary-color)';
      case 'tts_start':
      case 'tts_end':
        return 'var(--success-color)';
      case 'tool_call':
      case 'tool_result':
      case 'tool_error':
        return 'var(--warning-color)';
      case 'memory_store':
      case 'memory_retrieved':
      case 'memory_added':
        return 'var(--secondary-color)';
      case 'latency_trace':
      case 'component_timing':
      case 'system_metrics':
        return 'var(--text-secondary)';
      case 'error':
        return 'var(--danger-color)';
      default:
        return 'var(--text-color)';
    }
  };
  
  return (
    <div className="event-inspector">
      <div className="event-inspector-header">
        <h3>Event Inspector</h3>
        <div className="event-count">
          {filteredEvents.length} / {events.length} events
        </div>
      </div>
      
      <div className="event-filters">
        <div className="filter-section">
          <div className="filter-header">
            <h4>Filter by Type</h4>
            <button 
              className="clear-button"
              onClick={clearFilters}
            >
              Clear Filters
            </button>
          </div>
          <div className="type-filters">
            {availableTypes.map(type => (
              <div 
                key={type}
                className={`type-filter ${filters.types.includes(type) ? 'active' : ''}`}
                onClick={() => toggleTypeFilter(type)}
                style={{ 
                  '--type-color': getEventTypeColor(type),
                  borderColor: filters.types.includes(type) ? getEventTypeColor(type) : 'transparent'
                }}
              >
                {type}
              </div>
            ))}
          </div>
        </div>
        
        <div className="filter-row">
          <div className="search-filter">
            <input 
              type="text"
              placeholder="Search events..."
              value={filters.search}
              onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
            />
          </div>
          
          <div className="time-filter">
            <select
              value={filters.timeRange}
              onChange={(e) => setFilters(prev => ({ ...prev, timeRange: e.target.value }))}
            >
              <option value="all">All Time</option>
              <option value="1m">Last Minute</option>
              <option value="5m">Last 5 Minutes</option>
              <option value="15m">Last 15 Minutes</option>
              <option value="1h">Last Hour</option>
            </select>
          </div>
        </div>
      </div>
      
      <div className="event-list-container">
        <div className="event-list">
          {filteredEvents.length > 0 ? (
            filteredEvents.map((event, index) => (
              <div 
                key={`${event.type}-${event.timestamp}-${index}`}
                className={`event-item ${selectedEvent === event ? 'selected' : ''}`}
                onClick={() => setSelectedEvent(event)}
              >
                <div className="event-header">
                  <span 
                    className="event-type"
                    style={{ backgroundColor: getEventTypeColor(event.type) }}
                  >
                    {event.type}
                  </span>
                  <span className="event-time">{formatTime(event.timestamp)}</span>
                </div>
                <div className="event-preview">
                  {JSON.stringify(event.data).substring(0, 100)}
                  {JSON.stringify(event.data).length > 100 ? '...' : ''}
                </div>
              </div>
            ))
          ) : (
            <div className="no-events">
              <p>No events match the current filters.</p>
              <button onClick={clearFilters}>Clear Filters</button>
            </div>
          )}
        </div>
        
        {selectedEvent && (
          <div className="event-details">
            <div className="details-header">
              <h4>Event Details</h4>
              <button onClick={() => setSelectedEvent(null)}>Close</button>
            </div>
            <div className="details-content">
              <div className="detail-row">
                <span className="detail-label">Type:</span>
                <span className="detail-value">{selectedEvent.type}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Timestamp:</span>
                <span className="detail-value">{new Date(selectedEvent.timestamp).toLocaleString()}</span>
              </div>
              <div className="detail-row">
                <span className="detail-label">Data:</span>
              </div>
              <pre className="event-data">
                {JSON.stringify(selectedEvent.data, null, 2)}
              </pre>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default EventInspector;
