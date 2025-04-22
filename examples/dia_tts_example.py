#!/usr/bin/env python3
"""
Example script demonstrating the use of Dia TTS in Coda Lite.
"""

import os
import sys
import argparse
import logging

# Add the parent directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tts import create_tts

def list_voices_example():
    """Example of listing available TTS voices."""
    print("\n=== Dia TTS Information ===")

    # Initialize the TTS module using the factory function
    tts = create_tts(engine="dia", device="cpu")

    # List available voices (Dia doesn't have predefined voices)
    voices = tts.get_available_voices()
    print(f"Available voices: {voices}")
    print("Note: Dia TTS doesn't have predefined voices. It uses voice cloning instead.")

    # List available languages
    languages = tts.get_available_languages()
    print(f"Available languages: {languages}")
    print("Note: Dia TTS currently only supports English.")

def synthesize_example(text, output_path=None, audio_prompt_path=None):
    """Example of synthesizing speech with Dia TTS."""
    print(f"\n=== Synthesizing with Dia TTS ===")
    print(f"Text: '{text}'")
    
    if audio_prompt_path:
        print(f"Using voice from: {audio_prompt_path}")

    # Initialize the TTS module using the factory function
    tts = create_tts(
        engine="dia",
        device="cpu",
        audio_prompt_path=audio_prompt_path
    )

    # Synthesize speech
    if output_path:
        print(f"Saving to: {output_path}")
        result_path = tts.synthesize(text, output_path)
        print(f"Speech synthesized and saved to {result_path}")
    else:
        print("Playing directly...")
        tts.speak(text)
        print("Speech synthesized and played")

def dialogue_example(output_path=None, audio_prompt_path=None):
    """Example of synthesizing dialogue with Dia TTS."""
    print("\n=== Synthesizing Dialogue with Dia TTS ===")
    
    # Create a dialogue script
    dialogue = """
    [S1] Hello, how are you today?
    [S2] I'm doing well, thank you for asking. How about you?
    [S1] I'm great! I'm excited to be using Dia TTS for the first time.
    [S2] That's wonderful to hear. Dia TTS is designed to create natural-sounding dialogue.
    [S1] I can definitely tell. The voices sound very realistic. (laughs)
    [S2] Yes, and it can even handle non-verbal elements like laughter and pauses naturally.
    """
    
    # Initialize the TTS module
    tts = create_tts(
        engine="dia",
        device="cpu",
        audio_prompt_path=audio_prompt_path
    )
    
    # Synthesize the dialogue
    if output_path:
        result_path = tts.synthesize(dialogue, output_path)
        print(f"Dialogue synthesized and saved to {result_path}")
    else:
        tts.speak(dialogue)
        print("Dialogue synthesized and played")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Dia TTS example script")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--prompt", type=str, help="Audio prompt file path for voice cloning")
    parser.add_argument("--dialogue", action="store_true", help="Generate a dialogue example")
    args = parser.parse_args()

    # Configure logging
    logging.basicConfig(level=logging.INFO)

    # Show TTS information
    list_voices_example()

    # Synthesize speech
    if args.dialogue:
        dialogue_example(args.output, args.prompt)
    elif args.text:
        synthesize_example(args.text, args.output, args.prompt)
    else:
        # Default example
        text = "Hello, I am Coda Lite, your local voice assistant. How can I help you today?"
        synthesize_example(text, args.output, args.prompt)

if __name__ == "__main__":
    main()
