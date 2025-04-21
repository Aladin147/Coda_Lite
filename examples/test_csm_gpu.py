"""
Test script for CSM-1B TTS with GPU acceleration and audio playback.
"""

import os
import sys
import time
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("csm_gpu_test")

def main():
    """Test CSM-1B TTS with GPU acceleration and audio playback."""
    try:
        # Import the TTS module
        from tts import create_tts
        import torch
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        if device == "cuda":
            print(f"GPU: {torch.cuda.get_device_name(0)}")
            print(f"CUDA version: {torch.version.cuda}")
        
        # Create TTS instance
        print("Initializing CSM-1B TTS...")
        tts = create_tts(engine="csm", device=device, language="EN")
        
        # Get available voices
        voices = tts.get_available_voices()
        print(f"Available voices: {voices}")
        
        # Get available languages
        languages = tts.get_available_languages()
        print(f"Available languages: {languages}")
        
        # Test text
        text = "Hello, I am Coda. I'm now speaking with CSM-1B, a high-quality text-to-speech model running on GPU for faster performance."
        
        print(f"Synthesizing: {text}")
        
        # Measure time for synthesis
        start_time = time.time()
        
        # Speak the text directly
        print("Speaking text...")
        success = tts.speak(text)
        
        end_time = time.time()
        
        if success:
            print(f"Speech synthesis and playback completed in {end_time - start_time:.2f} seconds")
        else:
            print("Speech synthesis or playback failed")
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
