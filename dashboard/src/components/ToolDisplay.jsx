import { useState, useEffect } from 'react';
import '../styles/ToolDisplay.css';

/**
 * ToolDisplay component that shows tool usage cards
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 */
function ToolDisplay({ events }) {
  const [toolCalls, setToolCalls] = useState([]);
  
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    // Process tool-related events
    const toolEvents = events.filter(event => 
      event.type === 'tool_call' || 
      event.type === 'tool_result' || 
      event.type === 'tool_error'
    );
    
    if (toolEvents.length === 0) return;
    
    // Create a map of tool calls
    const toolCallsMap = {};
    
    toolEvents.forEach(event => {
      if (event.type === 'tool_call') {
        const id = event.data?.id || Math.random().toString(36).substring(7);
        toolCallsMap[id] = {
          id,
          tool: event.data?.tool || 'unknown',
          params: event.data?.params || {},
          result: null,
          timestamp: event.timestamp,
          status: 'pending'
        };
      } else if (event.type === 'tool_result' && event.data?.id) {
        const id = event.data.id;
        if (toolCallsMap[id]) {
          toolCallsMap[id] = {
            ...toolCallsMap[id],
            result: event.data.result,
            status: 'success'
          };
        }
      } else if (event.type === 'tool_error' && event.data?.id) {
        const id = event.data.id;
        if (toolCallsMap[id]) {
          toolCallsMap[id] = {
            ...toolCallsMap[id],
            result: event.data.error,
            status: 'error'
          };
        }
      }
    });
    
    // Convert to array and sort by timestamp (newest first)
    const toolCallsArray = Object.values(toolCallsMap);
    toolCallsArray.sort((a, b) => 
      new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
    );
    
    // Update state with the latest 5 tool calls
    setToolCalls(toolCallsArray.slice(0, 5));
  }, [events]);
  
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  const formatParams = (params) => {
    if (!params) return '';
    try {
      return JSON.stringify(params, null, 2);
    } catch (e) {
      return String(params);
    }
  };
  
  const formatResult = (result) => {
    if (result === null || result === undefined) return '';
    try {
      return typeof result === 'object' 
        ? JSON.stringify(result, null, 2) 
        : String(result);
    } catch (e) {
      return String(result);
    }
  };
  
  return (
    <div className="tool-display">
      <h3 className="tool-display-title">Tool Usage</h3>
      
      <div className="tool-list">
        {toolCalls.length > 0 ? (
          toolCalls.map((call) => (
            <div key={call.id} className={`tool-card ${call.status}`}>
              <div className="tool-header">
                <span className="tool-name">{call.tool}</span>
                <span className="tool-status">{call.status}</span>
              </div>
              
              <div className="tool-params">
                <pre>{formatParams(call.params)}</pre>
              </div>
              
              {call.result && (
                <div className="tool-result">
                  <div className="result-label">Result:</div>
                  <pre>{formatResult(call.result)}</pre>
                </div>
              )}
              
              <div className="tool-time">
                {formatTime(call.timestamp)}
              </div>
            </div>
          ))
        ) : (
          <div className="no-tools">No tool calls yet</div>
        )}
      </div>
    </div>
  );
}

export default ToolDisplay;
