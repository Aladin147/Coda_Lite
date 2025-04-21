#!/usr/bin/env python3
"""
Example script demonstrating the use of the CSMTTS class.
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

from tts import CSMTTS

def list_models_example():
    """Example of listing available TTS models."""
    print("\n=== Available TTS Models ===")
    
    # Initialize the CSMTTS module
    tts = CSMTTS()
    
    # List available models
    models = tts.list_available_models()
    
    print(f"Found {len(models)} available models:")
    for i, model in enumerate(models[:10], 1):  # Show first 10 models
        print(f"{i}. {model}")
    
    if len(models) > 10:
        print(f"... and {len(models) - 10} more")

def synthesize_example(text, output_path=None):
    """Example of synthesizing speech."""
    print(f"\n=== Synthesizing: '{text}' ===")
    
    # Initialize the CSMTTS module with a specific model
    # You can choose a different model from the list_models_example output
    tts = CSMTTS(
        model_name="tts_models/en/ljspeech/tacotron2-DDC",
        device="cpu"
    )
    
    # Check if the model has multiple speakers
    speakers = tts.list_speakers()
    if speakers:
        print(f"Available speakers: {speakers}")
        speaker = speakers[0]
    else:
        speaker = None
    
    # Check if the model supports multiple languages
    languages = tts.list_languages()
    if languages:
        print(f"Available languages: {languages}")
        language = languages[0] if "en" not in languages else "en"
    else:
        language = None
    
    start_time = time.time()
    
    # Synthesize speech
    if output_path:
        # Save to file
        result = tts.synthesize(
            text=text,
            output_path=output_path,
            speaker=speaker,
            language=language,
            speed=1.0
        )
        end_time = time.time()
        print(f"Speech synthesized in {end_time - start_time:.2f} seconds")
        print(f"Audio saved to: {result}")
    else:
        # Play directly
        print("Playing audio directly...")
        result = tts.synthesize(
            text=text,
            speaker=speaker,
            language=language,
            speed=1.0
        )
        end_time = time.time()
        print(f"Speech synthesized and played in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # List available models
    list_models_example()
    
    # Synthesize speech with direct playback
    text_to_speak = "Hello, I am Coda Lite, your local voice assistant. How can I help you today?"
    synthesize_example(text_to_speak)
    
    # Synthesize speech and save to file
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        synthesize_example(text_to_speak, output_file)
    else:
        print("\nTip: Run with a filename argument to save the audio to a file.")
        print("Example: python examples/tts_example.py output.wav")
