"""
Test selected English voices in MeloTTS.
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

logger = logging.getLogger("selected_voices_test")

def main():
    """Test selected English voices in MeloTTS."""
    try:
        # Import the TTS module
        from tts import create_tts
        import torch
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # Create TTS instance
        print("Initializing CSM-1B TTS...")
        tts = create_tts(engine="csm", device=device, language="EN")
        
        # Selected voices to test
        selected_voices = ["EN-US", "EN-BR", "EN-AU"]
        
        # Test text
        text = "Hello, I am Coda. This is a demonstration of the CSM-1B text-to-speech model. I can speak in different accents and languages."
        
        # Test each selected voice
        for voice in selected_voices:
            print(f"\nTesting voice: {voice}")
            print("-" * 50)
            
            # Speak the text with this voice
            print(f"Speaking with {voice} voice: \"{text}\"")
            
            # Measure time for synthesis
            start_time = time.time()
            
            # Speak the text directly
            success = tts.speak(text, speaker=voice)
            
            end_time = time.time()
            
            if success:
                print(f"Speech synthesis and playback completed in {end_time - start_time:.2f} seconds")
            else:
                print("Speech synthesis or playback failed")
            
            # Wait a bit between voices
            time.sleep(1)
        
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
