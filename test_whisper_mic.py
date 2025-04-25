#!/usr/bin/env python3
"""
Test script for Whisper STT with microphone input.
"""

import os
import sys
import time
import argparse
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("whisper_test")

# Add the parent directory to the path so we can import the stt module
sys.path.insert(0, str(Path(__file__).resolve().parent))

from stt.whisper_stt import WhisperSTT

def test_listen_once(stt, duration=5):
    """Test listening once for a fixed duration."""
    logger.info(f"Listening for {duration} seconds...")
    print(f"\nPlease speak for {duration} seconds...\n")
    
    # Start listening
    start_time = time.time()
    transcription = stt.listen(duration=duration)
    end_time = time.time()
    
    # Print results
    print(f"\nTranscription: {transcription}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
    
    return transcription

def test_listen_continuous(stt, max_duration=30):
    """Test continuous listening with push-to-talk."""
    def on_transcription(text):
        print(f"\nTranscription: {text}")
    
    # Set up a stop callback that will stop after max_duration
    start_time = time.time()
    def stop_callback():
        elapsed = time.time() - start_time
        if elapsed > max_duration:
            print(f"\nReached maximum duration of {max_duration} seconds.")
            return True
        return False
    
    print(f"\nContinuous listening started. Will stop after {max_duration} seconds.")
    print("Speak naturally with pauses, and the system will transcribe when you pause.")
    print("Press Ctrl+C to stop earlier.\n")
    
    try:
        # Start continuous listening
        stt.listen_continuous(
            callback=on_transcription,
            stop_callback=stop_callback,
            silence_threshold=0.01,  # Adjust based on your microphone and environment
            silence_duration=1.0     # Seconds of silence to consider speech ended
        )
    except KeyboardInterrupt:
        print("\nStopped by user.")

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test Whisper STT with microphone")
    parser.add_argument("--model", type=str, default="base", help="Model size (tiny, base, small, medium, large-v3)")
    parser.add_argument("--device", type=str, default="cuda" if os.environ.get("CUDA_VISIBLE_DEVICES") else "cpu", 
                        help="Device to use (cpu, cuda, auto)")
    parser.add_argument("--continuous", action="store_true", help="Use continuous listening mode")
    parser.add_argument("--duration", type=int, default=5, help="Duration to listen in seconds (for non-continuous mode)")
    parser.add_argument("--max-duration", type=int, default=30, help="Maximum duration for continuous mode in seconds")
    parser.add_argument("--language", type=str, default=None, help="Language code (e.g., en, fr, de)")
    args = parser.parse_args()
    
    # Print test configuration
    print(f"Testing Whisper STT with:")
    print(f"- Model: {args.model}")
    print(f"- Device: {args.device}")
    print(f"- Mode: {'Continuous' if args.continuous else 'Single'}")
    print(f"- Duration: {args.duration if not args.continuous else args.max_duration} seconds")
    print(f"- Language: {args.language or 'Auto-detect'}")
    
    try:
        # Initialize WhisperSTT
        stt = WhisperSTT(
            model_size=args.model,
            device=args.device,
            compute_type="float16" if args.device == "cuda" else "float32",
            language=args.language,
            vad_filter=True
        )
        
        # Run the appropriate test
        if args.continuous:
            test_listen_continuous(stt, args.max_duration)
        else:
            test_listen_once(stt, args.duration)
            
    except Exception as e:
        logger.error(f"Error during test: {e}", exc_info=True)
        return 1
    finally:
        # Clean up
        if 'stt' in locals():
            stt.close()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
