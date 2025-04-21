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

from tts import create_tts, CoquiTTS

def list_models_example():
    """Example of listing available TTS models."""
    print("\n=== Available TTS Models ===")

    # Initialize the TTS module using the factory function
    tts = create_tts(engine="coqui")

    # List available models (this is specific to Coqui TTS)
    if isinstance(tts, CoquiTTS):
        models = tts.list_available_models()

        print(f"Found {len(models)} available models:")
        for i, model in enumerate(models[:10], 1):  # Show first 10 models
            print(f"{i}. {model}")

        if len(models) > 10:
            print(f"... and {len(models) - 10} more")

def synthesize_example(text, output_path=None, engine="coqui"):
    """Example of synthesizing speech."""
    print(f"\n=== Synthesizing: '{text}' with {engine} engine ===")

    # Initialize the TTS module using the factory function
    # You can choose a different engine or model
    tts = create_tts(
        engine=engine,
        model_name="tts_models/en/ljspeech/tacotron2-DDC" if engine == "coqui" else None,
        device="cpu"
    )

    # Get available voices
    voices = tts.get_available_voices()
    if voices:
        print(f"Available voices: {voices}")
        voice = voices[0]
    else:
        voice = None

    # Get available languages
    languages = tts.get_available_languages()
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
            speaker=voice,  # For Coqui TTS compatibility
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
            speaker=voice,  # For Coqui TTS compatibility
            language=language,
            speed=1.0
        )
        end_time = time.time()
        print(f"Speech synthesized and played in {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    # List available models
    list_models_example()

    # Synthesize speech with direct playback using Coqui TTS
    text_to_speak = "Hello, I am Coda Lite, your local voice assistant. How can I help you today?"
    synthesize_example(text_to_speak, engine="coqui")

    # Try the CSM placeholder (which will fall back to Coqui for now)
    print("\n=== Testing CSM placeholder (falls back to Coqui) ===")
    synthesize_example("This is a test of the CSM placeholder.", engine="csm")

    # Synthesize speech and save to file
    if len(sys.argv) > 1:
        output_file = sys.argv[1]
        synthesize_example(text_to_speak, output_file, engine="coqui")
    else:
        print("\nTip: Run with a filename argument to save the audio to a file.")
        print("Example: python examples/tts_example.py output.wav")
