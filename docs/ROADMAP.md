# Coda Lite - Development Roadmap

This roadmap outlines the planned development path for Coda Lite, from initial prototype to a fully functional local voice assistant.

## Version Milestones

### v0.0.1 - Initial Setup ✅

- ✅ Project structure and repository setup
- ✅ Module placeholders and interfaces
- ✅ Documentation framework

### v0.0.1a - Basic Voice Loop ✅

- ✅ Speech-to-text with faster-whisper
- ✅ LLM integration with Ollama
- ✅ Text-to-speech with CSM-1B
- ✅ Simple conversation loop
- ✅ Latency optimization (target: sub-5s)

### v0.0.2 - Tool Integration ✅

- ✅ Structured output from LLM
- ✅ Tool router implementation
- ✅ Basic tools:
  - ✅ get_time()
  - ✅ tell_joke()
  - ✅ get_date()
- ✅ Tool execution and response formatting

### v0.0.3 - Enhanced Interaction ✅

- ✅ Improved system prompts
- ✅ Context management
- ✅ Conversation history
- ✅ Interruption handling
- ✅ Voice activity detection

### v0.0.4 - Personality & Customization ✅

- ✅ Voice customization options
- ✅ Personality tuning
- ✅ User preferences
- 🔄 Custom wake word

### v0.0.5 - Knowledge Integration ✅

- ✅ Local knowledge base
- ✅ Memory system with vector embeddings
- ✅ Long-term memory storage
- ✅ Personal data integration

### v0.1.0 - WebSocket Architecture ✅

- ✅ WebSocket server implementation
- ✅ Event-based communication
- ✅ Performance tracking
- ✅ TTS factory with ElevenLabs integration
- ✅ Modular architecture

### v0.1.1 - Dashboard Integration 🔄

- 🔄 React-based Tauri dashboard
- 🔄 Real-time visualization
- 🔄 Performance monitoring
- 🔄 Memory inspection
- 🔄 Tool usage tracking

### v0.2.0 - Beta Release ⏳

- ⏳ Wake word detection
- ⏳ Token streaming for real-time TTS
- ⏳ Additional languages support
- ⏳ Memory summarization
- ⏳ Comprehensive testing suite

### v1.0.0 - Production Release ⏳

- ⏳ Complete voice assistant functionality
- ⏳ Comprehensive tool set
- ⏳ Robust error handling
- ⏳ Performance optimization
- ⏳ User documentation

## Long-term Vision (v1.0 and beyond)

### Core Functionality Enhancements

- ⏳ Multi-modal input/output
- ⏳ Advanced context understanding
- ⏳ Proactive assistance
- ⏳ Multi-turn reasoning

### Technical Improvements

- ⏳ Model switching based on query complexity
- ⏳ Distributed processing for heavy tasks
- ⏳ Offline-first with optional cloud fallback
- ⏳ Hardware acceleration optimizations

### Ecosystem Development

- ⏳ Plugin system for third-party extensions
- ⏳ API for integration with other applications
- ⏳ Community model repository
- ⏳ Developer tools and SDK

---

*This roadmap is subject to change based on development progress, community feedback, and emerging technologies.*
