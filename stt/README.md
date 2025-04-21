# Speech-to-Text (STT) Module for Coda Lite

This module provides speech recognition capabilities for Coda Lite using the faster-whisper library.

## Whisper STT

The primary STT engine used in Coda Lite is Whisper, a state-of-the-art speech recognition model developed by OpenAI, implemented using the faster-whisper library for improved performance.

### Features

- High-accuracy speech recognition
- Multiple model sizes (tiny, base, small, medium, large)
- GPU acceleration for faster transcription
- Voice Activity Detection (VAD) for better speech detection
- Continuous listening mode for natural conversation
- Support for multiple languages

### Configuration

The STT engine can be configured in `config/config.yaml`:

```yaml
# Speech-to-Text settings
stt:
  model_size: "base"  # Options: tiny, base, small, medium, large
  language: "en"
  device: "cuda"  # Options: cpu, cuda - Using GPU for faster transcription
  compute_type: "float16"  # Options: float32, float16, int8 - float16 is faster on GPU
```

### Dependencies

Whisper STT requires the following dependencies:

- faster-whisper
- PyTorch (with CUDA support for GPU acceleration)
- pyaudio (for audio recording)
- numpy

### Usage

```python
from stt import WhisperSTT

# Create an STT instance
stt = WhisperSTT(
    model_size="base",
    device="cuda",
    compute_type="float16",
    language="en",
    vad_filter=True
)

# Transcribe an audio file
transcription = stt.transcribe_audio("audio.wav")
print(f"Transcription: {transcription}")

# Listen for a specific duration
transcription = stt.listen(duration=5)
print(f"Transcription: {transcription}")

# Continuous listening with callback
def handle_transcription(text):
    print(f"User said: {text}")
    # Process the transcription...

# Start continuous listening
stt.listen_continuous(
    callback=handle_transcription,
    stop_callback=lambda: False,  # Return True to stop listening
    silence_threshold=0.1,
    silence_duration=1.0
)

# Clean up resources when done
stt.close()
```

## Implementation Details

The STT module is implemented as a single class:

- `WhisperSTT`: Implementation of the Whisper STT engine using faster-whisper

The module provides methods for transcribing audio files, listening for a specific duration, and continuous listening with automatic speech detection.
