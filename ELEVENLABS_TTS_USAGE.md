# ElevenLabs TTS Integration for Coda

This document provides a quick guide to using the ElevenLabs Text-to-Speech (TTS) integration in Coda.

## Quick Start

1. **Set your API key** in `config/config.yaml` or as an environment variable:
   ```yaml
   tts:
     elevenlabs_api_key: "your-api-key-here"
   ```

2. **Set ElevenLabs as the TTS engine** in `config/config.yaml`:
   ```yaml
   tts:
     engine: "elevenlabs"
   ```

3. **Run the example script** to test the integration:
   ```bash
   python examples/elevenlabs_tts_example.py
   ```

## Available Voices

ElevenLabs offers a variety of voices. Some popular options include:

- Matilda (female): `3sJ9qwog9VNmFa3qD96n` - **Default for Coda**
- Josh (male): `JBFqnCBsd6RMkjVDRZzb`
- Rachel (female): `21m00Tcm4TlvDq8ikWAM`
- Domi (female): `AZnzlk1XvdvUeBnXmlld`
- Bella (female): `EXAVITQu4vr4xnSDxMaL`
- Elli (female): `MF3mGyEYCl7XYWbV9V6O`
- Adam (male): `TxGEqnHWrfWFTfGW9XjX`
- Arnold (male): `VR6AewLTigWG4xSOukaG`
- Sam (male): `pNInz6obpgDQGcFmaJgB`

To list all available voices, run:
```bash
python examples/elevenlabs_tts_example.py
```

## Available Models

- `eleven_multilingual_v2`: Multilingual v2 (best quality, supports 29 languages)
- `eleven_turbo_v2_5`: Turbo v2.5 (fastest, supports 32 languages)
- `eleven_monolingual_v1`: Monolingual v1 (English only)

## Voice Customization

You can customize the voice by adjusting these parameters in `config/config.yaml`:

```yaml
tts:
  elevenlabs_stability: 0.5  # Controls stability (0.0 to 1.0)
  elevenlabs_similarity_boost: 0.75  # Controls similarity to original voice (0.0 to 1.0)
  elevenlabs_style: 0.0  # Controls speaking style (0.0 to 1.0)
  elevenlabs_use_speaker_boost: true  # Whether to use speaker boost
```

## Switching Between TTS Engines

Coda supports multiple TTS engines. To switch between them, change the `engine` parameter in `config/config.yaml`:

```yaml
tts:
  engine: "elevenlabs"  # Options: "csm", "dia", "elevenlabs"
```

## For More Information

See the detailed documentation in `docs/elevenlabs_tts_setup.md`.
