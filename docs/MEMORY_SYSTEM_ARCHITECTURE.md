# Memory System Architecture

## Overview

Coda's memory system is designed to provide both short-term and long-term memory capabilities, enabling Coda to maintain conversation context and remember important information across sessions. The memory system is modular, extensible, and integrated with the WebSocket architecture for real-time monitoring and visualization.

## Architecture Components

The memory system consists of the following key components:

### 1. Short-Term Memory

The `ShortTermMemory` class (implemented as `MemoryManager`) manages the current conversation context:

- Stores conversation turns in a deque with a configurable maximum length
- Preserves system messages regardless of deque size
- Provides context generation with token limits
- Supports export and import for persistence

### 2. Long-Term Memory

The `LongTermMemory` class manages persistent memory storage:

- Stores memories with content, metadata, and embeddings
- Supports multiple vector database backends (ChromaDB, SQLite, in-memory)
- Provides semantic search by content similarity
- Supports metadata-based search
- Implements memory pruning when maximum capacity is reached
- Manages topics for memory organization

### 3. Memory Encoder

The `MemoryEncoder` class handles the encoding of memories:

- Generates embeddings for semantic search
- Chunks long text into manageable pieces
- Assigns importance scores to memories
- Extracts topics from text

### 4. Enhanced Memory Manager

The `EnhancedMemoryManager` class integrates short-term and long-term memory:

- Manages both short-term and long-term memory components
- Provides a unified interface for memory operations
- Implements automatic persistence of short-term memory
- Enhances context generation with relevant memories
- Supports fact and preference storage
- Extracts topics from user messages

### 5. WebSocket Memory Integration

The `WebSocketEnhancedMemoryManager` extends the `EnhancedMemoryManager` with WebSocket capabilities:

- Emits events for memory operations
- Integrates with the WebSocket server for real-time monitoring
- Implements duplicate message detection
- Provides visualization of memory operations in the dashboard

## Data Flow

The memory system data flow follows these steps:

1. **Conversation Input**: User and assistant messages are added to short-term memory
2. **Context Generation**: Short-term memory provides context for LLM processing
3. **Memory Extraction**: Important information is extracted from conversations
4. **Long-Term Storage**: Extracted information is stored in long-term memory
5. **Memory Retrieval**: Relevant memories are retrieved for context enhancement
6. **Event Emission**: Memory operations emit events for monitoring and visualization

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  Conversation   │────▶│   Short-Term    │────▶│    Context      │
│     Input       │     │     Memory      │     │   Generation    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                                │                        ▲
                                ▼                        │
                        ┌─────────────────┐     ┌─────────────────┐
                        │     Memory      │     │     Memory      │
                        │   Extraction    │     │    Retrieval    │
                        └─────────────────┘     └─────────────────┘
                                │                        ▲
                                ▼                        │
                        ┌─────────────────┐     ┌─────────────────┐
                        │    Long-Term    │────▶│     Event       │
                        │     Memory      │     │    Emission     │
                        └─────────────────┘     └─────────────────┘
