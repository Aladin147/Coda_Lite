# Dia TTS Usage Guide

This guide provides instructions for using Dia TTS in Coda Lite.

## Overview

Dia is a 1.6B parameter text-to-speech model created by Nari Labs. It directly generates highly realistic dialogue from a transcript and can be conditioned on audio for voice cloning. The model can also produce nonverbal communications like laughter, coughing, etc.

## Key Features

- **Ultra-realistic dialogue generation**: Dia TTS produces natural-sounding dialogue with appropriate prosody and timing.
- **Voice cloning**: Use an audio prompt to clone a voice for personalized speech synthesis.
- **Speaker tags**: Use `[S1]` and `[S2]` tags to differentiate speakers in dialogue.
- **Non-verbal elements**: Dia can generate non-verbal sounds like laughter, sighs, etc.
- **GPU acceleration**: Optimized for GPU inference with torch.compile support.

## Basic Usage

```python
from tts import create_tts

# Create a Dia TTS instance
tts = create_tts(
    engine="dia",
    device="cuda",  # Use "cpu" if no GPU is available
    temperature=1.3,
    top_p=0.95,
    cfg_scale=3.0,
    use_torch_compile=True
)

# Synthesize speech to a file
output_path = tts.synthesize(
    "[S1] Hello, I am using Dia TTS. [S2] It sounds very natural!",
    "output.wav"
)

# Play speech directly
tts.speak("[S1] This will be played immediately.")
```

## Speaker Tags

Dia TTS uses speaker tags to differentiate between speakers in dialogue:

```python
dialogue = """
[S1] Hello, how are you today?
[S2] I'm doing well, thank you for asking. How about you?
[S1] I'm great! I'm excited to be using Dia TTS.
[S2] That's wonderful to hear. Dia TTS is designed to create natural-sounding dialogue.
[S1] I can definitely tell. The voices sound very realistic. (laughs)
"""

tts.synthesize(dialogue, "dialogue.wav")
```

## Voice Cloning

You can clone a voice by providing an audio prompt:

```python
tts = create_tts(
    engine="dia",
    device="cuda",
    audio_prompt_path="path/to/voice/sample.mp3"
)

tts.synthesize("[S1] This will sound like the voice in the audio prompt.", "cloned_voice.wav")
```

## Generation Parameters

Dia TTS supports several parameters to control the generation:

- **temperature** (default: 1.3): Controls randomness (higher = more random, lower = more deterministic)
- **top_p** (default: 0.95): Top-p sampling parameter (0-1)
- **cfg_scale** (default: 3.0): Classifier-free guidance scale (higher = more adherence to the prompt)
- **use_torch_compile** (default: True): Use torch.compile for faster inference

Example:

```python
tts = create_tts(
    engine="dia",
    device="cuda",
    temperature=1.5,  # More random/creative
    top_p=0.9,
    cfg_scale=2.5,
    use_torch_compile=True
)
```

## GPU Optimization

Dia TTS is optimized for GPU inference. For best performance:

1. Use a GPU with at least 10GB of VRAM
2. Set `device="cuda"` when creating the TTS instance
3. Enable `use_torch_compile=True` for faster inference
4. Close other GPU-intensive applications

## Troubleshooting

### Common Issues

- **ImportError: No module named 'dia'**: Make sure you've installed the requirements with `pip install -r requirements-dia.txt`.
- **CUDA out of memory**: Dia requires around 10GB of VRAM. Try closing other GPU-intensive applications.
- **Slow generation on CPU**: Dia is designed to run on GPU. CPU inference will be significantly slower.
- **Error with torch.compile**: If you encounter errors with torch.compile, set `use_torch_compile=False`.

### Testing

You can test your Dia TTS installation with the provided test scripts:

```bash
# Test GPU performance
python test_dia_gpu.py

# Simple test
python test_dia_simple.py
```

## Examples

See `examples/dia_tts_example.py` for more usage examples.
