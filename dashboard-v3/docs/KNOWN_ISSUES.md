# Known Issues

This document tracks known issues in the Coda Dashboard v3.

## WebSocket Communication

### Asyncio Errors in Backend

When sending messages to Coda, you may see errors like this in the backend console:

```
ERROR:asyncio:Exception in callback _ProactorBaseWritePipeTransport._loop_writing(<_OverlappedF...hed result=17>)
handle: <Handle _ProactorBaseWritePipeTransport._loop_writing(<_OverlappedF...hed result=17>)>
Traceback (most recent call last):
  File "C:\Users\aladi\AppData\Local\Programs\Python\Python310\lib\asyncio\events.py", line 80, in _run
    self._context.run(self._callback, *self._args)
  File "C:\Users\aladi\AppData\Local\Programs\Python\Python310\lib\asyncio\proactor_events.py", line 381, in _loop_writing      
    assert f is self._write_fut
AssertionError
```

**Cause**: This is a known issue with Python's asyncio ProactorEventLoop on Windows. It's a race condition in the asyncio library where multiple write operations can overlap.

**Impact**: These errors don't affect functionality - Coda still responds to messages correctly.

**Workaround**: None needed, as it doesn't affect functionality.

**Fix**: This would require updating the server-side WebSocket implementation to handle concurrent writes better.

## UI Components

### WebSocketDebugger

The WebSocketDebugger component may show incorrect connection status information when the connection is lost and reconnected.

**Cause**: The component relies on polling the connection status, which may not always reflect the actual state.

**Impact**: The connection status display may be misleading.

**Workaround**: Refresh the page if you suspect the connection status is incorrect.

**Fix**: Improve the connection status tracking in the WebSocketClient.

### Performance Monitor

The Performance Monitor component may show zeros for all metrics until a new message is processed.

**Cause**: The component relies on receiving latency_trace events from the backend.

**Impact**: Performance metrics may not be displayed immediately.

**Workaround**: Send a message to Coda to trigger a new latency_trace event.

**Fix**: Add initial state loading for performance metrics.

## Browser Compatibility

### Safari WebSocket Support

Some versions of Safari may have issues with WebSocket connections.

**Cause**: Safari's implementation of WebSockets may differ from other browsers.

**Impact**: The dashboard may not connect to Coda in Safari.

**Workaround**: Use Chrome or Firefox instead.

**Fix**: Add browser-specific WebSocket handling for Safari.

## Development Environment

### Hot Module Replacement (HMR)

When using Vite's HMR, WebSocket connections may be lost and not automatically reconnected.

**Cause**: The WebSocketClient is recreated when the component is remounted.

**Impact**: You may need to refresh the page after code changes.

**Workaround**: Refresh the page after making code changes.

**Fix**: Improve the WebSocketClient to handle HMR better.
