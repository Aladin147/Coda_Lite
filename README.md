# Coda Lite – Core Operations & Digital Assistant (v0.0.9)

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
| 🗣️ TTS        | [MeloTTS (CSM-1B)](https://github.com/myshell-ai/MeloTTS)       | High-quality speech generation       |
| 🔧 Tools      | Python function routing          | Responding to structured LLM output |

---

## 🚀 Current Version: `v0.0.9` - Adaptive Agent

> 🧠 **Self-tuning, memory-aware assistant!**

- STT module fully implemented with Whisper (GPU-accelerated)
- LLM integration with Ollama complete
- TTS module implemented with MeloTTS (CSM-1B) with GPU acceleration
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

## 🔜 Upcoming: `v0.1.0` - Alpha Candidate

> Fully autonomous loop, early demos possible:

- Session summary generation for conversation sessions
- Memory explainability for insights into what Coda remembers
- Task management tools for productivity
- Fix remaining JSON leakage in tool calling responses
- Optimize performance of the two-pass approach
- Implement tool chaining (using results from one tool as input to another)

## 🔜 Future: `v0.2.0` - Beta Candidate

> Feature-complete with stability improvements:

- Wake word detection for hands-free activation
- Token streaming for real-time TTS output
- Voice quality improvements and tuning
- Additional languages support
- Improved error handling and recovery
- Expanded personality with context-aware responses
- Memory summarization for longer conversations

---

## 🛤️ Completed in `v0.0.9` - Adaptive Agent

> Self-tuning, memory-aware assistant:

- Memory-based personality conditioning system ✅
- Feedback pattern analysis and application ✅
- User preference insights based on feedback history ✅
- Mini-command language with system commands ✅
- Feedback storage in long-term memory ✅
- Automatic feedback pattern application ✅

## 🛤️ Completed in `v0.1.0` - Alpha Candidate

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

## 📁 Repository Structure

```bash
coda-lite/
├── main.py               # Entry point
├── version.py            # Version information
├── stt/                  # Speech-to-text (Whisper)
├── tts/                  # Text-to-speech (MeloTTS/CSM-1B)
├── llm/                  # LLM handling and prompt logic
├── memory/               # Memory management
├── personality/          # Personality management
├── intent/               # Intent routing system
├── feedback/             # User feedback system
├── tools/                # Tool calling + router
├── config/               # Prompt and settings files
├── data/                 # Cached audio, logs, temp files
├── gui/                  # Debug GUI for testing
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
