# Long-Term Memory System

This document describes the Long-Term Memory System in Coda Lite v0.1.4.

## Overview

The Long-Term Memory System allows Coda to remember information across sessions, providing a more personalized and contextually relevant experience. It uses vector embeddings to store and retrieve memories based on semantic similarity, with features like importance scoring, time decay, and memory chunking.

## Architecture

The Long-Term Memory System consists of the following components:

1. **LongTermMemory**: Core class for storing and retrieving memories using vector embeddings
2. **MemoryEncoder**: Utility for encoding conversations into memory chunks
3. **EnhancedMemoryManager**: Integration layer that combines short-term and long-term memory

## Features

### 1. Vector-Based Semantic Search

Coda uses sentence embeddings to store and retrieve memories based on semantic similarity:

```python
def retrieve_memories(self, query, limit=5, min_similarity=0.5, filter_criteria=None):
    # Generate query embedding
    query_embedding = self.embedding_model.encode(query)
    
    # Retrieve from vector database
    # ...
    
    # Apply time decay to adjust relevance
    memories = self._apply_time_decay(memories)
    
    return memories
```

### 2. Memory Importance Scoring

Memories are assigned importance scores based on their content:

```python
def _calculate_importance(self, text):
    # Base importance
    importance = 0.5
    
    # Check for important patterns
    for pattern_name, pattern in self.importance_patterns.items():
        matches = re.findall(pattern, text, re.IGNORECASE)
        if matches:
            # Different patterns have different weights
            if pattern_name == "preference":
                importance += 0.2
            elif pattern_name == "personal_info":
                importance += 0.3
            # ...
    
    # Cap at 1.0
    importance = min(importance, 1.0)
    
    return importance
```

### 3. Time Decay for Older Memories

Older memories are given less weight in retrieval:

```python
def _apply_time_decay(self, memories):
    now = datetime.now()
    
    for memory in memories:
        # Parse timestamp
        timestamp = memory.get("timestamp")
        if not timestamp:
            continue
            
        try:
            memory_time = datetime.fromisoformat(timestamp)
            
            # Calculate age in days
            age_days = (now - memory_time).total_seconds() / (24 * 3600)
            
            # Apply decay factor (half-life of 30 days)
            decay_factor = 2 ** (-age_days / 30)
            
            # Adjust similarity score
            original_similarity = memory.get("similarity", 0.5)
            importance = memory.get("importance", 0.5)
            
            # Final score combines similarity, importance, and time decay
            adjusted_score = original_similarity * importance * decay_factor
            
            # Update memory
            memory["adjusted_score"] = adjusted_score
            memory["decay_factor"] = decay_factor
            
        except Exception as e:
            logger.error(f"Error applying time decay: {e}")
            memory["adjusted_score"] = memory.get("similarity", 0.5)
    
    # Re-sort by adjusted score
    memories.sort(key=lambda x: x.get("adjusted_score", 0), reverse=True)
    
    return memories
```

### 4. Memory Chunking

Conversations are chunked into meaningful segments for storage:

```python
def encode_conversation(self, turns, include_system=False):
    # Filter turns if needed
    if not include_system:
        turns = [t for t in turns if t.get("role") != "system"]
    
    # Group turns by speaker
    grouped_turns = self._group_turns(turns)
    
    # Create chunks from grouped turns
    chunks = []
    for group in grouped_turns:
        group_chunks = self._create_chunks(group)
        chunks.extend(group_chunks)
    
    # Assign importance scores and metadata
    encoded_memories = []
    for chunk in chunks:
        importance = self._calculate_importance(chunk["content"])
        
        # Create memory
        memory = {
            "content": chunk["content"],
            "source_type": "conversation",
            "importance": importance,
            "metadata": {
                "speakers": chunk["speakers"],
                "turn_ids": chunk["turn_ids"],
                "timestamp": chunk["timestamp"],
                "topics": self._extract_topics(chunk["content"])
            }
        }
        
        encoded_memories.append(memory)
    
    return encoded_memories
```

### 5. User Summary

Coda maintains a summary of user preferences and information:

```python
def update_user_summary(self, key, value):
    self.metadata["user_summary"][key] = value
    self.metadata["last_updated"] = datetime.now().isoformat()
    self._save_metadata()
    logger.info(f"Updated user summary: {key} = {value}")

def get_user_summary(self, key=None):
    if key:
        return self.metadata["user_summary"].get(key)
    return self.metadata["user_summary"]
```

### 6. Enhanced Context Generation

Relevant memories are injected into the conversation context:

```python
def get_enhanced_context(self, user_input, max_tokens=800, max_memories=3):
    # Get short-term context
    context = self.short_term.get_context(max_tokens=max_tokens)
    
    # Retrieve relevant memories
    memories = self.retrieve_relevant_memories(user_input, limit=max_memories)
    
    # If we have memories, add them to the context
    if memories:
        # Find position to insert memories (after system message if present)
        insert_pos = 1 if context and context[0]["role"] == "system" else 0
        
        # Format memories as a system message
        memory_content = "Relevant information from previous conversations:\n\n"
        for i, memory in enumerate(memories):
            memory_content += f"{i+1}. {memory['content']}\n\n"
        
        # Insert memories
        context.insert(insert_pos, {
            "role": "system",
            "content": memory_content
        })
    
    return context
```

## Implementation Details

### Vector Database Options

The system supports multiple vector database backends:

1. **ChromaDB**: Persistent vector database with efficient similarity search
2. **SQLite**: Simple database with vector storage capabilities
3. **In-Memory**: Fallback option for testing or when other options are unavailable

### Memory Types

The system supports different types of memories:

1. **Conversation**: Chunks from user-assistant conversations
2. **Fact**: Explicit facts about the user or world
3. **Preference**: User preferences for various aspects

### Configuration

The long-term memory system can be configured in `config.yaml`:

```yaml
memory:
  # Long-term memory settings
  long_term_enabled: true
  long_term_path: "data/memory/long_term"
  embedding_model: "all-MiniLM-L6-v2"
  vector_db: "chroma"
  max_memories: 1000
  device: "cpu"
  
  # Memory encoding settings
  chunk_size: 200
  chunk_overlap: 50
  min_chunk_length: 50
  
  # Memory persistence settings
  auto_persist: true
  persist_interval: 5
```

## Memory Tools

The system provides several tools for interacting with memory:

1. **get_memory_stats**: Get statistics about the memory system
2. **add_fact**: Add a fact to long-term memory
3. **add_preference**: Add a user preference to long-term memory
4. **get_user_summary**: Get a summary of what Coda knows about the user
5. **search_memories**: Search long-term memories
6. **forget_session**: Forget the current session (reset short-term memory)

## Usage Examples

### Retrieving Relevant Memories

```python
# Get enhanced context with relevant memories
user_input = "What did we talk about regarding Python last time?"
context = memory_manager.get_enhanced_context(user_input)
```

### Adding Facts and Preferences

```python
# Add a fact
memory_manager.add_fact("The user's birthday is on May 15th.")

# Add a preference
memory_manager.add_preference("The user prefers concise responses.")
```

### Searching Memories

```python
# Search for memories about Python
memories = memory_manager.retrieve_relevant_memories("Python programming")
```

### Getting User Summary

```python
# Get user summary
summary = memory_manager.get_user_summary()
```

## Testing

A test script is provided to verify the Long-Term Memory System functionality:

```
python examples/test_long_term_memory.py
```

This script tests memory storage, retrieval, importance scoring, time decay, and integration with the enhanced memory manager.
