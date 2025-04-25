# Coda Lite Architecture

This document provides a comprehensive overview of the Coda Lite architecture, including its components, interactions, and design principles.

## System Overview

Coda Lite is a modular, extensible digital assistant with a focus on local processing, privacy, and customization. The system is designed with a WebSocket-based architecture that decouples the core logic from the user interface, allowing for flexible deployment options.

### Key Components

1. **Core Processing Pipeline**
   - Speech-to-Text (STT)
   - Language Model (LLM)
   - Text-to-Speech (TTS)
   - Memory System
   - Intent Router
   - Tool System

2. **Communication Layer**
   - WebSocket Server
   - Event System
   - Message Queue

3. **User Interface**
   - React Dashboard
   - Voice Controls
   - Visualization Components

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                        Coda Lite Core                           │
│                                                                 │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐      │
│  │   STT   │───▶│   LLM   │───▶│  Intent │───▶│   TTS   │      │
│  │ (Whisper)│    │ (Gemma) │    │ Router  │    │(ElevenLabs)│   │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘      │
│        │              │              │              │           │
│        │              │              │              │           │
│        │              ▼              ▼              │           │
│        │        ┌─────────────────────────┐         │           │
│        └───────▶│      Memory System      │◀────────┘           │
│                 │                         │                     │
│                 │  ┌─────────────────┐    │                     │
│                 │  │   Short-term    │    │                     │
│                 │  └─────────────────┘    │                     │
│                 │                         │                     │
│                 │  ┌─────────────────┐    │                     │
│                 │  │    Long-term    │    │                     │
│                 │  └─────────────────┘    │                     │
│                 └─────────────────────────┘                     │
│                              │                                  │
│                              │                                  │
│                              ▼                                  │
│                     ┌─────────────────┐                         │
│                     │   Tool System   │                         │
│                     └─────────────────┘                         │
│                              │                                  │
└──────────────────────────────┼──────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                      WebSocket Server                           │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Event System   │    │  Message Queue  │    │ Integration │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
                               │
                               ▼
┌─────────────────────────────────────────────────────────────────┐
│                        Dashboard (React)                        │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │  Voice Controls │    │ Conversation UI │    │ Memory View │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                                                 │
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │ Performance UI  │    │   System Info   │    │  Tool View  │  │
│  └─────────────────┘    └─────────────────┘    └─────────────┘  │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Component Details

### Speech-to-Text (STT)

The STT module is responsible for converting audio input to text. It uses Whisper for local speech recognition.

**Key Features:**
- Local processing with Whisper
- Support for multiple languages
- Configurable audio settings
- Real-time transcription

### Language Model (LLM)

The LLM module is the reasoning engine of Coda. It processes text input and generates responses.

**Key Features:**
- Local processing with Gemma 2B
- Fallback to LLaMA 3 8B
- Prompt management
- Context window management
- Tool calling capabilities

### Text-to-Speech (TTS)

The TTS module converts text responses to speech output.

**Key Features:**
- ElevenLabs API integration
- Dia TTS for local processing
- Voice selection
- Speech parameter customization

### Memory System

The memory system stores and retrieves information about conversations and user preferences.

**Key Features:**
- Short-term conversation memory
- Long-term vector-based memory
- Memory encoding and chunking
- Enhanced memory manager
- Memory snapshot system
- Temporal weighting system
- Memory debug system
- Active recall system
- Memory self-testing framework
- Memory summarization system

### Intent Router

The intent router analyzes user input and determines the appropriate action or response.

**Key Features:**
- Intent classification
- Action mapping
- Response generation
- Tool selection

### Tool System

The tool system provides additional capabilities to Coda through external integrations.

**Key Features:**
- Tool registration
- Tool calling
- Result processing
- Error handling

### WebSocket Server

The WebSocket server facilitates communication between the core system and the user interface.

**Key Features:**
- Real-time bidirectional communication
- Event emission
- Message queuing
- Connection management

