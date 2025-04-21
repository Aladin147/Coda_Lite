#!/usr/bin/env python3
"""
Test script for WhisperSTT with GPU acceleration.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("stt_gpu_test")

from stt import WhisperSTT
import torch

def main():
    """Test WhisperSTT with GPU acceleration."""
    try:
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        if device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
        
        # Initialize the WhisperSTT module
        print("\nInitializing WhisperSTT...")
        stt = WhisperSTT(
            model_size="base",  # Use base model for better accuracy
            device=device,
            compute_type="float16" if device == "cuda" else "float32",
            language="en",
            vad_filter=True
        )
        
        print("\nListening for 5 seconds...")
        print("Please speak now...")
        
        # Measure time for transcription
        start_time = time.time()
        
        # Listen and transcribe
        transcription = stt.listen(duration=5)
        
        end_time = time.time()
        
        print(f"\nTranscription completed in {end_time - start_time:.2f} seconds")
        print(f"Transcription: {transcription}")
        
        # Clean up
        stt.close()
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
