# Dashboard Instrumentation Guide

This document describes the instrumentation approach used in the Coda Dashboard v3 to help identify and fix WebSocket communication issues.

## Overview

We've added comprehensive instrumentation throughout the WebSocket communication flow to help identify the root causes of duplicate and concurrent messages. This instrumentation includes:

1. **Timestamped Logging**: All logs include ISO timestamps for precise timing analysis
2. **Unique Message IDs**: Each message is assigned a unique ID for tracking through the system
3. **Client Identification**: Each WebSocket client has a unique ID
4. **Message History**: A history of sent messages is maintained for analysis
5. **Component Tracing**: Each component logs its actions with stack traces
6. **Duplicate Detection**: Potential duplicate messages are detected and logged

## WebSocketClient Instrumentation

The `WebSocketClient` class has been enhanced with the following instrumentation:

### Properties

- `clientId`: A unique identifier for each client instance
- `messageCounter`: A counter for messages sent by this client
- `sentMessages`: A map of sent messages for deduplication and debugging

### Methods

- `sendMessage(type, data)`: Sends a message with instrumentation
  - Assigns a unique message ID
  - Logs message preparation, sending, and completion
  - Detects potential duplicate messages
  - Maintains a history of sent messages

### Connection Lifecycle

- `connect()`: Logs connection attempts and success/failure
- `disconnect()`: Logs disconnection with socket state
- `reconnect()`: Logs reconnection attempts with timing information

## Component Instrumentation

### App Component

- Logs message sending with component and function information
- Captures stack traces for message source identification

### VoiceControls Component

- Logs user interactions (mouse down, up, leave)
- Logs action type and component information
- Captures stack traces for event flow analysis

### TextInput Component

- Logs form submissions and keyboard shortcuts
- Logs message sending with text length information
- Captures stack traces for event flow analysis

## WebSocketDebugger Enhancements

The WebSocketDebugger component has been enhanced with:

- Display of client ID and message counter
- Button to show message history in console
- Detailed connection state information

## How to Use the Instrumentation

### Console Logging

Open the browser developer tools console to see the instrumented logs. The logs are formatted as:

```
[TIMESTAMP][WebSocketClient:CLIENT_ID] Message
```

### Message History

Click the "Show Message History" button in the WebSocketDebugger to see a table of all sent messages in the console.

### Analyzing Duplicate Messages

When a potential duplicate message is detected, a warning is logged with:
- The current message being sent
- Previous similar messages sent recently

### Tracing Message Flow

Each component logs its actions with stack traces, allowing you to trace the flow of events from user action to WebSocket message.

## Debugging Tips

1. **Filter Console Logs**: Use the console filter to focus on specific components or actions
2. **Look for Patterns**: Check for patterns in duplicate messages (timing, source)
3. **Check Stack Traces**: Examine stack traces to identify unexpected call paths
4. **Compare Timestamps**: Look for unusually close timestamps between similar messages
5. **Check Event Handlers**: Look for multiple event handlers firing for the same user action

## Next Steps

After collecting data with this instrumentation:

1. Analyze patterns in duplicate messages
2. Identify components or event handlers causing duplicate messages
3. Fix the root causes of duplicate messages
4. Implement message queuing as a fail-safe mechanism
5. Add automated tests to verify the fixes
