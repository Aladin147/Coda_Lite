"""
Example script to test CSM-1B TTS.
"""

import os
import sys
import logging

# Add the parent directory to the path so we can import the modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

from tts import create_tts

def main():
    """Test CSM-1B TTS."""
    print("Initializing CSM-1B TTS...")
    
    # Create TTS instance
    tts = create_tts(engine="csm")
    
    # Test text
    text = "Hello, I am Coda. I'm now speaking with CSM-1B, a high-quality text-to-speech model."
    
    print(f"Speaking: {text}")
    
    # Speak the text
    tts.speak(text)
    
    print("Done!")

if __name__ == "__main__":
    main()
