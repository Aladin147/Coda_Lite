# Coda Lite — GUI Test Harness

A lightweight debug GUI that wraps the voice loop (STT → LLM → TTS), giving you visual control over input/output, latency, and module behavior.

## Overview

This GUI test harness is designed to test Coda's core logic with:
- Manual text input
- Displayed LLM responses
- Optional playback
- Internal logs and performance metrics

## How to Run It

1. Install the required dependencies:
   ```
   pip install PySimpleGUI
   ```

2. Run the GUI script:
   ```
   python gui/coda_debug_gui.py
   ```

## Features

| Element | Function |
|---------|----------|
| 📝 Input Box | Type or paste simulated transcription |
| 🤖 Response Box | Shows LLM output from OllamaLLM.generate() |
| 🔊 Speak Button | Sends response to TTS.synthesize() |
| 📄 Log Output | Shows time, latency, debug info |
| ✅ Toggle Options | Auto-speak / Show Timing / Save History |

## What It Connects To

- `llm/ollama_llm.py`: for LLM generation
- `tts/speak.py`: for speech output
- `config/config_loader.py`: for configuration

## Why It Matters

- Debug voice loop without using your mic
- Visual latency/performance profiling
- Reuse components in future frontends (CLI, kiosk, mobile, etc.)

## Usage Tips

1. **Temperature and Max Tokens**: Adjust these sliders to control the LLM's behavior.
2. **Auto-speak**: Toggle this to automatically speak responses when generated.
3. **Show Timing**: Toggle this to display performance metrics in the log.
4. **Save Conversation**: Save the current conversation history to a JSON file.
5. **Clear Conversation**: Reset the conversation history while keeping the system prompt.

## Troubleshooting

- Make sure Ollama is running with your desired model pulled
- Check the debug log for error messages
- Ensure all dependencies are installed
