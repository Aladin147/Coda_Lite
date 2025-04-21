#!/usr/bin/env python3
"""
Minimal GUI for testing Coda Lite components
"""

import sys
import time
import logging
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("coda.minimal_gui")

# Import PySimpleGUI
import PySimpleGUI as sg

# Import Coda modules
from llm import OllamaLLM
from tts import create_tts

class MinimalGUI:
    def __init__(self):
        # Set theme
        sg.theme('DarkBlue3')

        # Define layout
        layout = [
            [sg.Text('Coda Lite - Minimal Test GUI', font=('Helvetica', 16))],
            [sg.HorizontalSeparator()],

            # Input section
            [sg.Text('Input:', font=('Helvetica', 11))],
            [sg.Multiline(key='-INPUT-', size=(80, 5), font=('Helvetica', 10))],
            [sg.Button('Send', key='-SEND-', size=(10, 1))],

            [sg.HorizontalSeparator()],

            # Response section
            [sg.Text('Response:', font=('Helvetica', 11))],
            [sg.Multiline(key='-RESPONSE-', size=(80, 10), font=('Helvetica', 10), disabled=True, background_color='#f0f0f0')],
            [sg.Button('Speak', key='-SPEAK-', size=(10, 1))],

            [sg.HorizontalSeparator()],

            # Log section
            [sg.Text('Log:', font=('Helvetica', 11))],
            [sg.Multiline(key='-LOG-', size=(80, 8), font=('Courier', 9), disabled=True, autoscroll=True, background_color='#000000', text_color='#00FF00')],

            # Status bar
            [sg.Text('Status:', size=(6, 1)), sg.Text('Ready', key='-STATUS-', size=(50, 1))],
            [sg.Button('Exit', key='-EXIT-', size=(10, 1))]
        ]

        # Create window
        self.window = sg.Window('Coda Lite - Minimal Test GUI', layout, finalize=True, resizable=True)

        # Initialize components
        self.init_components()

    def init_components(self):
        self.log("Initializing components...")

        # Initialize LLM
        try:
            self.log("Initializing LLM...")
            self.llm = OllamaLLM(
                model_name="llama3",
                host="http://localhost:11434",
                timeout=120
            )
            self.log(f"LLM initialized with model: {self.llm.model_name}")
        except Exception as e:
            self.log(f"Error initializing LLM: {e}", level="ERROR")
            self.llm = None

        # Initialize TTS
        try:
            self.log("Initializing TTS...")
            # Try to create TTS with CSM-1B (MeloTTS)
            try:
                import torch
                device = "cuda" if torch.cuda.is_available() else "cpu"
                self.log(f"Creating CSM-1B TTS on {device}")

                self.tts = create_tts(
                    engine="csm",
                    device=device,
                    language="en"
                )
            except Exception as e:
                self.log(f"Error initializing CSM-1B TTS: {e}", level="ERROR")
                self.log("No TTS available")
                self.tts = None
            self.log("TTS initialized successfully")
        except Exception as e:
            self.log(f"Error initializing TTS: {e}", level="ERROR")
            self.tts = None

        self.log("Components initialized")

    def log(self, message, level="INFO"):
        """Add a message to the log window."""
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] [{level}] {message}\n"

        # Update the log element
        current_log = self.window['-LOG-'].get()
        self.window['-LOG-'].update(current_log + log_entry)

        # Also log to console
        print(log_entry.strip())

        # Log to logger
        if level == "ERROR":
            logger.error(message)
        else:
            logger.info(message)

    def process_input(self, text):
        """Process user input and generate a response."""
        if not text.strip():
            self.log("Empty input", level="WARNING")
            return

        if not self.llm:
            self.log("LLM not initialized", level="ERROR")
            return

        self.window['-STATUS-'].update('Processing...')
        self.window.refresh()

        try:
            self.log(f"Sending to LLM: {text[:50]}{'...' if len(text) > 50 else ''}")

            # We'll use the generate method instead of chat, so we don't need messages

            # Get response from LLM
            start_time = time.time()

            # Use the chat method with stream=True to get chunks
            self.log("Using chat method with stream=True")

            # Format the messages
            messages = [
                {"role": "system", "content": "You are Coda, a helpful voice assistant."},
                {"role": "user", "content": text}
            ]

            # Use the chat method with stream=True
            response_obj = self.llm.chat(
                messages=messages,
                temperature=0.7,
                stream=True
            )

            # Log the raw response for debugging
            self.log(f"Raw response type: {type(response_obj)}")
            self.log(f"Raw response: {response_obj}")

            # Extract the response text
            if isinstance(response_obj, dict):
                response = response_obj.get("response", "")
                self.log(f"Response extracted from dictionary: {response[:50]}{'...' if len(response) > 50 else ''}")
            elif hasattr(response_obj, '__iter__') and hasattr(response_obj, '__next__'):
                # It's a generator, collect all chunks
                self.log("Received streaming response, collecting chunks...")
                response = ""
                try:
                    for chunk in response_obj:
                        if chunk:
                            response += chunk
                            self.log(f"Received chunk: {chunk[:20]}{'...' if len(chunk) > 20 else ''}")
                except Exception as e:
                    self.log(f"Error collecting response chunks: {e}", level="ERROR")
            else:
                # It's a regular string response
                response = str(response_obj)

            end_time = time.time()

            # Update the response box
            if response:
                self.window['-RESPONSE-'].update(response)
                self.log(f"Complete response: {response[:100]}{'...' if len(response) > 100 else ''}")
                self.log(f"Response generated in {end_time - start_time:.2f} seconds")
            else:
                self.window['-RESPONSE-'].update("No response received")
                self.log("No response received from LLM", level="WARNING")

        except Exception as e:
            import traceback
            self.log(f"Error processing input: {e}", level="ERROR")
            self.log(f"Traceback: {traceback.format_exc()}", level="ERROR")

        finally:
            self.window['-STATUS-'].update('Ready')

    def speak_response(self, text):
        """Speak the response using TTS."""
        if not text.strip():
            self.log("No text to speak", level="WARNING")
            return

        if not self.tts:
            self.log("TTS not initialized", level="ERROR")
            return

        self.window['-STATUS-'].update('Speaking...')
        self.window.refresh()

        try:
            self.log(f"Speaking: {text[:50]}{'...' if len(text) > 50 else ''}")

            # Synthesize speech
            start_time = time.time()
            result = self.tts.synthesize(text)
            end_time = time.time()

            self.log(f"Speech synthesized in {end_time - start_time:.2f} seconds")
            self.log(f"TTS result: {result}")

        except Exception as e:
            import traceback
            self.log(f"Error speaking response: {e}", level="ERROR")
            self.log(f"Traceback: {traceback.format_exc()}", level="ERROR")

        finally:
            self.window['-STATUS-'].update('Ready')

    def run(self):
        """Run the GUI event loop."""
        while True:
            event, values = self.window.read()

            if event == sg.WINDOW_CLOSED or event == '-EXIT-':
                break

            elif event == '-SEND-':
                text = values['-INPUT-'].strip()
                if text:
                    self.process_input(text)

            elif event == '-SPEAK-':
                text = values['-RESPONSE-'].strip()
                if text:
                    self.speak_response(text)

        self.window.close()

if __name__ == "__main__":
    gui = MinimalGUI()
    gui.run()
