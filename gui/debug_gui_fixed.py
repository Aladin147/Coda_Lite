#!/usr/bin/env python3
"""
Coda Lite - Debug GUI (Fixed Version)
A lightweight debug GUI for testing the Coda Lite voice assistant components.
"""

import os
import sys
import time
import json
import logging
import threading
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any

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
logger = logging.getLogger("coda.gui")

# Import PySimpleGUI
try:
    import PySimpleGUI as sg
    logger.info("PySimpleGUI imported successfully")
except ImportError as e:
    logger.error(f"Error importing PySimpleGUI: {e}")
    print(f"Error importing PySimpleGUI: {e}")
    print("Please install PySimpleGUI: pip install PySimpleGUI")
    sys.exit(1)

# Import Coda modules
try:
    from config.config_loader import ConfigLoader
    logger.info("ConfigLoader imported successfully")
except ImportError as e:
    logger.error(f"Error importing ConfigLoader: {e}")
    print(f"Error importing ConfigLoader: {e}")
    sys.exit(1)

try:
    from llm import OllamaLLM
    logger.info("OllamaLLM imported successfully")
except ImportError as e:
    logger.error(f"Error importing OllamaLLM: {e}")
    print(f"Error importing OllamaLLM: {e}")
    sys.exit(1)

try:
    from tts import create_tts
    logger.info("TTS module imported successfully")
except ImportError as e:
    logger.error(f"Error importing TTS module: {e}")
    print(f"Error importing TTS module: {e}")
    sys.exit(1)

# Import audio modules for device verification
try:
    import sounddevice as sd
    import numpy as np
    AUDIO_AVAILABLE = True
    logger.info("Audio modules imported successfully")

    # Print audio device information
    devices = sd.query_devices()
    logger.info(f"Audio devices: {devices}")
    logger.info(f"Default input device: {sd.default.device[0]}")
    logger.info(f"Default output device: {sd.default.device[1]}")

    # Test audio output with a short beep
    def test_audio():
        try:
            # Generate a short beep (440Hz for 0.5 seconds)
            sample_rate = 44100
            t = np.linspace(0, 0.5, int(sample_rate * 0.5), False)
            beep = 0.5 * np.sin(2 * np.pi * 440 * t)

            # Play the beep
            sd.play(beep, sample_rate)
            sd.wait()
            logger.info("Audio test completed successfully")
            return True
        except Exception as e:
            logger.error(f"Audio test failed: {e}")
            return False

    # Run the audio test
    AUDIO_TEST_PASSED = test_audio()

except ImportError:
    AUDIO_AVAILABLE = False
    AUDIO_TEST_PASSED = False
    logger.warning("Could not import audio modules. Audio device verification will be skipped.")

# Type definitions for conversation history
Message = Dict[str, str]
MessageList = List[Message]