```

## Memory Types

The memory system supports several types of memories:

### 1. Conversation Turns

- **Role**: The speaker role (system, user, or assistant)
- **Content**: The message content
- **Timestamp**: When the message was sent
- **Turn Index**: The sequential index of the turn

### 2. Facts

- **Content**: The factual information
- **Importance**: A score indicating the importance of the fact
- **Source Type**: The type of source (conversation, user statement, etc.)
- **Metadata**: Additional information about the fact

### 3. Preferences

- **Content**: The user preference
- **Importance**: A score indicating the importance of the preference
- **Source Type**: The type of source (conversation, user statement, etc.)
- **Metadata**: Additional information about the preference

### 4. Topics

- **Name**: The topic name
- **Description**: A description of the topic
- **Memories**: Associated memory IDs
- **Metadata**: Additional information about the topic

## Vector Database Integration

The long-term memory system supports multiple vector database backends:

### 1. ChromaDB

- **Persistent Storage**: Stores memories on disk for persistence across sessions
- **Efficient Search**: Provides efficient semantic search capabilities
- **Metadata Filtering**: Supports filtering by metadata
- **Collection Management**: Organizes memories in collections

### 2. SQLite

- **Lightweight Storage**: Provides a lightweight alternative to ChromaDB
- **SQL Queries**: Supports SQL queries for advanced filtering
- **Portability**: Highly portable across platforms
- **No External Dependencies**: Doesn't require external services

### 3. In-Memory

- **Fast Access**: Provides the fastest access to memories
- **No Persistence**: Memories are lost when the application is closed
- **Minimal Setup**: Requires no additional setup or dependencies
- **Testing**: Ideal for testing and development

## Configuration Options

The memory system supports the following configuration options:

### Short-Term Memory

- **max_turns**: Maximum number of conversation turns to store (default: 20)
- **token_limit**: Maximum number of tokens for context generation (default: 4096)

### Long-Term Memory

- **vector_db**: Vector database backend to use (chroma, sqlite, in_memory)
- **long_term_path**: Path to store long-term memory data
- **max_memories**: Maximum number of memories to store (default: 1000)
- **embedding_model**: Model to use for generating embeddings
- **min_importance**: Minimum importance score for memories to be stored

### Enhanced Memory Manager

- **auto_persist**: Whether to automatically persist short-term memory (default: true)
- **persist_interval**: Number of assistant turns between persistence (default: 5)
- **max_context_memories**: Maximum number of memories to include in context (default: 5)
- **min_similarity**: Minimum similarity score for memory retrieval (default: 0.7)

## Implementation Details

### Memory Storage Format

Memories are stored in the following format:

```json
{
  "id": "uuid-string",
  "content": "Memory content text",
  "metadata": {
    "source_type": "fact",
    "importance": 0.8,
    "timestamp": "2023-04-25T12:34:56.789Z",
    "topic": "user_preferences"
  },
  "embedding": [0.1, 0.2, 0.3, ...]
}
```

### Memory Retrieval Process

The memory retrieval process follows these steps:

1. **Query Embedding**: Generate an embedding for the query
2. **Similarity Search**: Find memories with similar embeddings
3. **Filtering**: Apply metadata filters if specified
4. **Ranking**: Rank results by similarity score
5. **Limiting**: Return the top N results

### Memory Persistence Process

The memory persistence process follows these steps:

1. **Turn Analysis**: Analyze conversation turns for important information
2. **Fact Extraction**: Extract facts from the conversation
3. **Preference Extraction**: Extract preferences from the conversation
4. **Topic Extraction**: Extract topics from the conversation
5. **Storage**: Store extracted information in long-term memory
6. **Cleanup**: Clear short-term memory if configured

## WebSocket Integration

The memory system integrates with the WebSocket architecture for real-time monitoring and visualization:

- **Event Emission**: Memory operations emit events for monitoring
- **Dashboard Integration**: Events are visualized in the dashboard
- **Performance Tracking**: Memory operation performance is tracked
- **Duplicate Detection**: Duplicate messages are detected and filtered

See [WebSocket Memory Integration](WEBSOCKET_MEMORY_INTEGRATION.md) for more details.

## Testing

The memory system is thoroughly tested with unit tests, integration tests, and end-to-end tests:

- **Unit Tests**: Test individual components in isolation
- **Integration Tests**: Test the interaction between components
- **End-to-End Tests**: Test the full pipeline from memory operation to retrieval
- **WebSocket Tests**: Test the WebSocket integration

See [Memory System Tests](MEMORY_SYSTEM_TESTS.md) for more details on testing.

## Known Issues and Solutions

### 1. ChromaDB Availability

**Issue**: ChromaDB is not always available, causing fallback to in-memory storage.

**Solution**: Implement better error handling and fallback mechanisms, with clear user notifications.

### 2. Memory Duplication

**Issue**: Memories are sometimes duplicated in long-term storage.

**Solution**: Implement content-based deduplication during memory addition.

### 3. System Message Handling

**Issue**: System messages are sometimes lost when the conversation history is pruned.

**Solution**: Implement special handling for system messages to ensure they are always preserved.

### 4. WebSocket Errors

**Issue**: WebSocket errors can cause memory events to be dropped.

**Solution**: Implement better error handling and retry mechanisms for WebSocket communication.

## Future Enhancements

Planned enhancements for the memory system include:

1. **Temporal Weighting**: Implement time-based decay for memory importance
2. **Memory Forgetting**: Add mechanisms for intentional forgetting of less important memories
3. **Memory Debug UI**: Create a dedicated UI for memory debugging and visualization
4. **Active Recall**: Implement proactive memory recall based on conversation context
5. **Memory Summarization**: Add summarization of related memories for more concise context
6. **Memory Verification**: Implement verification of memories against external sources
7. **Memory Privacy Controls**: Add user controls for memory persistence and access

## Conclusion

Coda's memory system provides a robust foundation for maintaining conversation context and remembering important information across sessions. The modular architecture, vector database integration, and WebSocket capabilities enable a flexible, extensible, and observable memory system that enhances Coda's conversational abilities.

By addressing known issues and implementing planned enhancements, the memory system will continue to evolve as a core component of Coda's architecture.
