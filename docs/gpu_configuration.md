# GPU Configuration for Coda Lite

This document explains how to configure Coda Lite to use GPU acceleration for both the Dia TTS speech synthesis and Ollama language model inference.

## Requirements

- NVIDIA GPU with CUDA support
- NVIDIA drivers installed
- PyTorch with CUDA support
- Ollama with GPU support enabled

## PyTorch CUDA Configuration

Coda Lite uses PyTorch for Dia TTS speech synthesis. To enable GPU acceleration, PyTorch must be installed with CUDA support:

```bash
# Uninstall existing CPU-only PyTorch
pip uninstall -y torch torchaudio

# Install PyTorch with CUDA support
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

You can verify that PyTorch is using CUDA with the following Python code:

```python
import torch
print(f'PyTorch version: {torch.__version__}')
print(f'CUDA available: {torch.cuda.is_available()}')
print(f'CUDA version: {torch.version.cuda if hasattr(torch.version, "cuda") else "None"}')
print(f'GPU device count: {torch.cuda.device_count()}')
print(f'GPU device name: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else "N/A"}')
```

## Ollama GPU Configuration

Ollama can use GPU acceleration for language model inference. To enable GPU support in Ollama:

1. Create a configuration file in the user's home directory:

```bash
# For Windows (PowerShell)
New-Item -Path $HOME\.ollama -ItemType Directory -Force
Set-Content -Path $HOME\.ollama\config -Value '{"gpu": {"enable": true}}'

# For Linux/macOS
mkdir -p ~/.ollama
echo '{"gpu": {"enable": true}}' > ~/.ollama/config
```

2. Restart Ollama:

```bash
# For Windows (PowerShell)
Stop-Process -Name ollama -Force
Start-Process -FilePath 'C:\Users\<username>\AppData\Local\Programs\Ollama\ollama.exe' -ArgumentList 'serve'

# For Linux/macOS
killall ollama
ollama serve
```

## Verifying GPU Usage

You can verify that both Dia TTS and Ollama are using the GPU with the following command:

```bash
# For Windows/Linux with NVIDIA GPU
nvidia-smi

# Look for Python (Dia TTS) and Ollama processes in the output
```

## Configuration in Coda Lite

Coda Lite is configured to use GPU acceleration by default. The configuration is in `config/config.yaml`:

```yaml
tts:
  device: "cuda"  # Options: cpu, cuda - Using GPU for better performance
```

If CUDA is not available, Coda Lite will automatically fall back to CPU.

## Performance Considerations

- GPU acceleration significantly improves performance for both speech synthesis and language model inference
- Dia TTS speech synthesis is approximately 3-5x faster on GPU compared to CPU
- Ollama language model inference is approximately 4-6x faster on GPU compared to CPU
- Both Dia TTS and Ollama can use the same GPU simultaneously, but they will share GPU memory
