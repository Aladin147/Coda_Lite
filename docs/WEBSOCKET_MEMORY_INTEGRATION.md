# WebSocket Memory Integration

## Overview

The WebSocket Memory Integration is a key component of Coda's architecture, enabling real-time communication between the memory system and the dashboard. This integration allows for event-based monitoring of memory operations, providing visibility into Coda's memory processes and enabling a more interactive user experience.

## Architecture

The WebSocket Memory Integration follows a publisher-subscriber pattern:

1. **Memory System (Publisher)**: Emits events for memory operations
2. **WebSocket Server (Broker)**: Receives events and distributes them to connected clients
3. **Dashboard (Subscriber)**: Receives and visualizes memory events

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Memory System  │────▶│ WebSocket Server │────▶│    Dashboard    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
        │                        ▲                       │
        │                        │                       │
        └────────────────────────┴───────────────────────┘
                      Event-based Communication
```

## Components

### 1. WebSocketEnhancedMemoryManager

The `WebSocketEnhancedMemoryManager` extends the `EnhancedMemoryManager` to emit WebSocket events for memory operations:

- **Memory Addition**: Emits events when memories are added to long-term storage
- **Memory Retrieval**: Emits events when memories are retrieved from long-term storage
- **Conversation Turns**: Emits events when conversation turns are added
- **Memory Persistence**: Emits events when short-term memory is persisted to long-term memory
- **Memory Clearing**: Emits events when short-term memory is cleared

### 2. CodaWebSocketIntegration

The `CodaWebSocketIntegration` class provides the interface between the memory system and the WebSocket server:

- **Event Emission**: Sends memory events to the WebSocket server
- **Duplicate Detection**: Prevents duplicate messages from being sent
- **Event Formatting**: Formats memory events according to the WebSocket protocol
- **Error Handling**: Handles errors in event emission

### 3. WebSocket Server

The WebSocket server handles the communication between the memory system and the dashboard:

- **Connection Management**: Manages client connections and disconnections
- **Event Distribution**: Distributes events to connected clients
- **Replay Buffer**: Stores recent events for new connections
- **Authentication**: Optionally authenticates clients

## Event Types

The WebSocket Memory Integration emits the following event types:

### Memory Events

- **memory_store**: Emitted when a memory is added to long-term storage
  ```json
  {
    "type": "memory_store",
    "memory_id": "uuid-string",
    "content": "Memory content text",
    "metadata": {
      "source_type": "fact",
      "importance": 0.8,
      "timestamp": "2023-04-25T12:34:56.789Z"
    }
  }
  ```

- **memory_retrieve**: Emitted when memories are retrieved from long-term storage
  ```json
  {
    "type": "memory_retrieve",
    "query": "Search query text",
    "results": [
      {
        "id": "uuid-string",
        "content": "Memory content text",
        "metadata": {
          "source_type": "fact",
          "importance": 0.8,
          "timestamp": "2023-04-25T12:34:56.789Z"
        },
        "similarity": 0.92
      }
    ]
  }
  ```

### Conversation Events

- **conversation_turn**: Emitted when a conversation turn is added
  ```json
  {
    "type": "conversation_turn",
    "role": "user",
    "content": "User message text",
    "turn_index": 42,
    "timestamp": "2023-04-25T12:34:56.789Z"
  }
  ```

### System Events

- **memory_persist**: Emitted when short-term memory is persisted to long-term memory
  ```json
  {
    "type": "memory_persist",
    "turn_count": 10,
    "memories_added": 3,
    "timestamp": "2023-04-25T12:34:56.789Z"
  }
  ```

- **memory_clear**: Emitted when short-term memory is cleared
  ```json
  {
    "type": "memory_clear",
    "timestamp": "2023-04-25T12:34:56.789Z"
  }
  ```

## Implementation Details

### WebSocketEnhancedMemoryManager

The `WebSocketEnhancedMemoryManager` extends the `EnhancedMemoryManager` with WebSocket event emission:

```python
class WebSocketEnhancedMemoryManager(EnhancedMemoryManager):
    def __init__(self, config=None, websocket_integration=None):
        super().__init__(config=config)
        self.websocket_integration = websocket_integration or CodaWebSocketIntegration()

    def add_memory(self, content, memory_type="fact", importance=0.5, metadata=None):
        # Add memory to long-term storage
        memory = super().add_memory(content, memory_type, importance, metadata)
        
        # Emit WebSocket event
        if self.websocket_integration:
            self.websocket_integration.memory_store(memory)
        
        return memory

    def get_memories(self, query, limit=5, min_similarity=0.0):
        # Retrieve memories from long-term storage
        memories = super().get_memories(query, limit, min_similarity)
        
        # Emit WebSocket event
        if self.websocket_integration:
            self.websocket_integration.memory_retrieve(query=query, results=memories)
        
        return memories

    def add_turn(self, role, content):
        # Add conversation turn
        turn = super().add_turn(role, content)
        
        # Emit WebSocket event
        if self.websocket_integration:
            self.websocket_integration.add_conversation_turn(role=role, content=content, turn=turn)
        
        return turn

    def persist_short_term_memory(self):
        # Persist short-term memory to long-term memory
        memories = super().persist_short_term_memory()
        
        # Emit WebSocket event
        if self.websocket_integration:
            self.websocket_integration.memory_persist(
                turn_count=self.short_term.turn_count,
                memories_added=len(memories)
            )
        
        return memories

    def clear_short_term(self):
        # Clear short-term memory
        super().clear_short_term()
        
        # Emit WebSocket event
        if self.websocket_integration:
            self.websocket_integration.memory_clear()
