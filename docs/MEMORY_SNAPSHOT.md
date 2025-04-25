# Memory Snapshot System

The Memory Snapshot System provides functionality to create, save, and load snapshots of Coda's memory system, including both short-term and long-term memories. This feature is useful for debugging, analysis, and preserving the state of the memory system at specific points in time.

## Features

- **Create Snapshots**: Capture the current state of the memory system, including short-term conversation history and long-term memories.
- **Save Snapshots**: Save snapshots to disk for later analysis or restoration.
- **Load Snapshots**: Load previously saved snapshots.
- **Apply Snapshots**: Restore the memory system to a previous state.
- **Automatic Snapshots**: Automatically create snapshots at regular intervals.
- **WebSocket Integration**: Emit events when snapshots are created, saved, loaded, or applied.

## Configuration

The Memory Snapshot System can be configured in the `config.yaml` file:

```yaml
memory:
  # Other memory settings...
  
  # Memory snapshot settings
  snapshot_dir: data/memory/snapshots
  auto_snapshot: true
  snapshot_interval: 10
```

- `snapshot_dir`: Directory to store snapshots (default: `data/memory/snapshots`)
- `auto_snapshot`: Whether to automatically create snapshots (default: `false`)
- `snapshot_interval`: Number of turns between automatic snapshots (default: `10`)

## Usage

### Creating a Snapshot

```python
from memory import EnhancedMemoryManager

# Initialize memory manager
memory = EnhancedMemoryManager(config)

# Create a snapshot
snapshot_id = memory.create_snapshot()
```

### Saving a Snapshot

```python
# Save a snapshot to disk
filepath = memory.save_snapshot(snapshot_id)
```

### Loading a Snapshot

```python
# Load a snapshot from disk
loaded_id = memory.load_snapshot(filepath)
```

### Applying a Snapshot

```python
# Apply a snapshot to restore the memory system
success = memory.apply_snapshot(snapshot_id)
```

### Listing Snapshots

```python
# List all snapshots
snapshots = memory.list_snapshots()
```

### Enabling Automatic Snapshots

```python
# Enable automatic snapshots
memory.enable_auto_snapshot(interval=10)
```

### Disabling Automatic Snapshots

```python
# Disable automatic snapshots
memory.disable_auto_snapshot()
```

## WebSocket Integration

The Memory Snapshot System is integrated with the WebSocket system to emit events when snapshots are created, saved, loaded, or applied. These events can be used by the dashboard to display snapshot information.

### Event Format

```json
{
  "memory_snapshot": {
    "action": "create",
    "snapshot_id": "snapshot_20250426_123456_abcd1234",
    "metadata": {
      "snapshot_id": "snapshot_20250426_123456_abcd1234",
      "timestamp": "2025-04-26T12:34:56.789012",
      "short_term_turns": 10,
      "long_term_memories": 100,
      "topics": 5
    }
  }
}
```

## Snapshot Structure

A memory snapshot contains the following information:

```json
{
  "snapshot_id": "snapshot_20250426_123456_abcd1234",
  "timestamp": "2025-04-26T12:34:56.789012",
  "short_term": {
    "turns": [
      {"role": "system", "content": "You are Coda."},
      {"role": "user", "content": "Hello, who are you?"},
      {"role": "assistant", "content": "I'm Coda, your voice assistant."}
    ],
    "turn_count": 3,
    "session_start": "2025-04-26T12:00:00.000000"
  },
  "long_term": {
    "memories": {
      "memory_1": {
        "content": "The user's name is Alice.",
        "timestamp": "2025-04-26T12:05:00.000000",
        "importance": 0.8,
        "metadata": {
          "source_type": "fact",
          "topics": ["user", "name"]
        }
      },
      "memory_2": {
        "content": "The user prefers brief responses.",
        "timestamp": "2025-04-26T12:10:00.000000",
        "importance": 0.7,
        "metadata": {
          "source_type": "preference",
          "topics": ["user", "preference", "communication"]
        }
      }
    },
    "topics": ["user", "name", "preference", "communication"],
    "memory_count": 2
  },
  "memory_stats": {
    "short_term": {
      "turn_count": 3,
      "session_duration": 2100.0
    },
    "long_term": {
      "total_memories": 2,
      "source_types": {
        "fact": 1,
        "preference": 1
      },
      "average_importance": 0.75,
      "oldest_memory": "2025-04-26T12:05:00.000000",
      "newest_memory": "2025-04-26T12:10:00.000000",
      "topics": 4,
      "user_summary_keys": []
    },
    "recent_topics": ["user", "name", "preference", "communication"],
    "last_tool_used": null
  }
}
```

## Implementation Details

The Memory Snapshot System is implemented in the following files:

- `memory/memory_snapshot.py`: Contains the `MemorySnapshotManager` class that manages snapshots.
- `memory/enhanced_memory_manager.py`: Contains the `EnhancedMemoryManager` class that integrates with the snapshot manager.
- `memory/websocket_memory.py`: Contains the `WebSocketEnhancedMemoryManager` class that adds WebSocket event emission.

## Future Enhancements

- **Snapshot Comparison**: Add functionality to compare two snapshots and identify differences.
- **Snapshot Filtering**: Add functionality to filter snapshots by date, content, or other criteria.
- **Snapshot Pruning**: Add functionality to automatically delete old snapshots to save disk space.
- **Snapshot Compression**: Add functionality to compress snapshots to save disk space.
- **Snapshot Encryption**: Add functionality to encrypt snapshots for security.
- **Snapshot Visualization**: Add functionality to visualize snapshots in the dashboard.
