# Known Issues and Troubleshooting Log

## Dashboard WebSocket Connection Issues

### Issue Description
The dashboard is experiencing persistent React errors with "Maximum update depth exceeded" when attempting to connect to the WebSocket server. This error occurs in the Avatar component and persists despite multiple implementation attempts and fixes.

### Error Details
```
Error: Maximum update depth exceeded. This can happen when a component repeatedly calls setState inside componentWillUpdate or componentDidUpdate. React limits the number of nested updates to prevent infinite loops.

Component Stack:
Avatar@http://localhost:5173/src/components/Avatar.tsx:21:36
div@unknown:0:0
div@unknown:0:0
div@unknown:0:0
DashboardContent@unknown:0:0
main@unknown:0:0
WebSocketProvider@http://localhost:5173/src/services/WebSocketProvider.tsx:29:34
ErrorBoundary@http://localhost:5173/src/components/ErrorBoundary.tsx:7:5
```

### Attempted Fixes

1. **WebSocketProvider Dependency Fix** - Removed `handleConnectionChange` and `handleMessage` from the useEffect dependencies to prevent infinite re-renders.
   - Result: Issue persisted

2. **Avatar Component Optimization** - Refactored the Avatar component to use `useMemo` for class name calculation to prevent unnecessary re-renders.
   - Result: Issue persisted

3. **Static Avatar Implementation** - Replaced the dynamic Avatar component with a static implementation that doesn't use state.
   - Result: Issue persisted

4. **Minimal Test Implementation** - Created a completely new minimal implementation without using the existing components.
   - Result: Issue persisted

### Current Status
The issue appears to be deeper than just the Avatar or WebSocketProvider components. It may be related to:

1. Circular dependencies in the React component tree
2. Issues with the Zustand store implementation
3. Conflicts between different state management approaches
4. Potential issues with the WebSocket event handling

### Next Steps
1. Conduct an external audit of the codebase to identify potential issues
2. Consider a complete rebuild of the dashboard with a simpler architecture
3. Investigate potential issues with the WebSocket server implementation
4. Test with different React state management libraries

## WebSocket Server Connection Issues

### Issue Description
When attempting to connect directly to the WebSocket server at http://localhost:8765, the browser shows an error message indicating that WebSocket servers cannot be accessed directly with a browser.

### Error Details
```
Failed to open a WebSocket connection: invalid Connection header: keep-alive.
You cannot access a WebSocket server directly with a browser. You need a WebSocket client.
```

### Current Status
This is expected behavior as WebSocket servers require a WebSocket client to connect, not a direct HTTP request. The dashboard should be using a proper WebSocket client implementation to connect to the server.

### WebSocket Server Event Loop Issues

The WebSocket server is generating warnings about missing event loops:

```
WARNING:coda.websocket:No event loop in current thread, event system_metrics dropped
```

This indicates that the WebSocket server is trying to send system metrics events, but there's no asyncio event loop in the thread where this is happening. This is causing the system metrics events to be dropped, which could affect the dashboard's ability to display performance information.

#### Potential Causes:
1. The system metrics are being generated in a thread that doesn't have an asyncio event loop
2. The WebSocket server's event loop architecture may have threading issues
3. There might be a mismatch between the threading model used for metrics collection and the one used for WebSocket communication

#### Potential Solutions:
1. Ensure all threads that need to send events have access to an event loop
2. Use a queue-based approach to transfer events from non-event-loop threads to the main event loop
3. Refactor the metrics collection to run in the same thread as the WebSocket server's event loop

## Memory System Issues

### Issue Description
The memory system is not functioning correctly as it doesn't remember information past the current conversation.

### Error Details
Initialization is failing due to missing ConfigLoader.get_all() method and system prompt file.

### Current Status
This issue is tracked separately and will be addressed after resolving the dashboard connection issues.

## Next Steps for Dashboard Implementation

1. **Complete External Audit**: Submit the codebase for external review to identify potential issues that may be causing the persistent React errors.

2. **Simplified Implementation**: Consider a complete rebuild with a more straightforward architecture:
   - Minimal component hierarchy
   - Simpler state management
   - Fewer dependencies between components
   - Clear separation between WebSocket handling and UI components

3. **Alternative Approaches**:
   - Test with different state management libraries (Redux, MobX, etc.)
   - Consider using a different WebSocket client library
   - Implement a proxy layer between the WebSocket server and the UI components

4. **Debugging Tools**:
   - Add more comprehensive logging
   - Use React DevTools to trace component updates
   - Implement performance monitoring for React renders
