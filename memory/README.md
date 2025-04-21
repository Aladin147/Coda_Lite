# Memory Module for Coda Lite

This module provides short-term memory management for Coda Lite, allowing the assistant to maintain context across conversation turns.

## Overview

The memory module stores conversation turns and provides context for the LLM within token limits. It also supports basic export/import functionality for debugging and future extensions.

## Features

- **Conversation Memory**: Stores user and assistant messages with timestamps
- **Token-Aware Context**: Provides context for the LLM within token limits
- **System Message Handling**: Always includes the system message in the context
- **Memory Export/Import**: Supports exporting and importing memory for debugging
- **Session Management**: Tracks session duration and turn count

## Usage

```python
from memory import MemoryManager

# Initialize the memory manager
memory = MemoryManager(max_turns=20)

# Add system message
memory.add_turn("system", "You are Coda, a helpful assistant.")

# Add user message
memory.add_turn("user", "Hello, who are you?")

# Add assistant message
memory.add_turn("assistant", "I'm Coda, your voice assistant. How can I help you today?")

# Get context for LLM
context = memory.get_context(max_tokens=800)

# Export memory to file
memory.export("data/memory/session.json")

# Reset memory
memory.reset()

# Import memory from file
memory.import_data("data/memory/session.json")
```

## Design Principles

The memory module is designed with the following principles in mind:

1. **Separation of Concerns**: Memory management is separated from other components
2. **Token Awareness**: Context is provided within token limits
3. **Future Extensibility**: The module is designed to be extended with long-term memory in the future
4. **Clean API**: The API is simple and easy to use

## Future Extensions

The memory module is designed to be extended with the following features in the future:

1. **Long-Term Memory**: Store and retrieve information across sessions
2. **Memory Summarization**: Summarize conversation history to save tokens
3. **Semantic Search**: Find relevant information in memory using embeddings
4. **Memory Visualization**: Visualize memory for debugging and analysis