### Dashboard

The dashboard provides a visual interface for interacting with Coda.

**Key Features:**
- Voice controls
- Conversation view
- Memory visualization
- Performance monitoring
- System information
- Tool usage display

## Data Flow

1. **User Input**
   - User speaks or types input
   - Input is captured by the dashboard
   - Input is sent to the core system via WebSocket

2. **Processing**
   - STT converts audio to text (if voice input)
   - LLM processes the text input
   - Intent router determines the appropriate action
   - Tools are called if needed
   - Memory is updated with the conversation

3. **Response Generation**
   - LLM generates a response
   - Response is processed by the intent router
   - Response is sent to the TTS module
   - TTS converts text to speech

4. **User Interface Update**
   - Response is sent to the dashboard via WebSocket
   - Dashboard updates the conversation view
   - Dashboard plays the audio response
   - Dashboard updates memory and performance visualizations

## Design Principles

### Modularity

Coda is designed with a modular architecture, allowing components to be replaced or upgraded independently. This enables easy experimentation with different models and approaches.

### Decoupling

The core logic is decoupled from the user interface through a WebSocket-based communication layer. This allows the core to run as a CLI application while the dashboard provides a visual interface.

### Extensibility

The system is designed to be easily extended with new capabilities through the tool system and modular components.

### Performance

Coda prioritizes performance and responsiveness, with a focus on local processing and efficient resource usage.

### Privacy

By prioritizing local processing, Coda respects user privacy and reduces dependency on external services.

## Implementation Details

### Memory System

The memory system is a key component of Coda, providing both short-term and long-term memory capabilities.

#### Short-Term Memory

Short-term memory stores the current conversation context, including:
- User messages
- Assistant responses
- System messages
- Tool calls and results

#### Long-Term Memory

Long-term memory stores persistent information, including:
- User preferences
- Facts about the user
- Important conversation snippets
- Tool usage patterns

#### Memory Enhancements

The memory system includes several enhancements:
- **Memory Snapshot**: Captures the state of memory for debugging and analysis
- **Temporal Weighting**: Applies time-based decay to memory importance
- **Memory Debug**: Provides tools for inspecting and debugging memory
- **Active Recall**: Tests and reinforces important memories
- **Memory Self-Testing**: Verifies memory integrity and retrieval accuracy
- **Memory Summarization**: Generates summaries of memory clusters and user profiles

### WebSocket Integration

The WebSocket server provides real-time communication between the core system and the dashboard.

#### Event System

The event system emits events for various system activities, including:
- Conversation events (user input, assistant response)
- Memory events (memory updates, retrievals)
- Performance events (component timing, resource usage)
- System events (startup, shutdown, errors)

#### Message Queue

The message queue ensures that events are processed in order and prevents message loss during high activity.

### Dashboard

The dashboard provides a visual interface for interacting with Coda.

#### React Components

The dashboard is built with React and includes components for:
- Voice controls (push-to-talk, demo mode)
- Conversation view (message history, typing indicators)
- Memory visualization (memory browser, topic clusters)
- Performance monitoring (component timing, resource usage)
- System information (status, configuration)
- Tool usage display (tool calls, results)

#### WebSocket Client

The dashboard includes a WebSocket client for communicating with the core system, handling:
- Connection management
- Event processing
- Message sending
- Error handling

## Future Directions

### Architecture Improvements

- Fully decouple core logic from UI
- Implement a more modular architecture
- Create a plugin system for extensions

### Dashboard Enhancements

- Implement memory visualization components
- Create user profile display
- Add memory cluster visualization

### Performance Optimizations

- Optimize memory retrieval with better caching
- Improve summarization performance
- Enhance WebSocket event handling

## Conclusion

Coda Lite's architecture is designed for flexibility, extensibility, and performance. By decoupling the core logic from the user interface and implementing a modular design, Coda can evolve and improve over time while maintaining a consistent user experience.
