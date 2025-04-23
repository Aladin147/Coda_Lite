#!/usr/bin/env python3
"""
Example script for testing ElevenLabs TTS integration.
"""

import os
import sys
import argparse
import logging
import yaml
import soundfile as sf
from pathlib import Path

# Add the parent directory to the path so we can import the tts module
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tts import create_tts

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("elevenlabs_example")

def load_config(config_path):
    """Load configuration from YAML file."""
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    """Main function."""
    parser = argparse.ArgumentParser(description="Test ElevenLabs TTS integration")
    parser.add_argument("--text", type=str, default="Hello, I am Coda, your AI assistant. I'm using ElevenLabs for text to speech. How can I help you today?", help="Text to synthesize")
    parser.add_argument("--output", type=str, default="elevenlabs_output.wav", help="Output file path")
    parser.add_argument("--config", type=str, default="config/config.yaml", help="Path to config file")
    parser.add_argument("--voice", type=str, help="Voice ID to use (overrides config)")
    parser.add_argument("--model", type=str, help="Model ID to use (overrides config)")
    args = parser.parse_args()
    
    # Load configuration
    config = load_config(args.config)
    tts_config = config.get("tts", {})
    
    # Override config with command line arguments if provided
    if args.voice:
        tts_config["elevenlabs_voice_id"] = args.voice
    if args.model:
        tts_config["elevenlabs_model_id"] = args.model
    
    # Create ElevenLabs TTS instance
    try:
        tts = create_tts(
            engine="elevenlabs",
            api_key=tts_config.get("elevenlabs_api_key"),
            voice_id=tts_config.get("elevenlabs_voice_id"),
            model_id=tts_config.get("elevenlabs_model_id"),
            stability=tts_config.get("elevenlabs_stability", 0.5),
            similarity_boost=tts_config.get("elevenlabs_similarity_boost", 0.75),
            style=tts_config.get("elevenlabs_style", 0.0),
            use_speaker_boost=tts_config.get("elevenlabs_use_speaker_boost", True),
        )
        
        logger.info(f"ElevenLabs TTS initialized with voice: {tts_config.get('elevenlabs_voice_id')}")
        logger.info(f"Using model: {tts_config.get('elevenlabs_model_id')}")
        
        # Synthesize speech
        logger.info(f"Synthesizing text: {args.text}")
        audio = tts.synthesize(args.text, args.output)
        
        logger.info(f"Speech synthesized successfully to {args.output}")
        
        # List available voices
        logger.info("Fetching available voices...")
        voices = tts.get_available_voices()
        logger.info(f"Available voices: {len(voices)}")
        for i, voice in enumerate(voices[:5]):  # Show only first 5 voices
            logger.info(f"Voice {i+1}: {voice['name']} (ID: {voice['id']})")
        if len(voices) > 5:
            logger.info(f"... and {len(voices) - 5} more voices")
        
        return 0
    except Exception as e:
        logger.error(f"Error: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
