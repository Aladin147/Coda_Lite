# Coda Lite – Core Operations & Digital Assistant (v0.0.1)

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
| 🗣️ TTS        | [Coqui TTS](https://github.com/coqui-ai/TTS) (CSM-1B planned)       | Local speech generation       |
| 🔧 Tools      | Python function routing          | Responding to structured LLM output |

---

## 🚀 Current Version: `v0.0.1`

> 🔄 **Voice loop in development**
- STT module fully implemented with Whisper
- LLM integration with Ollama complete
- TTS module implemented with Coqui (CSM-1B planned)
- Debug GUI for testing the conversation loop
- Working on optimizing performance and reliability

---

## 🔜 Upcoming: `v0.0.1a`
> Completing the voice loop and adding enhancements:
- CSM-1B integration for improved TTS quality
- Full conversation loop with voice input
- Performance optimization for sub-5s latency
- Basic error handling and recovery

Followed by tool calling in v0.0.2.

---

## 🛤️ Planned for `v0.0.2`
> Adding tool capabilities and refinements:
- Basic **tool calling** implementation
- Structured output from LLM
- Tool router implementation
- Simple tools like `get_time()`, `tell_joke()`, etc.
- System prompt refinements for better interactions

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
├── tts/                  # Text-to-speech (currently Coqui, CSM-1B planned)
├── llm/                  # LLM handling and prompt logic
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
