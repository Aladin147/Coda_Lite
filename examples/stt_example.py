#!/usr/bin/env python3
"""
Example script demonstrating the use of the WhisperSTT class.
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

from stt import WhisperSTT

def transcribe_file_example(file_path):
    """Example of transcribing an audio file."""
    print(f"\n=== Transcribing file: {file_path} ===")
    
    # Initialize the WhisperSTT module with a small model for faster loading
    stt = WhisperSTT(
        model_size="tiny",  # Use tiny model for quick demo
        device="cpu",
        compute_type="float32",
        vad_filter=True,  # Enable voice activity detection
    )
    
    # Transcribe the audio file
    start_time = time.time()
    transcription = stt.transcribe_audio(file_path)
    end_time = time.time()
    
    print(f"Transcription completed in {end_time - start_time:.2f} seconds")
    print(f"Transcription: {transcription}")
    
    # Clean up
    stt.close()

def listen_example(duration=5):
    """Example of listening for speech and transcribing."""
    print(f"\n=== Listening for {duration} seconds ===")
    
    # Initialize the WhisperSTT module with a small model for faster loading
    stt = WhisperSTT(
        model_size="tiny",  # Use tiny model for quick demo
        device="cpu",
        compute_type="float32",
    )
    
    print(f"Speak for {duration} seconds...")
    
    # Listen and transcribe
    start_time = time.time()
    transcription = stt.listen(duration=duration)
    end_time = time.time()
    
    print(f"Transcription completed in {end_time - start_time:.2f} seconds")
    print(f"Transcription: {transcription}")
    
    # Clean up
    stt.close()

def continuous_listen_example(max_duration=30):
    """Example of continuous listening and transcribing."""
    print(f"\n=== Continuous listening (max {max_duration} seconds) ===")
    
    # Initialize the WhisperSTT module with a small model for faster loading
    stt = WhisperSTT(
        model_size="tiny",  # Use tiny model for quick demo
        device="cpu",
        compute_type="float32",
    )
    
    # Set up a callback to handle transcriptions
    def handle_transcription(text):
        print(f"Transcription: {text}")
    
    # Set up a stop callback to limit the duration
    start_time = time.time()
    def should_stop():
        return time.time() - start_time > max_duration
    
    print(f"Speak naturally, pausing between phrases. Will listen for up to {max_duration} seconds...")
    print("Press Ctrl+C to stop earlier.")
    
    try:
        # Start continuous listening
        stt.listen_continuous(
            callback=handle_transcription,
            stop_callback=should_stop,
            silence_threshold=0.1,
            silence_duration=1.0,
        )
    except KeyboardInterrupt:
        print("\nStopped by user")
    finally:
        # Clean up
        stt.close()

if __name__ == "__main__":
    # Check if an audio file was provided
    if len(sys.argv) > 1 and os.path.isfile(sys.argv[1]):
        transcribe_file_example(sys.argv[1])
    else:
        print("No audio file provided or file not found.")
        print("Running listen examples instead.")
        
        try:
            # Run the listen example
            listen_example(duration=5)
            
            # Run the continuous listen example
            continuous_listen_example(max_duration=30)
        except KeyboardInterrupt:
            print("\nExamples stopped by user")
