# Memory Debug System

The Memory Debug System provides functionality for debugging and visualizing Coda's memory system, including both short-term and long-term memories. This feature is useful for developers and users to understand how Coda's memory works, diagnose issues, and visualize memory operations.

## Features

- **Memory Operation Logging**: Track all memory operations (add, retrieve, update, delete, etc.)
- **Memory Statistics**: Provide detailed statistics about the memory system
- **Memory Search**: Search for memories based on content, type, and importance
- **Memory Visualization**: Visualize memory operations and statistics in the dashboard
- **Memory Reinforcement**: Manually reinforce important memories
- **Memory Forgetting**: Manually forget (delete) memories or apply automatic forgetting
- **Memory Snapshots**: Create, save, load, and apply memory snapshots

## WebSocket Integration

The Memory Debug System is integrated with the WebSocket system to emit events when memory operations occur. These events can be used by the dashboard to display memory debug information.

### Event Types

- `MEMORY_DEBUG_OPERATION`: Emitted when a memory operation occurs
- `MEMORY_DEBUG_STATS`: Emitted when memory statistics are updated
- `MEMORY_DEBUG_SEARCH`: Emitted when a memory search is performed
- `MEMORY_DEBUG_REINFORCE`: Emitted when a memory is reinforced
- `MEMORY_DEBUG_FORGET`: Emitted when a memory is forgotten
- `MEMORY_DEBUG_SNAPSHOT`: Emitted when a memory snapshot operation occurs

### Event Format Examples

#### Memory Debug Operation Event

```json
{
  "type": "memory_debug_operation",
  "operation_type": "add_memory",
  "timestamp": "2025-04-26T12:34:56.789012",
  "details": {
    "memory_id": "memory_123",
    "memory_type": "fact",
    "importance": 0.8,
    "content_preview": "The user's name is Alice..."
  }
}
```

#### Memory Debug Stats Event

```json
{
  "type": "memory_debug_stats",
  "stats": {
    "short_term": {
      "turn_count": 10,
      "max_turns": 20
    },
    "long_term": {
      "memory_count": 100,
      "max_memories": 1000,
      "memory_types": {
        "fact": 50,
        "preference": 30,
        "conversation": 20
      }
    },
    "debug": {
      "operations_count": 50,
      "operations_by_type": {
        "add_memory": 20,
        "retrieve_memories": 15,
        "update_importance": 10,
        "forget": 5
      },
      "last_update": 1714147200.123
    }
  },
  "timestamp": 1714147200.123
}
```

## Usage

### Logging Memory Operations

```python
from memory.memory_debug import MemoryDebugSystem

# Initialize memory debug system
debug = MemoryDebugSystem(memory_manager=memory_manager, websocket_integration=ws)

# Log a memory operation
debug.log_operation(
    operation_type="add_memory",
    details={
        "memory_id": "memory_123",
        "memory_type": "fact",
        "importance": 0.8,
        "content_preview": "The user's name is Alice..."
    }
)
```

### Getting Memory Statistics

```python
# Get memory statistics
stats = debug.get_memory_stats()
```

### Searching for Memories

```python
# Search for memories
memories = debug.search_memories(
    query="Alice",
    memory_type="fact",
    min_importance=0.5,
    max_results=10
)
```

### Reinforcing a Memory

```python
# Reinforce a memory
debug.reinforce_memory(
    memory_id="memory_123",
    strength=0.8
)
```

### Forgetting a Memory

```python
# Forget a memory
debug.forget_memory(memory_id="memory_123")
```

### Applying the Forgetting Mechanism

```python
# Apply the forgetting mechanism
forgotten_count = debug.apply_forgetting_mechanism(max_memories=100)
```

### Creating a Memory Snapshot

```python
# Create a memory snapshot
snapshot_id = debug.create_memory_snapshot()
```

### Applying a Memory Snapshot

```python
# Apply a memory snapshot
success = debug.apply_memory_snapshot(snapshot_id="snapshot_123")
```

## Dashboard Integration

The Memory Debug System is designed to be integrated with the dashboard to provide a visual interface for debugging and visualizing the memory system. The dashboard can subscribe to memory debug events and display them in a user-friendly way.

### Memory Debug UI Components

- **Memory Operations Log**: Display a log of recent memory operations
- **Memory Statistics**: Display memory statistics and metrics
- **Memory Search**: Allow users to search for memories
- **Memory Visualization**: Visualize memory operations and statistics
- **Memory Controls**: Allow users to reinforce, forget, and snapshot memories

## Implementation Details

The Memory Debug System is implemented in the following files:

- `memory/memory_debug.py`: Contains the `MemoryDebugSystem` class that manages memory debugging
- `memory/websocket_memory.py`: Contains the `WebSocketEnhancedMemoryManager` class that integrates with the debug system
- `websocket/events.py`: Contains the event types and classes for memory debug events
- `websocket/integration_fixed.py`: Contains the WebSocket integration methods for memory debug events

## Future Enhancements

- **Memory Graph Visualization**: Visualize memory relationships as a graph
- **Memory Timeline**: Display memory operations on a timeline
- **Memory Comparison**: Compare memory states before and after operations
- **Memory Export/Import**: Export and import memory debug data
- **Memory Profiling**: Profile memory performance and usage
- **Memory Anomaly Detection**: Detect anomalies in memory operations