class CodaDebugWrapper:
    """Wrapper for Coda components for use in the debug GUI."""

    def __init__(self):
        """Initialize the Coda debug wrapper."""
        # Load configuration
        self.config = ConfigLoader()
        logger.info("Configuration loaded")

        # Initialize conversation history
        self.conversation_history: MessageList = []

        # Load system prompt
        system_prompt_file = self.config.get("llm.system_prompt_file", "config/prompts/system.txt")
        self.system_prompt = self._load_system_prompt(system_prompt_file)
        logger.info(f"System prompt loaded from {system_prompt_file}")

        # Add system message to conversation history
        self.conversation_history.append({"role": "system", "content": self.system_prompt})

        # Initialize LLM module
        logger.info("Initializing Language Model module...")
        try:
            self.llm = OllamaLLM(
                model_name=self.config.get("llm.model_name", "llama3"),
                host="http://localhost:11434",
                timeout=120
            )
            logger.info(f"LLM initialized with model: {self.llm.model_name}")
        except Exception as e:
            logger.error(f"Error initializing LLM: {e}")
            raise

        # Initialize TTS module
        logger.info("Initializing Text-to-Speech module...")
        try:
            # Try to create TTS with specific model
            try:
                self.tts = create_tts(
                    engine=self.config.get("tts.engine", "coqui"),
                    model_name=self.config.get("tts.model_name", None),
                    device=self.config.get("tts.device", "cpu")
                )
            except Exception as model_error:
                # If that fails, try with default model
                logger.warning(f"Failed to initialize TTS with specific model: {model_error}")
                logger.info("Trying with default model...")
                self.tts = create_tts(engine="coqui")

            logger.info("TTS initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing TTS: {e}")
            # Create a mock TTS for testing
            from tts.mock_tts import MockTTS
            logger.warning("Using MockTTS as fallback")
            self.tts = MockTTS()
            print("\n[WARNING] Using MockTTS - no audio output will be produced")

        logger.info("Coda debug wrapper initialized successfully")

    def _load_system_prompt(self, file_path: str) -> str:
        """Load system prompt from file."""
        try:
            with open(file_path, 'r') as f:
                return f.read().strip()
        except Exception as e:
            logger.error(f"Error loading system prompt: {e}")
            return "You are Coda, a helpful voice assistant running locally on the user's computer."

    def process_input(self, text: str, temperature: float = 0.7, max_tokens: int = 256) -> Dict[str, Any]:
        """
        Process user input and generate a response.

        Args:
            text: User input text
            temperature: LLM temperature
            max_tokens: Maximum tokens to generate

        Returns:
            Dict with response text and timing information
        """
        if not text.strip():
            return {"response": "", "error": "Empty input", "timings": {}}

        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": text})

        # Generate response from LLM
        try:
            # Timing information
            timings = {}

            # Start LLM generation
            logger.info(f"Sending to LLM: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"\n[LLM] Processing: {text[:50]}{'...' if len(text) > 50 else ''}")

            llm_start = time.time()
            response_obj = self.llm.chat(
                messages=self.conversation_history,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False  # Ensure we're not using streaming mode
            )

            # Check if response is a generator (streaming response)
            if hasattr(response_obj, '__iter__') and hasattr(response_obj, '__next__'):
                # It's a generator, collect all chunks
                logger.info("Received streaming response, collecting chunks...")
                print("[LLM] Received streaming response, collecting chunks...")
                response = ""
                try:
                    for chunk in response_obj:
                        if chunk:
                            response += chunk
                            print(f"[LLM] Received chunk: {chunk[:20]}{'...' if len(chunk) > 20 else ''}")
                except Exception as e:
                    logger.error(f"Error collecting response chunks: {e}")
                    print(f"[LLM] Error collecting response chunks: {e}")

                # Log the collected response
                print(f"[LLM] Complete response: {response[:100]}{'...' if len(response) > 100 else ''}")
            else:
                # It's a regular string response
                response = response_obj
                print(f"[LLM] Regular response: {response[:100]}{'...' if len(response) > 100 else ''}")

            # If response is empty, try again with stream=True
            if not response:
                logger.warning("Empty response received, trying again with stream=True")
                print("[LLM] Empty response received, trying again with stream=True")

                try:
                    # Try again with streaming mode
                    response_obj = self.llm.chat(
                        messages=self.conversation_history,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True  # Use streaming mode
                    )

                    # Collect chunks
                    response = ""
                    for chunk in response_obj:
                        if chunk:
                            response += chunk
                            print(f"[LLM] Received chunk: {chunk[:20]}{'...' if len(chunk) > 20 else ''}")

                    print(f"[LLM] Complete response (retry): {response[:100]}{'...' if len(response) > 100 else ''}")
                except Exception as e:
                    logger.error(f"Error in retry with streaming: {e}")
                    print(f"[LLM] Error in retry with streaming: {e}")

            llm_end = time.time()

            # Record timing
            timings["llm_time"] = llm_end - llm_start
            timings["total_time"] = llm_end - llm_start

            logger.info(f"LLM response received in {timings['llm_time']:.2f} seconds")
            print(f"[LLM] Response received in {timings['llm_time']:.2f} seconds")

            # Add assistant message to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})

            # Limit conversation history to last 10 messages (plus system prompt)
            if len(self.conversation_history) > 11:  # 1 system + 10 messages
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]

            return {
                "response": response,
                "error": None,
                "timings": timings
            }

        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            print(f"\n[LLM] ERROR: {e}")
            return {
                "response": "",
                "error": str(e),
                "timings": {}
            }

    def speak_response(self, text: str) -> Dict[str, Any]:
        """
        Speak the response using TTS.

        Args:
            text: Text to speak

        Returns:
            Dict with timing information
        """
        if not text or not text.strip():
            print("\n[TTS] ERROR: Empty text provided to speak_response")
            logger.error("Empty text provided to speak_response")
            return {"error": "Empty text", "timings": {}}

        try:
            # Timing information
            timings = {}

            # Log before TTS generation
            logger.info(f"[TTS] Attempting to speak: {text[:50]}{'...' if len(text) > 50 else ''}")
            print(f"\n[TTS] Attempting to speak: {text[:50]}{'...' if len(text) > 50 else ''}")

            # Start TTS generation
            tts_start = time.time()

            # Check if text is valid
            if isinstance(text, str) and text.strip():
                result = self.tts.synthesize(text)
                success = True
            else:
                print(f"\n[TTS] WARNING: Invalid text format: {type(text)}")
                result = None
                success = False

            tts_end = time.time()

            # Record timing
            timings["tts_time"] = tts_end - tts_start

            # Log after TTS generation
            if success:
                logger.info(f"[TTS] Speech synthesis completed. Result: {result}")
                print(f"[TTS] Speech synthesis completed. Time: {timings['tts_time']:.2f}s")
            else:
                logger.warning("[TTS] Speech synthesis failed due to invalid text")
                print("[TTS] Speech synthesis failed due to invalid text")

            return {
                "error": None if success else "Invalid text format",
                "timings": timings,
                "result": result,
                "success": success
            }

        except Exception as e:
            logger.error(f"Error speaking response: {e}", exc_info=True)
            print(f"\n[TTS] ERROR: {e}")
            return {
                "error": str(e),
                "timings": {},
                "success": False
            }

    def save_conversation(self, file_path: str) -> bool:
        """
        Save the conversation history to a file.

        Args:
            file_path: Path to save the conversation

        Returns:
            bool: True if successful, False otherwise
        """
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            with open(file_path, 'w') as f:
                json.dump(self.conversation_history, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"Error saving conversation: {e}", exc_info=True)
            return False

    def clear_conversation(self) -> None:
        """Clear the conversation history except for the system prompt."""
        self.conversation_history = [self.conversation_history[0]]

