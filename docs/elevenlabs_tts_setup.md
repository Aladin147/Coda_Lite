# ElevenLabs TTS Integration for Coda

This document describes how to set up and use the ElevenLabs Text-to-Speech (TTS) integration for Coda.

## Overview

ElevenLabs provides high-quality, natural-sounding text-to-speech capabilities with a wide range of voices and languages. This integration allows Coda to use ElevenLabs' API for speech synthesis, providing a significant improvement in voice quality compared to open-source alternatives.

## Prerequisites

- An ElevenLabs account (sign up at [elevenlabs.io](https://elevenlabs.io))
- An ElevenLabs API key (available in your ElevenLabs account settings)
- Python 3.8 or higher
- The `elevenlabs` Python package (installed automatically with Coda)

## Configuration

### API Key

You can provide your ElevenLabs API key in one of two ways:

1. **In the configuration file**: Add your API key to the `elevenlabs_api_key` field in the `tts` section of `config/config.yaml`.
2. **As an environment variable**: Set the `ELEVENLABS_API_KEY` environment variable.

### Voice Selection

ElevenLabs offers a variety of voices. You can specify which voice to use by setting the `elevenlabs_voice_id` in the configuration file. Some popular voices include:

- `JBFqnCBsd6RMkjVDRZzb` - Josh (male)
- `21m00Tcm4TlvDq8ikWAM` - Rachel (female)
- `AZnzlk1XvdvUeBnXmlld` - Domi (female)
- `EXAVITQu4vr4xnSDxMaL` - Bella (female)
- `MF3mGyEYCl7XYWbV9V6O` - Elli (female)
- `TxGEqnHWrfWFTfGW9XjX` - Adam (male)
- `VR6AewLTigWG4xSOukaG` - Arnold (male)
- `pNInz6obpgDQGcFmaJgB` - Sam (male)

You can also list all available voices by running the example script with your API key.

### Model Selection

ElevenLabs offers different models for speech synthesis. You can specify which model to use by setting the `elevenlabs_model_id` in the configuration file:

- `eleven_multilingual_v2` - Multilingual v2 (best quality, supports 29 languages)
- `eleven_turbo_v2_5` - Turbo v2.5 (fastest, supports 32 languages)
- `eleven_monolingual_v1` - Monolingual v1 (English only)

### Voice Customization

You can customize the voice characteristics by adjusting the following parameters in the configuration file:

- `elevenlabs_stability` (0.0 to 1.0): Controls the stability of the voice. Higher values result in more consistent and stable speech.
- `elevenlabs_similarity_boost` (0.0 to 1.0): Controls how closely the output matches the original voice. Higher values result in speech that sounds more like the original voice.
- `elevenlabs_style` (0.0 to 1.0): Controls the speaking style. Higher values result in more expressive speech.
- `elevenlabs_use_speaker_boost` (true/false): Whether to use speaker boost, which enhances the clarity and presence of the voice.

## Usage

### Basic Usage

To use ElevenLabs TTS in your Coda application, set the `engine` parameter in the `tts` section of `config/config.yaml` to `"elevenlabs"`:

```yaml
tts:
  engine: "elevenlabs"
  # Other TTS settings...
```

### Example Script

You can test the ElevenLabs TTS integration using the provided example script:

```bash
python examples/elevenlabs_tts_example.py --text "Hello, this is a test of ElevenLabs TTS integration."
```

This will generate a speech file using the configured voice and save it to `elevenlabs_output.wav`.

### Additional Options

The example script supports the following command-line options:

- `--text`: The text to synthesize (default: a greeting message)
- `--output`: The output file path (default: `elevenlabs_output.wav`)
- `--config`: The path to the configuration file (default: `config/config.yaml`)
- `--voice`: The voice ID to use (overrides the configuration)
- `--model`: The model ID to use (overrides the configuration)

## Switching Between TTS Engines

Coda supports multiple TTS engines, and you can switch between them by changing the `engine` parameter in the configuration file:

- `"csm"`: Use CSM-1B (MeloTTS) for offline TTS
- `"dia"`: Use Dia TTS for high-quality offline TTS
- `"elevenlabs"`: Use ElevenLabs for premium online TTS

## Troubleshooting

### API Key Issues

If you encounter authentication errors, make sure your API key is correct and has not expired. You can verify your API key in your ElevenLabs account settings.

### Rate Limiting

ElevenLabs has rate limits based on your subscription plan. If you encounter rate limiting errors, you may need to upgrade your plan or reduce your usage.

### Voice Not Found

If you specify a voice ID that doesn't exist or that you don't have access to, you'll receive an error. Use the example script to list all available voices and choose one that's accessible to you.

## Resources

- [ElevenLabs Documentation](https://elevenlabs.io/docs)
- [ElevenLabs API Reference](https://elevenlabs.io/docs/api-reference)
- [ElevenLabs Python SDK](https://github.com/elevenlabs/elevenlabs-python)
