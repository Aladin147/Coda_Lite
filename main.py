#!/usr/bin/env python3
"""
Coda Lite - Core Operations & Digital Assistant (v0.0.2)
Main entry point for the Coda Lite voice assistant.

This module initializes and coordinates the core components:
- Speech-to-Text (STT)
- Language Model (LLM)
- Text-to-Speech (TTS)
- Tool execution

Current version (v0.0.2) implements the optimized voice loop with concurrent processing.
"""

import os
import sys
import time
import logging
import signal
import threading
from datetime import datetime
from typing import List, Dict, Any, Optional, Callable
from queue import Queue

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/logs/coda_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("coda")

# Import modules
from config.config_loader import ConfigLoader
from stt import WhisperSTT
from llm import OllamaLLM
from tts import create_tts

# Type definitions for conversation history
Message = Dict[str, str]
MessageList = List[Message]

def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)

def load_system_prompt(file_path: str) -> str:
    """Load system prompt from file."""
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return "You are Coda, a helpful voice assistant running locally on the user's computer."

class CodaAssistant:
    """Main Coda Lite assistant class."""

    def __init__(self, config: ConfigLoader):
        """Initialize the Coda assistant."""
        self.config = config
        self.conversation_history: MessageList = []
        self.running = True
        self.processing = False  # Flag to track if we're currently processing a request
        self.response_queue = Queue()  # Queue for responses to be spoken

        # Initialize STT module
        logger.info("Initializing Speech-to-Text module...")
        self.stt = WhisperSTT(
            model_size=config.get("stt.model_size", "base"),
            device=config.get("stt.device", "cuda"),
            compute_type=config.get("stt.compute_type", "float16"),
            language=config.get("stt.language", "en"),
            vad_filter=True
        )

        # Initialize LLM module
        logger.info("Initializing Language Model module...")
        self.llm = OllamaLLM(
            model_name=config.get("llm.model_name", "llama3"),
            host="http://localhost:11434",
            timeout=120
        )

        # Initialize TTS module
        logger.info("Initializing Text-to-Speech module...")
        self.tts = create_tts(
            engine="csm",  # Use CSM-1B TTS
            language=config.get("tts.language", "EN"),
            voice=config.get("tts.voice", "EN-US"),
            device=config.get("tts.device", "cuda")
        )

        # Load system prompt
        system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
        self.system_prompt = load_system_prompt(system_prompt_file)

        # Add system message to conversation history
        self.conversation_history.append({"role": "system", "content": self.system_prompt})

        # Start the TTS worker thread
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

        logger.info("Coda assistant initialized successfully")

    def _tts_worker(self):
        """Worker thread for TTS processing."""
        while self.running:
            try:
                # Get the next response from the queue (blocking with timeout)
                try:
                    response = self.response_queue.get(timeout=0.5)
                except Exception:  # Queue.Empty
                    continue

                # Speak the response
                self.tts.speak(response)

                # Mark the task as done
                self.response_queue.task_done()
            except Exception as e:
                logger.error(f"Error in TTS worker: {e}", exc_info=True)

    def _process_user_input(self, text: str):
        """Process user input in a separate thread."""
        try:
            # Generate response from LLM
            start_time = time.time()
            response = self.llm.chat(
                messages=self.conversation_history,
                temperature=self.config.get("llm.temperature", 0.7),
                max_tokens=self.config.get("llm.max_tokens", 256)
            )
            end_time = time.time()

            logger.info(f"LLM response generated in {end_time - start_time:.2f} seconds")
            logger.info(f"Assistant response: {response}")

            # Add assistant message to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})

            # Print the response
            print(f"Coda: {response}")

            # Add the response to the TTS queue
            self.response_queue.put(response)

            # Limit conversation history to last 10 messages (plus system prompt)
            if len(self.conversation_history) > 11:  # 1 system + 10 messages
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            error_message = "I'm sorry, I encountered an error while processing your request."
            print(f"Coda: {error_message}")
            self.response_queue.put(error_message)
        finally:
            self.processing = False

    def handle_transcription(self, text: str) -> None:
        """Handle transcribed text from STT."""
        if not text.strip():
            logger.info("Empty transcription, ignoring")
            return

        # If we're already processing a request, ignore this one
        if self.processing:
            logger.info("Already processing a request, ignoring")
            return

        logger.info(f"User said: {text}")
        print(f"\nYou: {text}")

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": text})

        # Set the processing flag
        self.processing = True

        # Process the user input in a separate thread
        threading.Thread(
            target=self._process_user_input,
            args=(text,),
            daemon=True
        ).start()

    def should_stop(self) -> bool:
        """Check if the assistant should stop listening."""
        return not self.running

    def run(self) -> None:
        """Run the main conversation loop."""
        logger.info("Starting conversation loop")

        # Welcome message
        welcome_message = "Hello! I'm Coda, your voice assistant. How can I help you today?"
        print(f"\nCoda: {welcome_message}")
        self.response_queue.put(welcome_message)

        try:
            # Start continuous listening
            self.stt.listen_continuous(
                callback=self.handle_transcription,
                stop_callback=self.should_stop,
                silence_threshold=0.1,
                silence_duration=1.0
            )
        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received, stopping conversation loop")
        except Exception as e:
            logger.error(f"Error in conversation loop: {e}", exc_info=True)
        finally:
            self.cleanup()

    def stop(self) -> None:
        """Stop the conversation loop."""
        logger.info("Stopping conversation loop")
        self.running = False

    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up resources")

        # Stop the TTS worker thread
        logger.info("Stopping TTS worker thread")
        self.running = False
        if hasattr(self, 'tts_thread') and self.tts_thread.is_alive():
            try:
                self.tts_thread.join(timeout=2.0)  # Wait for up to 2 seconds
                if self.tts_thread.is_alive():
                    logger.warning("TTS worker thread did not terminate gracefully")
            except Exception as e:
                logger.error(f"Error stopping TTS worker thread: {e}")

        # Close the STT module
        logger.info("Closing STT module")
        try:
            self.stt.close()
        except Exception as e:
            logger.error(f"Error closing STT: {e}")

def signal_handler(sig, frame):
    """Handle signals for graceful shutdown."""
    logger.info(f"Signal {sig} received, shutting down")
    if 'assistant' in globals():
        assistant.stop()

def main():
    """Main entry point for Coda Lite."""
    global assistant

    logger.info("Starting Coda Lite v0.0.2")
    ensure_directories()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = ConfigLoader()

    try:
        # Initialize and run the assistant
        assistant = CodaAssistant(config)
        logger.info("Coda Lite is ready. Press Ctrl+C to exit.")
        assistant.run()
    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        logger.info("Coda Lite shutdown complete. Goodbye!")

if __name__ == "__main__":
    main()
