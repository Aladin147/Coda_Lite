# Voice Loop Implementation

This document describes the implementation of the voice loop in Coda Lite, which enables natural voice interaction between the user and the assistant.

## Overview

The voice loop consists of three main components:

1. **Speech-to-Text (STT)**: Converts user's speech to text
2. **Language Model (LLM)**: Processes the text and generates a response
3. **Text-to-Speech (TTS)**: Converts the response text to speech

These components work together to create a seamless voice interaction experience.

## Implementation

### Speech-to-Text (STT)

The STT component is implemented using the faster-whisper library, which provides a high-performance implementation of OpenAI's Whisper model.

- **Model**: Base Whisper model (can be configured to use tiny, base, small, medium, or large)
- **Device**: CUDA (GPU) for faster transcription
- **Compute Type**: float16 for optimal performance on GPU
- **Voice Activity Detection (VAD)**: Enabled to filter out silence and background noise

The STT component provides three main methods:
- `transcribe_audio()`: Transcribes an audio file
- `listen()`: Records audio for a specific duration and transcribes it
- `listen_continuous()`: Continuously listens for speech, automatically detecting when the user starts and stops speaking

### Language Model (LLM)

The LLM component is implemented using Ollama, which provides a local API for running large language models.

- **Model**: LLaMA 3 (default)
- **API**: Ollama's HTTP API
- **System Prompt**: Configurable via `config/prompts/system.txt`

The LLM component processes the user's input and generates a response based on the conversation history.

### Text-to-Speech (TTS)

The TTS component is implemented using MeloTTS (CSM-1B), which provides high-quality, multilingual speech synthesis.

- **Model**: CSM-1B
- **Device**: CUDA (GPU) for faster synthesis
- **Language**: English (configurable to use other supported languages)
- **Voice**: EN-US (configurable to use other available voices)

The TTS component provides two main methods:
- `synthesize()`: Synthesizes speech to a file
- `speak()`: Synthesizes speech and plays it directly

## Voice Loop Flow

1. The application initializes the STT, LLM, and TTS components
2. The TTS component speaks a welcome message
3. The STT component starts continuous listening
4. When the user speaks, the STT component transcribes the speech
5. The transcribed text is sent to the LLM component
6. The LLM component generates a response
7. The response is sent to the TTS component
8. The TTS component synthesizes and plays the response
9. The loop continues from step 4

## Performance Optimization

To achieve low-latency voice interaction, several performance optimizations have been implemented:

- **GPU Acceleration**: Both STT and TTS components use CUDA for faster processing
- **Model Size Selection**: The base Whisper model provides a good balance between accuracy and speed
- **Compute Type Optimization**: Using float16 for faster computation on GPU
- **Voice Activity Detection**: Filtering out silence and background noise to improve transcription accuracy
- **Conversation History Management**: Limiting the conversation history to prevent memory issues

## Configuration

The voice loop can be configured via the `config/config.yaml` file, which allows customization of various parameters for each component.

## Future Improvements

- **Wake Word Detection**: Add a wake word detection system to activate the assistant only when needed
- **Voice Quality Improvements**: Fine-tune the TTS model for better voice quality
- **Latency Optimization**: Further reduce the latency for more natural conversation
- **Multi-language Support**: Extend the voice loop to support multiple languages
- **Voice Customization**: Allow users to customize the assistant's voice
