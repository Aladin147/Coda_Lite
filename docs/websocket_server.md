# WebSocket Server Documentation

## Overview

The WebSocket server is a core component of Coda's architecture, providing a communication layer between the core logic and the user interface. It enables real-time bidirectional communication, allowing the UI to receive events from the core system and send commands to control its behavior.

## Architecture

The WebSocket server is implemented using Python's `websockets` library (version 15.0.1+) and follows a client-server model:

- **Server**: Runs as part of Coda's core system and handles client connections, event broadcasting, and command processing
- **Clients**: Connect to the server to receive events and send commands (e.g., the Tauri dashboard)

The server uses a JSON-based protocol for communication, with each message containing a type, data payload, and timestamp.

## Event Schema

Events sent from the server to clients follow this schema:

```json
{
  "type": "event_type",
  "data": {
    "key1": "value1",
    "key2": "value2"
  },
  "timestamp": "2025-05-01T12:34:56.789Z"
}
```

### Event Types

The server emits the following event types:

#### Speech-to-Text Events

- `stt_start`: Speech-to-text processing has started
- `stt_progress`: Intermediate speech-to-text results
- `stt_result`: Final speech-to-text result
- `stt_error`: Error during speech-to-text processing

#### Language Model Events

- `llm_start`: Language model processing has started
- `llm_progress`: Intermediate language model results (token streaming)
- `llm_result`: Final language model result
- `llm_error`: Error during language model processing

#### Text-to-Speech Events

- `tts_start`: Text-to-speech processing has started
- `tts_progress`: Intermediate text-to-speech results
- `tts_result`: Final text-to-speech result
- `tts_error`: Error during text-to-speech processing

#### Memory Events

- `memory_store`: Memory item has been stored
- `memory_recall`: Memory item has been recalled
- `memory_error`: Error during memory operation

#### Tool Events

- `tool_call`: Tool has been called
- `tool_result`: Tool has returned a result
- `tool_error`: Error during tool execution

#### System Events

- `system_info`: System information (version, uptime, memory usage)
- `latency_trace`: Performance metrics for various components
- `connection_status`: Connection status changes
- `replay`: Replay of events for new clients

## Command Schema

Commands sent from clients to the server follow this schema:

```json
{
  "type": "command_type",
  "data": {
    "key1": "value1",
    "key2": "value2"
  },
  "timestamp": "2025-05-01T12:34:56.789Z"
}
```

### Command Types

The server accepts the following command types:

#### Speech-to-Text Commands

- `stt_start`: Start speech-to-text processing
  - `mode`: Mode of operation (e.g., `push_to_talk`, `continuous`)
- `stt_stop`: Stop speech-to-text processing

#### System Commands

- `demo_flow`: Run a demo of the complete voice interaction flow
- `get_system_info`: Request system information
- `get_performance_metrics`: Request performance metrics

## Implementation

The WebSocket server is implemented in the `websocket/server.py` file. It provides the following functionality:

- Client connection management
- Event broadcasting to all connected clients
- Command processing and routing
- Event replay for new clients
- Error handling and logging

### Server Class

The `WebSocketServer` class is the main entry point for the WebSocket server. It provides methods for starting and stopping the server, broadcasting events, and handling client connections.

```python
class WebSocketServer:
    def __init__(self, host="localhost", port=8765):
        self.host = host
        self.port = port
        self.clients = set()
        self.running = False
        self.server = None
        self.event_buffer = []
        self.buffer_size = 100
        
    async def start(self):
        """Start the WebSocket server."""
        # Implementation details...
        
    async def stop(self):
        """Stop the WebSocket server."""
        # Implementation details...
        
    async def broadcast(self, event):
        """Broadcast an event to all connected clients."""
        # Implementation details...
        
    async def _handle_client(self, websocket, path):
        """Handle a client connection."""
        # Implementation details...
```

## Usage

To use the WebSocket server, you need to:

1. Create an instance of the `WebSocketServer` class
2. Start the server with the `start()` method
3. Broadcast events with the `broadcast()` method
4. Stop the server with the `stop()` method when done

```python
import asyncio
from websocket.server import WebSocketServer

async def main():
    server = WebSocketServer(host="localhost", port=8765)
    await server.start()
    
    # Broadcast an event
    event = {
        "type": "system_info",
        "data": {
            "version": "0.1.1",
            "uptime": 3600,
            "memory": 1024 * 1024 * 100
        },
        "timestamp": "2025-05-01T12:34:56.789Z"
    }
    await server.broadcast(event)
    
    # Run forever
    try:
        await asyncio.Future()
    finally:
        await server.stop()

if __name__ == "__main__":
    asyncio.run(main())
```

## Compatibility

The WebSocket server is compatible with:

- Python 3.8+
- websockets 15.0.1+
- Any WebSocket client that supports the standard WebSocket protocol

## Security Considerations

The WebSocket server currently does not implement authentication or encryption. It is intended for local use only and should not be exposed to the public internet without additional security measures.

## Related Documentation

- [Dashboard Documentation](dashboard_documentation.md) - Documentation for the Tauri dashboard
- [Architecture Transformation Roadmap](ARCHITECTURE_ROADMAP.md) - Detailed plan for the WebSocket-based architecture

---

*This document will be updated as the WebSocket server evolves.*
