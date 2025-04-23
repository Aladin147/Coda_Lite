import React from 'react';

function EventLog({ events }) {
  const formatTimestamp = (timestamp) => {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  };
  
  const formatEventData = (event) => {
    if (!event.data) return 'No data';
    
    try {
      return JSON.stringify(event.data, null, 2);
    } catch (error) {
      return 'Error formatting data';
    }
  };
  
  return (
    <div className="event-log">
      {events.length === 0 ? (
        <div className="card">
          <div className="card-title">No events received yet</div>
        </div>
      ) : (
        events.map((event, index) => (
          <div key={index} className="event-item">
            <div className="event-header">
              <span className="event-type">{event.type}</span>
              <span className="event-timestamp">{formatTimestamp(event.timestamp)}</span>
            </div>
            <pre className="event-data">{formatEventData(event)}</pre>
          </div>
        ))
      )}
    </div>
  );
}

export default EventLog;