```

### CodaWebSocketIntegration

The `CodaWebSocketIntegration` class provides the interface to the WebSocket server:

```python
class CodaWebSocketIntegration:
    def __init__(self):
        self.server = None
        self.message_cache = {}
        self.cache_size = 100
        self.logger = logging.getLogger("coda.websocket.integration")

    def set_server(self, server):
        self.server = server

    def memory_store(self, memory):
        if not self.server:
            return False
        
        # Create event data
        event_data = {
            "type": "memory_store",
            "memory_id": memory["id"],
            "content": memory["content"],
            "metadata": memory["metadata"]
        }
        
        # Check for duplicates
        message_hash = self._hash_message(event_data)
        if self._is_duplicate(message_hash):
            self.logger.warning(f"Duplicate message detected: {event_data['type']}")
            return False
        
        # Send event
        self.server.broadcast_event(event_data)
        return True

    def memory_retrieve(self, query, results):
        if not self.server:
            return False
        
        # Create event data
        event_data = {
            "type": "memory_retrieve",
            "query": query,
            "results": results
        }
        
        # Check for duplicates
        message_hash = self._hash_message(event_data)
        if self._is_duplicate(message_hash):
            self.logger.warning(f"Duplicate message detected: {event_data['type']}")
            return False
        
        # Send event
        self.server.broadcast_event(event_data)
        return True

    def add_conversation_turn(self, role, content, turn):
        if not self.server:
            return False
        
        # Create event data
        event_data = {
            "type": "conversation_turn",
            "role": role,
            "content": content,
            "turn_index": turn["turn_index"],
            "timestamp": turn["timestamp"]
        }
        
        # Check for duplicates
        message_hash = self._hash_message(event_data)
        if self._is_duplicate(message_hash):
            self.logger.warning(f"Duplicate message detected: {event_data['type']}")
            return False
        
        # Send event
        self.server.broadcast_event(event_data)
        return True

    def memory_persist(self, turn_count, memories_added):
        if not self.server:
            return False
        
        # Create event data
        event_data = {
            "type": "memory_persist",
            "turn_count": turn_count,
            "memories_added": memories_added,
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for duplicates
        message_hash = self._hash_message(event_data)
        if self._is_duplicate(message_hash):
            self.logger.warning(f"Duplicate message detected: {event_data['type']}")
            return False
        
        # Send event
        self.server.broadcast_event(event_data)
        return True

    def memory_clear(self):
        if not self.server:
            return False
        
        # Create event data
        event_data = {
            "type": "memory_clear",
            "timestamp": datetime.now().isoformat()
        }
        
        # Check for duplicates
        message_hash = self._hash_message(event_data)
        if self._is_duplicate(message_hash):
            self.logger.warning(f"Duplicate message detected: {event_data['type']}")
            return False
        
        # Send event
        self.server.broadcast_event(event_data)
        return True

    def _hash_message(self, message):
        # Create a hash of the message for duplicate detection
        return hashlib.md5(json.dumps(message, sort_keys=True).encode()).hexdigest()

    def _is_duplicate(self, message_hash):
        # Check if the message is a duplicate
        if message_hash in self.message_cache:
            return True
        
        # Add to cache
        self.message_cache[message_hash] = time.time()
        
        # Prune cache if needed
        if len(self.message_cache) > self.cache_size:
            # Remove oldest entries
            oldest = sorted(self.message_cache.items(), key=lambda x: x[1])
            for i in range(len(oldest) - self.cache_size):
                del self.message_cache[oldest[i][0]]
        
        return False
```

## Dashboard Integration

The dashboard integrates with the WebSocket Memory Integration to visualize memory events:

- **Memory Viewer**: Displays memories from the memory_store and memory_retrieve events
- **Conversation View**: Displays conversation turns from the conversation_turn events
- **System Events**: Displays system events like memory_persist and memory_clear
- **Performance Metrics**: Tracks memory operation performance

## Known Issues and Solutions

### 1. Duplicate Messages

**Issue**: The WebSocket server sometimes receives duplicate messages, especially during high-load operations.

**Solution**: Implemented a message cache with hash-based duplicate detection in the `CodaWebSocketIntegration` class.

### 2. Missing Event Loops

**Issue**: Warnings about missing event loops in current threads, causing system_metrics events to be dropped.

**Solution**: Use `asyncio.call_soon_threadsafe` or `asyncio.Queue` to properly handle events across threads.

### 3. Concurrent Write Errors

**Issue**: AsyncIO errors with 'AssertionError: assert f is self._write_fut' in _ProactorBaseWritePipeTransport._loop_writing.

**Solution**: Implement proper synchronization for WebSocket writes to prevent concurrent access.

### 4. Memory Duplication

**Issue**: Memory events sometimes appear multiple times in the dashboard.

**Solution**: Enhanced duplicate detection in both the WebSocket integration and the dashboard.

## Testing

The WebSocket Memory Integration is thoroughly tested with the following test cases:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test the interaction between components
- **End-to-End Tests**: Test the full pipeline from memory operation to dashboard visualization
- **Stress Tests**: Test behavior under high load
- **Error Handling Tests**: Test behavior when errors occur

See [Memory System Tests](MEMORY_SYSTEM_TESTS.md) for more details on testing.

## Future Enhancements

Planned enhancements for the WebSocket Memory Integration include:

1. **Event Prioritization**: Prioritize important events during high-load situations
2. **Event Batching**: Batch multiple events together for more efficient transmission
3. **Selective Subscription**: Allow clients to subscribe to specific event types
4. **Enhanced Security**: Add more robust authentication and authorization
5. **Performance Optimization**: Optimize event serialization and transmission
6. **Improved Error Recovery**: Better handling of connection failures and reconnection
7. **Event Replay**: Allow clients to request replay of specific event types or time ranges

## Conclusion

The WebSocket Memory Integration is a critical component of Coda's architecture, enabling real-time communication between the memory system and the dashboard. This integration provides visibility into Coda's memory processes and enables a more interactive user experience.

By addressing known issues and implementing planned enhancements, the WebSocket Memory Integration will continue to evolve as a robust and efficient communication channel for Coda's memory system.
