#!/usr/bin/env python3
"""
Simple test script for Dia TTS.
This script tests basic functionality of the Dia TTS implementation.
"""

import os
import sys
import logging
import argparse

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("dia_simple_test")

def test_dia_tts(text=None, output_path=None, use_gpu=False):
    """Test Dia TTS with the given text."""
    try:
        from tts import create_tts
        
        # Default text if none provided
        if text is None:
            text = "[S1] Hello, I am testing Dia TTS. [S2] This is a dialogue test with multiple speakers."
        
        # Set device based on GPU availability
        device = "cuda" if use_gpu else "cpu"
        logger.info(f"Using device: {device}")
        
        # Create TTS instance
        logger.info("Creating Dia TTS instance...")
        tts = create_tts(
            engine="dia",
            device=device,
            temperature=1.3,
            top_p=0.95,
            cfg_scale=3.0,
            use_torch_compile=True
        )
        
        # Set output path if not provided
        if output_path is None:
            output_path = "dia_test_output.wav"
        
        # Synthesize speech
        logger.info(f"Synthesizing speech: {text}")
        result_path = tts.synthesize(text, output_path)
        
        if result_path:
            logger.info(f"Speech synthesized successfully to {result_path}")
            return True
        else:
            logger.error("Speech synthesis failed")
            return False
    except Exception as e:
        logger.error(f"Error testing Dia TTS: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Simple Dia TTS test")
    parser.add_argument("--text", type=str, help="Text to synthesize")
    parser.add_argument("--output", type=str, help="Output file path")
    parser.add_argument("--gpu", action="store_true", help="Use GPU for inference")
    args = parser.parse_args()
    
    success = test_dia_tts(args.text, args.output, args.gpu)
    
    if success:
        logger.info("Test completed successfully")
        return 0
    else:
        logger.error("Test failed")
        return 1

if __name__ == "__main__":
    sys.exit(main())
