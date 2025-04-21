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
| 🗣️ TTS        | [CSM-1B](https://huggingface.co/myshell-ai/CSM)       | Local speech generation       |
| 🔧 Tools      | Python function routing          | Responding to structured LLM output |

---

## 🚀 Current Version: `v0.0.1`

> 🔁 **Voice loop only**
- Talk to Coda, get a vocal reply
- Tuned for minimal latency and natural tone
- Ideal for stress-testing the loop and UX

---

## 🔜 Upcoming: `v0.0.1a`
> Adds basic **tool calling**, such as:
- `get_time()`
- `tell_joke()`
- `get_gear("Canon R6")`

Coda will begin executing structured tasks and narrating results.

---

## 🛤️ Planned for `v0.0.2`
> 🎙️ **Fine-tuned voice model** for unique personality  
> 🧠 **System prompt refinements** for tone, behavior, and emotional tone

---

## 🔮 Toward 1.0 – The Vision

Coda is meant to evolve from a voice loop into a full digital operator:

- 🗃️ Modular “brains” (multi-model support)
- 🔌 Plugin-based tool system (code, media, sensors)
- 🧠 Memory + local knowledge (RAG)
- 📺 Visual UI (optional dashboard)
- 💬 Real personality (fine-tuned voice + prompt tuning)
- 🔐 Fully local fallback runtime, with optional cloud “showoff” mode

Coda is not a chatbot.

Coda is **a system** — and this is just its first breath.

---

## 📁 Repository Structure

```bash
coda-lite/
├── main.py               # Entry point
├── stt/                  # Speech-to-text (Whisper)
├── tts/                  # Text-to-speech (CSM-1B)
├── llm/                  # LLM handling and prompt logic
├── tools/                # Tool calling + router
├── config/               # Prompt and settings files
├── data/                 # Cached audio, logs, temp files
```

---

## 🙏 Credits

Built with open-source LLMs, models, and libraries — powered by the work of countless developers and researchers.  
This project stands on the shoulders of open communities.

---

## 💡 Why “Coda”?

> C.O.D.A. = **Core Operations & Digital Assistant**  
It's a system, not a gimmick — and it plays the final note of how voice assistants *should* work.

---

## 🛠️ License

MIT – free to use, fork, remix, and build on.  
We don’t gatekeep useful tech.
