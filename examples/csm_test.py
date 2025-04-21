"""
Test script for CSM-1B TTS (MeloTTS).
"""

import os
import sys
import logging
from pathlib import Path

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger("csm_test")

def main():
    """Test CSM-1B TTS."""
    try:
        # Import the TTS module
        from tts import create_tts
        import torch
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Create TTS instance
        print("Initializing CSM-1B TTS...")
        tts = create_tts(engine="csm", device=device)
        
        # Test text
        text = "Hello, I am Coda. I'm now speaking with CSM-1B, a high-quality text-to-speech model."
        
        print(f"Speaking: {text}")
        
        # Speak the text
        result = tts.speak(text)
        
        print(f"Speech result: {result}")
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
