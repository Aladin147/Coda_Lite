# Coda WebSocket Implementation Guide

This document describes the WebSocket implementation used in Coda's dashboard to communicate with the Coda backend.

## Overview

Coda's dashboard communicates with the backend using WebSockets. The backend runs a WebSocket server on port 8765, and the dashboard connects to this server to send commands and receive events.

## Implementation Details

### WebSocketClient

The core of our implementation is the `WebSocketClient` class, which provides a simple interface for connecting to and communicating with the Coda backend.

Key features:
- Direct WebSocket connection to the Coda backend
- Global access through the `window.wsClient` object
- Automatic reconnection on disconnection
- Event-based communication

### Message Format

All messages sent between the dashboard and the backend follow this format:

```json
{
  "type": "message_type",
  "data": {
    // Message-specific data
  },
  "timestamp": "2023-06-01T12:34:56.789Z"
}
```

### Connection Process

1. The dashboard creates a new `WebSocketClient` instance
2. The client connects to the WebSocket server at `ws://localhost:8765`
3. On successful connection, the client stores itself in `window.wsClient`
4. The dashboard can then send messages using `window.wsClient.socket.send()`

### Sending Messages

To send a message to the backend:

```typescript
if ((window as any).wsClient && (window as any).wsClient.isConnected()) {
  const message = {
    type: 'message_type',
    data: { /* message data */ },
    timestamp: new Date().toISOString()
  };
  
  (window as any).wsClient.socket.send(JSON.stringify(message));
}
```

### Receiving Events

The client receives events from the backend through the WebSocket connection. These events are processed by the `onEvent` callback:

```typescript
client.onEvent = (event) => {
  // Process the event
  console.log('Received event:', event);
  
  // Update UI based on event type
  switch (event.type) {
    case 'latency_trace':
      // Update performance metrics
      break;
    case 'system_metrics':
      // Update system metrics
      break;
    // ...
  }
};
```

## Common Message Types

### Commands (Dashboard to Backend)

| Type | Description | Data |
|------|-------------|------|
| `stt_start` | Start speech-to-text | `{}` |
| `stt_stop` | Stop speech-to-text | `{}` |
| `text_input` | Send text input | `{ "text": "message text" }` |
| `demo_flow` | Run a demo flow | `{ "text": "demo prompt" }` |

### Events (Backend to Dashboard)

| Type | Description | Data |
|------|-------------|------|
| `latency_trace` | Performance metrics | `{ "stt_seconds": 0.5, "llm_seconds": 1.2, ... }` |
| `system_metrics` | System resource usage | `{ "memory_mb": 1024, "cpu_percent": 30, ... }` |
| `memory_store` | Memory storage event | `{ "memory_id": "123", "content": "...", ... }` |
| `conversation_message` | Message in conversation | `{ "message_id": "123", "content": "...", ... }` |
| `mode_change` | Coda mode change | `{ "mode": "listening" }` |
| `emotion_change` | Coda emotion change | `{ "emotion": "neutral" }` |

## Troubleshooting

### Common Issues

1. **Connection Failures**
   - Ensure the Coda backend is running
   - Verify the WebSocket server is running on port 8765
   - Check for network issues or firewall restrictions

2. **Message Not Received**
   - Verify the message format is correct
   - Check that the WebSocket connection is open
   - Look for errors in the browser console

3. **Asyncio Errors in Backend**
   - These are known issues with Python's asyncio ProactorEventLoop on Windows
   - They typically don't affect functionality
   - Example error: `AssertionError: assert f is self._write_fut`

### Debugging Tools

1. **WebSocketDebugger Component**
   - Shows connection status
   - Displays all events received
   - Provides tools to test the connection

2. **Browser Developer Tools**
   - Network tab can show WebSocket frames
   - Console logs connection events and errors

## Lessons Learned

### What Worked

1. **Direct WebSocket Implementation**
   - Using the native WebSocket API directly
   - Storing the client in the window object for global access
   - Simple event-based communication

2. **Consistent Message Format**
   - Using a standard format for all messages
   - Including timestamps for debugging

3. **Automatic Reconnection**
   - Handling disconnections gracefully
   - Exponential backoff for reconnection attempts

### What Didn't Work

1. **Complex Abstraction Layers**
   - Multiple layers of abstraction made debugging difficult
   - Observer pattern added unnecessary complexity

2. **State Management Integration**
   - Tight coupling with state management libraries
   - Made it hard to track the flow of data

3. **Custom WebSocket Protocol**
   - Deviating from standard WebSocket patterns
   - Added unnecessary complexity

## Best Practices

1. **Keep It Simple**
   - Use the native WebSocket API directly
   - Minimize abstraction layers

2. **Global Access**
   - Store the WebSocket client in a globally accessible location
   - Makes it easier to send messages from anywhere

3. **Consistent Error Handling**
   - Check connection status before sending messages
   - Provide clear error messages

4. **Logging**
   - Log all sent and received messages
   - Include timestamps for debugging

5. **Testing**
   - Test with the actual backend
   - Use the WebSocketDebugger to verify communication