def create_gui():
    """Create the PySimpleGUI interface."""
    # Set theme
    sg.theme('DarkBlue3')

    # Define layout
    layout = [
        [sg.Text('Coda Lite - Debug GUI', font=('Helvetica', 16))],
        [sg.HorizontalSeparator()],

        # Input section
        [sg.Text('User Input:', font=('Helvetica', 11))],
        [sg.Multiline(key='-INPUT-', size=(80, 5), font=('Helvetica', 10))],
        [
            sg.Button('Send', key='-SEND-', size=(10, 1)),
            sg.Button('Clear Input', key='-CLEAR_INPUT-', size=(10, 1)),
            sg.Text('Temperature:'),
            sg.Slider(range=(0.1, 1.0), default_value=0.7, resolution=0.1, orientation='h', size=(10, 15), key='-TEMP-'),
            sg.Text('Max Tokens:'),
            sg.Slider(range=(50, 500), default_value=256, resolution=1, orientation='h', size=(10, 15), key='-MAX_TOKENS-')
        ],

        [sg.HorizontalSeparator()],

        # Response section
        [sg.Text('LLM Response:', font=('Helvetica', 11))],
        [sg.Multiline(key='-RESPONSE-', size=(80, 10), font=('Helvetica', 10), disabled=True, background_color='#f0f0f0')],
        [
            sg.Button('Speak', key='-SPEAK-', size=(10, 1)),
            sg.Button('Copy', key='-COPY-', size=(10, 1)),
            sg.Button('Clear Response', key='-CLEAR_RESPONSE-', size=(10, 1)),
            sg.Checkbox('Auto-speak', key='-AUTO_SPEAK-', default=False)
        ],

        [sg.HorizontalSeparator()],

        # Log section
        [sg.Text('Debug Log:', font=('Helvetica', 11))],
        [sg.Multiline(key='-LOG-', size=(80, 8), font=('Courier', 9), disabled=True, autoscroll=True, background_color='#000000', text_color='#00FF00')],

        # Options section
        [
            sg.Button('Clear Log', key='-CLEAR_LOG-', size=(10, 1)),
            sg.Button('Save Conversation', key='-SAVE-', size=(15, 1)),
            sg.Button('Clear Conversation', key='-CLEAR_CONV-', size=(15, 1)),
            sg.Checkbox('Show Timing', key='-SHOW_TIMING-', default=True)
        ],

        [sg.HorizontalSeparator()],

        # Status bar
        [
            sg.Text('Status:', size=(6, 1)),
            sg.Text('Ready', key='-STATUS-', size=(50, 1)),
            sg.Button('Exit', key='-EXIT-', size=(10, 1))
        ]
    ]

    # Create window
    window = sg.Window('Coda Lite - Debug GUI', layout, finalize=True, resizable=True)

    return window

