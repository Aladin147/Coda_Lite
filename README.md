# Coda Lite – Core Operations & Digital Assistant (v0.1.1)

**Coda Lite** is a lightweight, local-first voice assistant prototype focused on one thing:
⚡ **Real-time, low-latency, human-feeling conversation.**

No cloud. No bloat. No gimmicks.
Just a responsive, modular base for something much bigger.

---

## 🎯 Goals

Coda Lite aims to:

- Run **fully locally** on consumer hardware
- Provide **natural back-and-forth voice interaction**
- Operate with **sub-3s latency per interaction**
- Execute **basic tool functions** via structured LLM output
- Be **easy to extend and customize**

This project is the **first step** in building an open, modular, transparent AI assistant stack designed for real-world usefulness — not demos or hype.

---

## 📦 Tech Stack

| Layer         | Tool                             | Purpose                        |
|---------------|----------------------------------|--------------------------------|
| 🎙️ STT        | [faster-whisper](https://github.com/guillaumekln/faster-whisper)  | Local speech-to-text          |
| 🧠 LLM        | [Ollama](https://ollama.com/) + LLaMA 3 / DeepSeek   | Local reasoning engine        |
| 🗣️ TTS        | [ElevenLabs](https://elevenlabs.io/) / [MeloTTS (CSM-1B)](https://github.com/myshell-ai/MeloTTS) / [Dia TTS](https://github.com/nari-labs/dia)      | High-quality speech generation       |
| 🔧 Tools      | Python function routing          | Responding to structured LLM output |

---

## ✅ Completed in `v0.1.0` - WebSocket Architecture

> 🔸 **Modular, decoupled system with WebSocket communication!**

- WebSocket server implementation for decoupled architecture
- Event-based communication between components
- Performance tracking throughout the system
- TTS factory with ElevenLabs integration
- Modular architecture for easy extension
- STT module fully implemented with Whisper (GPU-accelerated)
- LLM integration with Ollama complete
- TTS module implemented with MeloTTS (CSM-1B), Dia TTS, and ElevenLabs
- Multiple English voices available (US, British, Australian, Indian)
- Concurrent processing with threading for reduced latency
- Advanced personality engine with behavioral conditioning
- Long-term memory with vector embeddings and semantic search
- Intent routing system with pattern-based detection
- User feedback hooks for collecting and processing feedback
- Memory-based personality conditioning system
- Mini-command language with system commands
- Tools include `get_time()`, `get_date()`, `tell_joke()`, etc.

---

## 🚀 Current Version: `v0.1.1` - Dashboard Integration

> Visual interface for monitoring and interaction:

- React-based dashboard implementation ✅
- Real-time visualization of system events ✅
- Performance monitoring and metrics display ✅
- Memory inspection and visualization ✅
- Tool usage tracking and display ✅
- Conversation view with real-time updates ✅
- Push-to-talk and demo functionality ✅
- Dark/light theme support (dark mode default) ✅
- WebSocket server compatibility with websockets 15.0.1+ ✅
- Responsive design for different screen sizes ✅
- Event queue system for non-blocking event handling ✅
- Accurate performance metrics with component-specific timing ✅

**Dashboard Features:**

- Avatar with speaking animation
- Real-time event log
- Performance metrics visualization
  - Processing time metrics (STT, LLM, TTS)
  - Audio duration metrics (user speaking, Coda speaking)
  - Total conversation time tracking
- Memory viewer
- Tool usage cards
- System information display
- Theme toggle for light/dark mode
- Text input option alongside voice input

See [WebSocket Dashboard Documentation](docs/WEBSOCKET_DASHBOARD.md) for more details.

## 🔜 Future: `v0.2.0` - Beta Release

> Feature-complete with stability improvements:

- Wake word detection for hands-free activation
- Token streaming for real-time TTS output
- Voice quality improvements and tuning
- Additional languages support
- Improved error handling and recovery
- Expanded personality with context-aware responses
- Memory summarization for longer conversations
- Comprehensive testing suite

---

## 🛤️ Completed in `v0.1.0` - WebSocket Architecture

> Modular, decoupled system with WebSocket communication:

- WebSocket server implementation ✅
- Event-based communication between components ✅
- Performance tracking throughout the system ✅
- TTS factory with ElevenLabs integration ✅
- Modular architecture for easy extension ✅

## 🛤️ Completed in `v0.0.9` - Adaptive Agent

> Self-tuning, memory-aware assistant:

- Memory-based personality conditioning system ✅
- Feedback pattern analysis and application ✅
- User preference insights based on feedback history ✅
- Mini-command language with system commands ✅
- Feedback storage in long-term memory ✅
- Automatic feedback pattern application ✅

## 🛤️ Completed in `v0.0.8` - Tool Calling

> Enhanced tool calling system:

- **Two-pass tool calling** implementation ✅
- Aggressive JSON cleaning to reduce leakage ✅
- Enhanced error handling and fallbacks ✅
- Improved context handling for the second pass ✅
- Test script for verifying tool calling functionality ✅

## 🛤️ Completed in `v0.0.2` - Memory & Tools

> Basic tool capabilities added:

- Basic **tool calling** implementation ✅
- Structured output from LLM ✅
- Tool router implementation ✅
- Simple tools like `get_time()`, `tell_joke()` ✅
- System prompt refinements for better interactions ✅

---

## 🔮 Toward 1.0 – The Vision

Coda is meant to evolve from a voice loop into a full digital operator:

- 🗃️ Modular "brains" (multi-model support)
- 🔌 Plugin-based tool system (code, media, sensors)
- 🧠 Memory + local knowledge (RAG)
- 📺 Visual UI (optional dashboard)
- 💬 Real personality (fine-tuned voice + prompt tuning)
- 🔐 Fully local fallback runtime, with optional cloud "showoff" mode

Coda is not a chatbot.

Coda is **a system** — and this is just its first breath.

---

## 🚀 GPU Acceleration

Coda Lite supports GPU acceleration for improved performance:

- **ElevenLabs TTS**: Cloud-based API for high-quality speech synthesis
- **Dia TTS**: Uses CUDA for faster speech synthesis (3-5x speedup) when used as a fallback
- **Ollama**: Uses GPU for faster language model inference (4-6x speedup)
- **Whisper**: Uses GPU for faster speech recognition

See [GPU Configuration](docs/gpu_configuration.md) for setup instructions.

---

## 🧠 Memory System

Coda Lite features a sophisticated memory system with both short-term and long-term capabilities:

- **Short-Term Memory**: Maintains the current conversation context
- **Long-Term Memory**: Stores important information across sessions using vector embeddings
- **Memory Encoder**: Intelligently chunks and encodes conversations for efficient storage
- **Semantic Search**: Retrieves relevant memories based on semantic similarity
- **Time-Based Decay**: Applies recency bias to prioritize newer memories
- **Importance Scoring**: Assigns higher importance to facts, preferences, and key information
- **Enhanced Persistence**: Ensures memories are reliably saved across sessions
- **Optimized Retrieval**: Retrieves the most relevant memories with adaptive thresholds
- **Topic Grouping**: Organizes memories by topic for better context integration

The memory system enables Coda to remember user preferences, important facts, and previous conversations, creating a more personalized and contextually aware experience.

See [Memory System Documentation](docs/LONG_TERM_MEMORY.md) and [Memory System Fixes](docs/MEMORY_SYSTEM_FIXES.md) for more details.

---

## 📁 Repository Structure

```bash
coda-lite/
├── main.py               # Entry point (CLI version)
├── main_websocket.py      # Entry point (WebSocket version)
├── version.py            # Version information
├── stt/                  # Speech-to-text (Whisper)
├── tts/                  # Text-to-speech (MeloTTS/CSM-1B, Dia TTS, ElevenLabs)
├── llm/                  # LLM handling and prompt logic
├── memory/               # Memory management (short-term and long-term)
├── personality/          # Personality management
├── intent/               # Intent routing system
├── feedback/             # User feedback system
├── tools/                # Tool calling + router
├── websocket/            # WebSocket server and event handling
├── utils/                # Utility functions and helpers
├── config/               # Prompt and settings files
├── data/                 # Cached audio, logs, temp files
├── gui/                  # Debug GUI for testing
├── dashboard/            # Tauri + React dashboard
├── docs/                 # Project documentation
├── examples/             # Example scripts
├── tests/                # Unit tests
├── CHANGELOG.md          # Detailed version history
```

---

## 🙏 Credits

Built with open-source LLMs, models, and libraries — powered by the work of countless developers and researchers.
This project stands on the shoulders of open communities.

---

## 💡 Why "Coda"?

> C.O.D.A. = **Core Operations & Digital Assistant**
It's a system, not a gimmick — and it plays the final note of how voice assistants *should* work.

---

## 🛠️ License

MIT – free to use, fork, remix, and build on.
We don't gatekeep useful tech.
