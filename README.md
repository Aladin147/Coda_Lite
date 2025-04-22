# Coda Lite – Core Operations & Digital Assistant (v0.0.2)

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

## 🚀 Current Version: `v0.0.2`

> 🔧 **Tool calling added!**

- STT module fully implemented with Whisper (GPU-accelerated)
- LLM integration with Ollama complete
- TTS module implemented with MeloTTS (CSM-1B) with GPU acceleration
- Multiple English voices available (US, British, Australian, Indian)
- Concurrent processing with threading for reduced latency
- Personality module for more engaging interactions
- Short-term memory for conversation context
- Basic tool calling implementation
- Simple tools like `get_time()`, `tell_joke()`, etc.
- Performance improved by ~23% with pipeline optimization

---

## 🔜 Upcoming: `v0.0.3`

> Enhancing the voice loop and adding refinements:

- Wake word detection for hands-free activation
- Token streaming for real-time TTS output
- Voice quality improvements and tuning
- Additional languages support
- Improved error handling and recovery
- Expanded personality with context-aware responses
- Memory summarization for longer conversations

---

## 🛤️ Completed in `v0.0.2`

> Tool capabilities added:

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
├── stt/                  # Speech-to-text (Whisper)
├── tts/                  # Text-to-speech (MeloTTS/CSM-1B)
├── llm/                  # LLM handling and prompt logic
├── memory/               # Memory management
├── personality/          # Personality management
├── tools/                # Tool calling + router
├── config/               # Prompt and settings files
├── data/                 # Cached audio, logs, temp files
├── gui/                  # Debug GUI for testing
├── docs/                 # Project documentation
├── examples/             # Example scripts
├── tests/                # Unit tests
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