def log_message(window, message, level="INFO"):
    """Add a message to the log window."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"

    # Update the log element
    current_log = window['-LOG-'].get()
    window['-LOG-'].update(current_log + log_entry)

def process_in_thread(window, coda, text, temperature, max_tokens):
    """Process input in a separate thread to keep the GUI responsive."""
    try:
        # Update status
        window['-STATUS-'].update('Processing...')
        window.refresh()

        # Process input
        result = coda.process_input(text, temperature, max_tokens)

        # Update response
        if result["error"]:
            window['-RESPONSE-'].update(f"Error: {result['error']}")
            log_message(window, f"Error generating response: {result['error']}", "ERROR")
        else:
            # Check if response is valid
            response = result.get("response", "")
            if response:
                # Update the response box
                window['-RESPONSE-'].update(response)
                log_message(window, f"Response received: {response[:50]}{'...' if len(response) > 50 else ''}")

                # Log timing information
                if window['-SHOW_TIMING-'].get():
                    llm_time = result["timings"].get("llm_time", 0)
                    log_message(window, f"Response generated in {llm_time:.2f} seconds")

                # Auto-speak if enabled
                if window['-AUTO_SPEAK-'].get():
                    window['-STATUS-'].update('Speaking...')
                    window.refresh()

                    speak_result = coda.speak_response(response)

                    if speak_result.get("error"):
                        log_message(window, f"Error speaking response: {speak_result['error']}", "ERROR")
                    elif window['-SHOW_TIMING-'].get():
                        tts_time = speak_result["timings"].get("tts_time", 0)
                        log_message(window, f"Speech synthesized in {tts_time:.2f} seconds")
            else:
                window['-RESPONSE-'].update("No response received from LLM")
                log_message(window, "No response received from LLM", "ERROR")

        # Update status
        window['-STATUS-'].update('Ready')

    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        log_message(window, f"Error in processing thread: {e}", "ERROR")
        log_message(window, f"Traceback: {error_traceback}", "ERROR")
        window['-STATUS-'].update('Error')

def main():
    """Main entry point for the Coda Lite debug GUI."""
    # Create the GUI
    window = create_gui()

    # Log audio device information
    if AUDIO_AVAILABLE:
        log_message(window, f"Audio modules loaded successfully")
        if AUDIO_TEST_PASSED:
            log_message(window, f"Audio test passed - sound output is working")
        else:
            log_message(window, f"Audio test failed - check sound output", "WARNING")
    else:
        log_message(window, f"Audio modules not available - sound output may not work", "WARNING")

    # Initialize the Coda wrapper
    try:
        log_message(window, "Initializing Coda debug wrapper...")
        coda = CodaDebugWrapper()
        log_message(window, "Coda debug wrapper initialized successfully")
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        log_message(window, f"Error initializing Coda: {e}", "ERROR")
        log_message(window, f"Traceback: {error_traceback}", "ERROR")
        coda = None

    # Event loop
    while True:
        event, values = window.read(timeout=100)

        # Exit event
        if event == sg.WINDOW_CLOSED or event == '-EXIT-':
            break

        # Check if Coda is initialized
        if coda is None:
            if event not in ['-EXIT-', '-CLEAR_LOG-']:
                log_message(window, "Coda is not initialized", "ERROR")
                continue

        # Send button
        if event == '-SEND-':
            text = values['-INPUT-'].strip()
            if text:
                temperature = float(values['-TEMP-'])
                max_tokens = int(values['-MAX_TOKENS-'])

                log_message(window, f"Processing input: {text[:50]}{'...' if len(text) > 50 else ''}")

                # Process in a separate thread
                threading.Thread(
                    target=process_in_thread,
                    args=(window, coda, text, temperature, max_tokens),
                    daemon=True
                ).start()
            else:
                log_message(window, "Empty input", "WARNING")

        # Speak button
        elif event == '-SPEAK-':
            text = values['-RESPONSE-'].strip()
            if text:
                window['-STATUS-'].update('Speaking...')
                window.refresh()

                # Speak in a separate thread
                def speak_thread():
                    try:
                        log_message(window, f"Attempting to speak: {text[:30]}{'...' if len(text) > 30 else ''}")
                        result = coda.speak_response(text)

                        if result.get("error"):
                            log_message(window, f"Error speaking response: {result['error']}", "ERROR")
                        elif result.get("success", False):
                            if values['-SHOW_TIMING-']:
                                tts_time = result["timings"].get("tts_time", 0)
                                log_message(window, f"Speech synthesized in {tts_time:.2f} seconds")
                        else:
                            log_message(window, "Speech synthesis failed", "WARNING")
                    except Exception as e:
                        import traceback
                        error_traceback = traceback.format_exc()
                        log_message(window, f"Error in speak thread: {e}", "ERROR")
                        log_message(window, f"Traceback: {error_traceback}", "ERROR")
                    finally:
                        window['-STATUS-'].update('Ready')

                threading.Thread(target=speak_thread, daemon=True).start()
            else:
                log_message(window, "No response to speak", "WARNING")

        # Copy button
        elif event == '-COPY-':
            text = values['-RESPONSE-'].strip()
            if text:
                window.TKroot.clipboard_clear()
                window.TKroot.clipboard_append(text)
                log_message(window, "Response copied to clipboard")
            else:
                log_message(window, "No response to copy", "WARNING")

        # Clear buttons
        elif event == '-CLEAR_INPUT-':
            window['-INPUT-'].update('')

        elif event == '-CLEAR_RESPONSE-':
            window['-RESPONSE-'].update('')

        elif event == '-CLEAR_LOG-':
            window['-LOG-'].update('')

        elif event == '-CLEAR_CONV-':
            if coda:
                coda.clear_conversation()
                log_message(window, "Conversation history cleared")

        # Save conversation
        elif event == '-SAVE-':
            if coda:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                file_path = f"data/conversations/conversation_{timestamp}.json"

                if coda.save_conversation(file_path):
                    log_message(window, f"Conversation saved to {file_path}")
                else:
                    log_message(window, "Error saving conversation", "ERROR")

    # Close the window
    window.close()

if __name__ == "__main__":
    # Create data directories
    os.makedirs("data/conversations", exist_ok=True)

    # Run the GUI
    main()
