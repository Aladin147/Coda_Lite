#!/usr/bin/env python3
"""
Test script for the complete voice loop (STT -> LLM -> TTS).
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

logger = logging.getLogger("voice_loop_test")

# Import modules
from config.config_loader import ConfigLoader
from stt import WhisperSTT
from llm import OllamaLLM
from tts import create_tts

def main():
    """Test the complete voice loop."""
    try:
        # Load configuration
        config = ConfigLoader()
        
        print("Initializing components...")
        
        # Initialize STT module
        print("Initializing Speech-to-Text module...")
        stt = WhisperSTT(
            model_size=config.get("stt.model_size", "base"),
            device=config.get("stt.device", "cpu"),
            compute_type=config.get("stt.compute_type", "float32"),
            language=config.get("stt.language", "en"),
            vad_filter=True
        )
        
        # Initialize LLM module
        print("Initializing Language Model module...")
        llm = OllamaLLM(
            model_name=config.get("llm.model_name", "llama3"),
            host="http://localhost:11434",
            timeout=120
        )
        
        # Initialize TTS module
        print("Initializing Text-to-Speech module...")
        tts = create_tts(
            engine="csm",  # Use CSM-1B TTS
            device=config.get("tts.device", "cuda"),
            language=config.get("tts.language", "EN"),
            voice=config.get("tts.voice", "EN-US")
        )
        
        # Load system prompt
        system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
        try:
            with open(system_prompt_file, 'r') as f:
                system_prompt = f.read().strip()
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            system_prompt = "You are Coda, a helpful voice assistant running locally on the user's computer."
        
        # Initialize conversation history
        conversation_history = [{"role": "system", "content": system_prompt}]
        
        # Welcome message
        welcome_message = "Hello! I'm Coda, your voice assistant. How can I help you today?"
        print(f"\nCoda: {welcome_message}")
        tts.speak(welcome_message)
        
        # Test the voice loop
        print("\nTesting voice loop...")
        print("Speak for 5 seconds...")
        
        # Listen for user input
        user_input = stt.listen(duration=5)
        
        if user_input:
            print(f"\nYou: {user_input}")
            
            # Add user message to conversation history
            conversation_history.append({"role": "user", "content": user_input})
            
            # Generate response from LLM
            print("Generating response...")
            start_time = time.time()
            response = llm.chat(
                messages=conversation_history,
                temperature=config.get("llm.temperature", 0.7),
                max_tokens=config.get("llm.max_tokens", 256)
            )
            end_time = time.time()
            
            print(f"Response generated in {end_time - start_time:.2f} seconds")
            print(f"\nCoda: {response}")
            
            # Add assistant message to conversation history
            conversation_history.append({"role": "assistant", "content": response})
            
            # Speak the response
            print("Speaking response...")
            tts.speak(response)
        else:
            print("No speech detected or transcription failed.")
        
        # Clean up
        print("\nCleaning up...")
        stt.close()
        
        print("\nTest completed!")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
