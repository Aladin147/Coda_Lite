import time
import torch
import soundfile as sf
import os
from dia.model import Dia

# Enable detailed GPU memory logging
os.environ['CUDA_LAUNCH_BLOCKING'] = '1'

# Check PyTorch and CUDA
print(f"PyTorch version: {torch.__version__}")
print(f"CUDA available: {torch.cuda.is_available()}")
print(f"CUDA version: {torch.version.cuda if hasattr(torch.version, 'cuda') else 'None'}")
print(f"GPU device: {torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'N/A'}")

# Initialize Dia TTS model with explicit device setting
print("\nInitializing Dia TTS model...")
start_time = time.time()
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model = Dia.from_pretrained("nari-labs/Dia-1.6B", device=device)
print(f"Model initialization time: {time.time() - start_time:.2f} seconds")

# Force ALL model components to GPU if available
if torch.cuda.is_available():
    print("\nMoving ALL model components to GPU...")

    # Move the main model to GPU
    if hasattr(model, 'model'):
        model.model = model.model.to('cuda')
        print("- Main model moved to GPU")

    # Move the DAC model (vocoder) to GPU
    if hasattr(model, 'dac_model') and model.dac_model is not None:
        model.dac_model = model.dac_model.to('cuda')
        print("- DAC model (vocoder) moved to GPU")

    # Move encoder to GPU if it exists
    if hasattr(model.model, 'encoder'):
        model.model.encoder = model.model.encoder.to('cuda')
        print("- Encoder moved to GPU")

    # Move decoder to GPU if it exists
    if hasattr(model.model, 'decoder'):
        model.model.decoder = model.model.decoder.to('cuda')
        print("- Decoder moved to GPU")

    # Print GPU memory usage before generation
    print(f"\nGPU memory allocated: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
    print(f"GPU memory reserved: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

# Try to enable torch.compile if available
try:
    if hasattr(torch, 'compile') and torch.cuda.is_available():
        print("\nEnabling torch.compile for better performance...")
        if hasattr(model.model, 'encoder'):
            model.model.encoder = torch.compile(model.model.encoder)
            print("- Encoder compiled")
        if hasattr(model.model, 'decoder'):
            model.model.decoder = torch.compile(model.model.decoder)
            print("- Decoder compiled")
        print("Torch compile enabled")
except Exception as e:
    print(f"Could not enable torch.compile: {e}")

# Generate speech
text = "[S1] This is a test of Dia TTS running on GPU. [S2] Let's see if it's faster now."
print(f"\nGenerating speech for: {text}")

# Time the text-to-mel generation
print("\nGenerating speech...")
start_time = time.time()

# Enable use_torch_compile for better performance
audio = model.generate(
    text,
    use_torch_compile=True,  # Enable torch.compile
    temperature=1.0,         # Default temperature
    top_p=0.95,              # Default top_p
    cfg_scale=3.0            # Default cfg_scale
)

generation_time = time.time() - start_time
print(f"Speech generation time: {generation_time:.2f} seconds")

# Print GPU memory usage after generation
if torch.cuda.is_available():
    print(f"GPU memory allocated after generation: {torch.cuda.memory_allocated() / 1024**2:.2f} MB")
    print(f"GPU memory reserved after generation: {torch.cuda.memory_reserved() / 1024**2:.2f} MB")

# Save the audio
sf.write("test_output.wav", audio, 44100)
print("Audio saved to test_output.wav")
