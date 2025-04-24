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
      event.type === 'tool_error' ||
      (event.type === 'llm_result' && event.data?.tool_calls) ||
      (event.type === 'component_timing' && event.data?.component === 'tool')
    );

    if (toolEvents.length === 0) return;

    // Create a map of tool calls
    const toolCallsMap = {};

    // First, get existing tool calls
    setToolCalls(prevToolCalls => {
      // Initialize map with existing tool calls
      prevToolCalls.forEach(call => {
        toolCallsMap[call.id] = call;
      });

      // Process new events
      toolEvents.forEach(event => {
        if (event.type === 'tool_call') {
          const id = event.data?.id || `tool-${Date.now()}-${Math.random().toString(36).substring(7)}`;
          toolCallsMap[id] = {
            id,
            tool: event.data?.tool || 'unknown',
            params: event.data?.params || {},
            result: null,
            timestamp: event.timestamp,
            status: 'pending',
            isNew: true
          };
        } else if (event.type === 'tool_result' && event.data?.id) {
          const id = event.data.id;
          if (toolCallsMap[id]) {
            toolCallsMap[id] = {
              ...toolCallsMap[id],
              result: event.data.result,
              status: 'success',
              isNew: true
            };
          } else {
            // Create a new entry if we got a result without a call
            toolCallsMap[id] = {
              id,
              tool: event.data?.tool || 'unknown',
              params: {},
              result: event.data.result,
              timestamp: event.timestamp,
              status: 'success',
              isNew: true
            };
          }
        } else if (event.type === 'tool_error' && event.data?.id) {
          const id = event.data.id;
          if (toolCallsMap[id]) {
            toolCallsMap[id] = {
              ...toolCallsMap[id],
              result: event.data.error,
              status: 'error',
              isNew: true
            };
          } else {
            // Create a new entry if we got an error without a call
            toolCallsMap[id] = {
              id,
              tool: event.data?.tool || 'unknown',
              params: {},
              result: event.data.error,
              timestamp: event.timestamp,
              status: 'error',
              isNew: true
            };
          }
        } else if (event.type === 'llm_result' && event.data?.tool_calls) {
          // Handle tool calls from LLM result
          event.data.tool_calls.forEach((toolCall, index) => {
            const id = toolCall.id || `llm-tool-${Date.now()}-${index}`;
            toolCallsMap[id] = {
              id,
              tool: toolCall.name || 'unknown',
              params: toolCall.arguments || {},
              result: null,
              timestamp: event.timestamp,
              status: 'pending',
              isNew: true
            };
          });
        } else if (event.type === 'component_timing' && event.data?.component === 'tool') {
          // Handle tool timing events
          const id = event.data?.id || `timing-${Date.now()}`;
          if (toolCallsMap[id]) {
            toolCallsMap[id] = {
              ...toolCallsMap[id],
              duration: event.data.duration,
              isNew: true
            };
          }
        }
      });

      // Convert to array and sort by timestamp (newest first)
      const toolCallsArray = Object.values(toolCallsMap);
      toolCallsArray.sort((a, b) =>
        new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime()
      );

      // Update state with the latest 10 tool calls
      return toolCallsArray.slice(0, 10);
    });

    // Clear the "new" flag after 3 seconds
    const timer = setTimeout(() => {
      setToolCalls(prevToolCalls =>
        prevToolCalls.map(call => ({
          ...call,
          isNew: false
        }))
      );
    }, 3000);

    return () => clearTimeout(timer);
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
      <div className="section-header">
        <h3 className="section-title">Tool Usage</h3>
      </div>

      <div className="tool-list">
        {toolCalls.length > 0 ? (
          toolCalls.map((call) => (
            <div key={call.id} className={`tool-card ${call.status} ${call.isNew ? 'tool-new' : ''}`}>
              <div className="tool-header">
                <span className="tool-name">{call.tool}</span>
                <span className="tool-status">{call.status}</span>
                {call.duration && (
                  <span className="tool-duration">{call.duration.toFixed(2)}s</span>
                )}
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
          <div className="no-tools">
            <p>No tool calls yet</p>
            <p className="no-tools-description">Tools will appear here when Coda uses them to perform tasks.</p>
          </div>
        )}
      </div>
    </div>
  );
}

export default ToolDisplay;
