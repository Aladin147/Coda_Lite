"""
List all available voices in MeloTTS for each supported language.
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

logger = logging.getLogger("melotts_voices")

def main():
    """List all available voices in MeloTTS for each supported language."""
    try:
        # Add the melotts directory to the Python path
        melotts_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'melotts', 'MeloTTS-main')
        if melotts_path not in sys.path:
            sys.path.append(melotts_path)
        
        # Import MeloTTS
        from melo.api import TTS
        import torch
        
        # Check if CUDA is available
        device = "cuda" if torch.cuda.is_available() else "cpu"
        print(f"Using device: {device}")
        
        # List of supported languages
        languages = ["EN", "ES", "FR", "ZH", "JP", "KR"]
        
        print("\nAvailable voices for each language:")
        print("==================================")
        
        for lang in languages:
            print(f"\nLanguage: {lang}")
            print("-" * (len(lang) + 10))
            
            try:
                # Initialize the TTS model for this language
                model = TTS(language=lang, device=device)
                
                # Get available speakers
                speakers = model.hps.data.spk2id
                
                # Print the speakers
                print(f"Found {len(speakers)} voices:")
                for i, speaker in enumerate(speakers.keys(), 1):
                    print(f"  {i}. {speaker}")
                
                # Clean up to free memory
                del model
                if device == "cuda":
                    torch.cuda.empty_cache()
                
            except Exception as e:
                print(f"Error loading voices for language {lang}: {e}")
        
        print("\nDone!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
