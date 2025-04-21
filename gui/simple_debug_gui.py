#!/usr/bin/env python3
"""
Coda Lite - Simple Debug GUI
A lightweight debug GUI for testing PySimpleGUI functionality.
"""

import os
import sys
import time
import logging
from datetime import datetime
from pathlib import Path

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

class MockLLM:
    """Mock LLM class for testing."""
    
    def chat(self, messages, temperature=0.7, max_tokens=256, **kwargs):
        """Mock chat method."""
        user_message = next((m["content"] for m in messages if m["role"] == "user"), "")
        return f"This is a mock response to: '{user_message}'\nTemperature: {temperature}, Max tokens: {max_tokens}"

class MockTTS:
    """Mock TTS class for testing."""
    
    def synthesize(self, text, **kwargs):
        """Mock synthesize method."""
        print(f"\n[TTS WOULD SAY]: {text}\n")
        return True

class SimpleCodaWrapper:
    """Simple wrapper for testing the GUI."""
    
    def __init__(self):
        """Initialize the simple wrapper."""
        self.llm = MockLLM()
        self.tts = MockTTS()
        self.conversation_history = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]
        logger.info("Simple Coda wrapper initialized")
    
    def process_input(self, text, temperature=0.7, max_tokens=256):
        """Process user input and generate a response."""
        if not text.strip():
            return {"response": "", "error": "Empty input", "timings": {}}
        
        # Add user message to conversation history
        self.conversation_history.append({"role": "user", "content": text})
        
        # Generate response
        try:
            start_time = time.time()
            response = self.llm.chat(
                messages=self.conversation_history,
                temperature=temperature,
                max_tokens=max_tokens
            )
            end_time = time.time()
            
            # Add assistant message to conversation history
            self.conversation_history.append({"role": "assistant", "content": response})
            
            return {
                "response": response,
                "error": None,
                "timings": {"llm_time": end_time - start_time}
            }
        except Exception as e:
            logger.error(f"Error generating response: {e}")
            return {
                "response": "",
                "error": str(e),
                "timings": {}
            }
    
    def speak_response(self, text):
        """Speak the response using TTS."""
        if not text.strip():
            return {"error": "Empty text", "timings": {}}
        
        try:
            start_time = time.time()
            self.tts.synthesize(text)
            end_time = time.time()
            
            return {
                "error": None,
                "timings": {"tts_time": end_time - start_time}
            }
        except Exception as e:
            logger.error(f"Error speaking response: {e}")
            return {
                "error": str(e),
                "timings": {}
            }
    
    def clear_conversation(self):
        """Clear the conversation history except for the system prompt."""
        self.conversation_history = [self.conversation_history[0]]

def create_gui():
    """Create the PySimpleGUI interface."""
    # Set theme
    sg.theme('DarkBlue3')
    
    # Define layout
    layout = [
        [sg.Text('Coda Lite - Simple Debug GUI', font=('Helvetica', 16))],
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
    window = sg.Window('Coda Lite - Simple Debug GUI', layout, finalize=True, resizable=True)
    
    return window

def log_message(window, message, level="INFO"):
    """Add a message to the log window."""
    timestamp = datetime.now().strftime("%H:%M:%S")
    log_entry = f"[{timestamp}] [{level}] {message}\n"
    
    # Update the log element
    current_log = window['-LOG-'].get()
    window['-LOG-'].update(current_log + log_entry)

def main():
    """Main entry point for the simple debug GUI."""
    # Create the GUI
    window = create_gui()
    
    # Initialize the simple wrapper
    try:
        coda = SimpleCodaWrapper()
        log_message(window, "Simple Coda wrapper initialized successfully")
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        log_message(window, f"Error initializing Simple Coda wrapper: {e}", "ERROR")
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
                
                # Process input
                window['-STATUS-'].update('Processing...')
                window.refresh()
                
                result = coda.process_input(text, temperature, max_tokens)
                
                # Update response
                if result["error"]:
                    window['-RESPONSE-'].update(f"Error: {result['error']}")
                    log_message(window, f"Error generating response: {result['error']}", "ERROR")
                else:
                    window['-RESPONSE-'].update(result["response"])
                    
                    # Log timing information
                    if values['-SHOW_TIMING-']:
                        llm_time = result["timings"].get("llm_time", 0)
                        log_message(window, f"Response generated in {llm_time:.2f} seconds")
                    
                    # Auto-speak if enabled
                    if values['-AUTO_SPEAK-']:
                        window['-STATUS-'].update('Speaking...')
                        window.refresh()
                        
                        speak_result = coda.speak_response(result["response"])
                        
                        if speak_result["error"]:
                            log_message(window, f"Error speaking response: {speak_result['error']}", "ERROR")
                        elif values['-SHOW_TIMING-']:
                            tts_time = speak_result["timings"].get("tts_time", 0)
                            log_message(window, f"Speech synthesized in {tts_time:.2f} seconds")
                
                window['-STATUS-'].update('Ready')
            else:
                log_message(window, "Empty input", "WARNING")
        
        # Speak button
        elif event == '-SPEAK-':
            text = values['-RESPONSE-'].strip()
            if text:
                window['-STATUS-'].update('Speaking...')
                window.refresh()
                
                speak_result = coda.speak_response(text)
                
                if speak_result["error"]:
                    log_message(window, f"Error speaking response: {speak_result['error']}", "ERROR")
                elif values['-SHOW_TIMING-']:
                    tts_time = speak_result["timings"].get("tts_time", 0)
                    log_message(window, f"Speech synthesized in {tts_time:.2f} seconds")
                
                window['-STATUS-'].update('Ready')
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
    
    # Close the window
    window.close()

if __name__ == "__main__":
    main()
