#!/usr/bin/env python3
"""
Script to list all available voices in your ElevenLabs account.
"""

import os
import sys
import logging
from elevenlabs.client import ElevenLabs

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("list_voices")

def main():
    """Main function."""
    # Get API key from environment variable or config file
    api_key = os.environ.get("ELEVENLABS_API_KEY")
    if not api_key:
        # Try to read from config file
        try:
            import yaml
            with open("config/config.yaml", "r") as f:
                config = yaml.safe_load(f)
                api_key = config.get("tts", {}).get("elevenlabs_api_key", "")
        except Exception as e:
            logger.error(f"Error reading config file: {e}")
            api_key = ""
    
    if not api_key:
        logger.error("No API key found. Please set ELEVENLABS_API_KEY environment variable or add it to config/config.yaml")
        return 1
    
    # Initialize ElevenLabs client
    client = ElevenLabs(api_key=api_key)
    
    try:
        # Get all voices
        voices_response = client.voices.get_all()
        
        # Print voice information
        logger.info(f"Found {len(voices_response.voices)} voices in your account:")
        print("\n=== Available Voices ===")
        
        for i, voice in enumerate(voices_response.voices):
            print(f"{i+1}. Name: {voice.name}")
            print(f"   ID: {voice.voice_id}")
            print(f"   Description: {voice.description or 'N/A'}")
            print(f"   Category: {voice.category}")
            print()
        
        return 0
    except Exception as e:
        logger.error(f"Error getting voices: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
