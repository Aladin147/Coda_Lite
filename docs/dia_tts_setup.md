# Dia TTS Setup Guide

This guide provides instructions for setting up and using Dia TTS in Coda Lite.

## Overview

Dia is a 1.6B parameter text-to-speech model created by Nari Labs. It directly generates highly realistic dialogue from a transcript and can be conditioned on audio for voice cloning. The model can also produce nonverbal communications like laughter, coughing, etc.

Key features:
- Ultra-realistic dialogue generation
- Voice cloning through audio prompts
- Support for non-verbal elements
- GPU acceleration for faster inference

## Installation

### Prerequisites

- NVIDIA GPU with CUDA support (recommended)
- Python 3.10+ (recommended)
- PyTorch 2.6.0+ with CUDA support

### Installation Steps

1. **Install Dia TTS dependencies**:

   ```bash
   pip install -r requirements-dia.txt
   ```

2. **Verify installation**:

   ```bash
   python test_dia_gpu.py
   ```

   This will test if Dia TTS is properly installed and can use your GPU.

## Usage

### Basic Usage

```python
from tts import create_tts

# Create a Dia TTS instance
tts = create_tts(engine="dia", device="cuda")

# Synthesize speech
tts.speak("Hello, I am Coda Lite, your local voice assistant.")
```

### Dialogue Generation

Dia TTS excels at generating natural-sounding dialogue. Use `[S1]` and `[S2]` tags to indicate different speakers:

```python
dialogue = """
[S1] Hello, how are you today?
[S2] I'm doing well, thank you for asking. How about you?
[S1] I'm great! I'm excited to be using Dia TTS.
[S2] That's wonderful to hear. Dia TTS is designed to create natural-sounding dialogue.
[S1] I can definitely tell. The voices sound very realistic. (laughs)
"""

tts.speak(dialogue)
```

### Voice Cloning

You can clone a voice by providing an audio prompt:

```python
tts = create_tts(
    engine="dia",
    device="cuda",
    audio_prompt_path="path/to/voice/sample.mp3"
)

tts.speak("This will sound like the voice in the audio prompt.")
```

### Advanced Parameters

Dia TTS supports several parameters to control the generation:

```python
tts = create_tts(
    engine="dia",
    device="cuda",
    temperature=1.3,        # Controls randomness (higher = more random)
    top_p=0.95,             # Top-p sampling parameter
    cfg_scale=3.0,          # Classifier-free guidance scale
    use_torch_compile=True  # Use torch.compile for faster inference
)
```

## Configuration

You can configure Dia TTS in the `config/config.yaml` file:

```yaml
tts:
  engine: "dia"
  device: "cuda"
  
  # Dia TTS specific settings
  audio_prompt_path: null
  temperature: 1.3
  top_p: 0.95
  cfg_scale: 3.0
  use_torch_compile: true
```

## Troubleshooting

### GPU Issues

If you encounter GPU-related issues:

1. **Verify CUDA is available**:
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

2. **Check GPU memory usage**:
   ```python
   import torch
   print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
   print(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")
   ```

3. **Run the test script**:
   ```bash
   python test_dia_gpu.py
   ```

### Common Issues

- **ImportError: No module named 'dia'**: Make sure you've installed the requirements with `pip install -r requirements-dia.txt`.
- **CUDA out of memory**: Dia requires around 10GB of VRAM. Try closing other GPU-intensive applications.
- **Slow generation on CPU**: Dia is designed to run on GPU. CPU inference will be significantly slower.

## Examples

See `examples/dia_tts_example.py` for more usage examples.

## Performance Considerations

- The first generation may be slower due to model compilation and optimization.
- Using `torch.compile` can significantly improve performance on supported GPUs.
- For best performance, ensure no other GPU-intensive tasks are running simultaneously.
