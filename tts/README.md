# Text-to-Speech (TTS) Module for Coda Lite

This module provides a common interface for different TTS implementations.

Coda Lite currently supports the following TTS engines:

1. CSM-1B (MeloTTS) - A high-quality, multilingual text-to-speech model
2. Dia TTS - An ultra-realistic dialogue synthesis model

## CSM-1B (MeloTTS)

The primary TTS engine used in Coda Lite is CSM-1B (MeloTTS), a high-quality, multilingual text-to-speech model developed by MyShell.ai.

### Features

- High-quality, natural-sounding speech synthesis
- Multilingual support (EN, ES, FR, ZH, JP, KR)
- Multiple voices for English (EN-US, EN-BR, EN_INDIA, EN-AU, EN-Default)
- GPU acceleration for faster inference

### Configuration

The TTS engine can be configured in `config/config.yaml`:

```yaml
# Text-to-Speech settings
tts:
  engine: "csm"  # Options: csm, dia
  language: "EN"  # Language code for CSM-1B (EN, ES, FR, ZH, JP, KR)
  voice: "EN-Default"  # Available voices for English: EN-US, EN-BR, EN_INDIA, EN-AU, EN-Default
  speed: 1.0
  device: "cuda"  # Options: cpu, cuda - Using GPU for better performance

  # Dia TTS specific settings
  audio_prompt_path: null  # Path to audio file for voice cloning with Dia TTS
```

### Dependencies

CSM-1B (MeloTTS) requires the following dependencies:

- PyTorch
- torchaudio
- simpleaudio (for audio playback)
- MeloTTS (included in the project as a local module)
- Various NLP libraries for text processing (nltk, g2p_en, etc.)

### Usage

```python
from tts import create_tts

# Create a TTS instance
tts = create_tts(engine="csm", language="EN", device="cuda")

# Synthesize speech to a file
output_path = tts.synthesize("Hello, I am Coda.", output_path="output.wav")

# Speak directly
tts.speak("Hello, I am Coda.")

# Get available voices
voices = tts.get_available_voices()
print(f"Available voices: {voices}")

# Get available languages
languages = tts.get_available_languages()
print(f"Available languages: {languages}")
```

## Dia TTS

Dia TTS is a 1.6B parameter text-to-speech model created by Nari Labs, capable of generating ultra-realistic dialogue.

### Features

- Direct generation of highly realistic dialogue from a transcript
- Voice cloning through audio prompts
- Support for non-verbal communications (laughter, coughing, etc.)
- Speaker tags for multi-speaker dialogues ([S1], [S2])

### Configuration

Dia TTS can be configured in `config/config.yaml`:

```yaml
# Text-to-Speech settings
tts:
  engine: "dia"  # Use Dia TTS engine
  device: "cuda"  # Options: cpu, cuda - Using GPU for better performance
  audio_prompt_path: "path/to/voice/sample.mp3"  # Optional: Path to audio file for voice cloning
```

### Dependencies

Dia TTS requires the following dependencies:

- PyTorch >= 2.0.0
- soundfile
- Dia TTS package (installed from GitHub)

You can install the dependencies using:

```bash
pip install -r requirements-dia.txt
```

### Usage

```python
from tts import create_tts
import soundfile as sf

# Create a Dia TTS instance
tts = create_tts(engine="dia", device="cuda")

# Synthesize a simple message
tts.speak("Hello, I am Coda.")

# Synthesize dialogue
dialogue = """
[S1] Hello, how are you today?
[S2] I'm doing well, thank you for asking.
[S1] That's great to hear! (laughs)
"""

# Save to file
output_path = tts.synthesize(dialogue, output_path="dialogue.wav")

# Voice cloning example
tts_with_voice = create_tts(
    engine="dia",
    device="cuda",
    audio_prompt_path="path/to/voice/sample.mp3"
)
tts_with_voice.speak("This will sound like the voice in the audio prompt.")
```

## Implementation Details

The TTS module is implemented as a class hierarchy:

- `BaseTTS`: Abstract base class defining the common interface for all TTS implementations
- `CSMTTS`: Implementation of the CSM-1B (MeloTTS) engine
- `DiaTTS`: Implementation of the Dia TTS engine

The `create_tts` factory function is used to create TTS instances based on the specified engine.
