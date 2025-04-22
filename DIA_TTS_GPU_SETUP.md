# Dia TTS GPU Setup Guide

This guide provides instructions for setting up Dia TTS with proper GPU support in Coda Lite.

## Prerequisites

- NVIDIA GPU with CUDA support
- NVIDIA drivers installed
- Python 3.10.x (recommended)

## Installation Steps

1. **Create a virtual environment with Python 3.10**:
   ```bash
   python3.10 -m venv venv310
   source venv310/Scripts/activate  # Windows
   # OR
   source venv310/bin/activate      # Linux/Mac
   ```

2. **Install PyTorch with CUDA support**:
   ```bash
   # For CUDA 12.x
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
   
   # For CUDA 11.x
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
   ```

3. **Verify CUDA is available**:
   ```python
   import torch
   print(f"CUDA available: {torch.cuda.is_available()}")
   print(f"CUDA version: {torch.version.cuda}")
   print(f"GPU device: {torch.cuda.get_device_name(0)}")
   ```

4. **Install Dia TTS**:
   ```bash
   pip install git+https://github.com/nari-labs/dia.git
   ```

5. **Install other dependencies**:
   ```bash
   pip install soundfile simpleaudio
   ```

## Implementation Details

The Dia TTS implementation in `tts/dia_tts.py` has been updated to properly use GPU acceleration. Key changes include:

1. **Explicit device placement**: All model components are explicitly moved to the GPU after initialization.
2. **Component verification**: Before generation, we verify that all components are on the GPU.
3. **Error handling**: Graceful fallback to CPU if GPU is not available.

## Troubleshooting

If you encounter issues with GPU acceleration:

1. **Verify CUDA is available**:
   ```python
   import torch
   print(torch.cuda.is_available())
   ```

2. **Check PyTorch installation**:
   ```bash
   pip list | grep torch
   ```
   The output should include `+cu121` or similar CUDA version indicator.

3. **Check GPU memory usage**:
   ```python
   import torch
   print(f"GPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
   print(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")
   ```

4. **Run the test script**:
   ```bash
   python test_dia_gpu_direct.py
   ```

## Performance Considerations

- Dia TTS performs significantly better on GPU compared to CPU.
- The first generation may be slower due to compilation and optimization.
- For best performance, ensure no other GPU-intensive tasks are running simultaneously.

## Implementation Notes

The key parts of the implementation that ensure GPU usage are:

1. **Model initialization with device parameter**:
   ```python
   torch_device = torch.device(device)
   self.model = Dia.from_pretrained("nari-labs/Dia-1.6B", device=torch_device)
   ```

2. **Explicit component movement to GPU**:
   ```python
   # Move main model to GPU
   if hasattr(self.model, 'model'):
       self.model.model = self.model.model.to(torch_device)
   
   # Move DAC model (vocoder) to GPU
   if hasattr(self.model, 'dac_model') and self.model.dac_model is not None:
       self.model.dac_model = self.model.dac_model.to(torch_device)
   
   # Move encoder to GPU
   if hasattr(self.model.model, 'encoder'):
       self.model.model.encoder = self.model.model.encoder.to(torch_device)
   
   # Move decoder to GPU
   if hasattr(self.model.model, 'decoder'):
       self.model.model.decoder = self.model.model.decoder.to(torch_device)
   ```

3. **Verification before generation**:
   ```python
   # Double-check components before generation
   if hasattr(self.model, 'model') and self.model.model.device.type != "cuda":
       self.model.model = self.model.model.to("cuda")
   ```
