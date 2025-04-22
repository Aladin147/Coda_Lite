#!/usr/bin/env python3
"""
Coda Lite - Core Operations & Digital Assistant (v0.0.2)
Main entry point for the Coda Lite voice assistant.

This module initializes and coordinates the core components:
- Speech-to-Text (STT)
- Language Model (LLM)
- Text-to-Speech (TTS)
- Tool execution

Current version (v0.0.2) implements the optimized voice loop with memory, personality, and tool calling.
"""

import os
import sys
import time
import logging
import signal
import threading
import random
import json
from datetime import datetime
from typing import List, Dict
from queue import Queue

from personality import PersonalityLoader
from memory import MemoryManager
from tools import get_tool_router
from tools.basic_tools import set_memory_manager

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
    os.makedirs("data/memory", exist_ok=True)

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

    def summarize_tool_result(self, original_query: str, tool_result: str) -> str:
        """Helper function to summarize a tool result in a natural way.

        Args:
            original_query: The original user query that triggered the tool call
            tool_result: The result from the tool execution

        Returns:
            A natural language summary of the tool result
        """
        logger.info(f"Summarizing tool result: {tool_result} for query: {original_query}")

        # Create a brand new context for the second pass
        messages = [
            {"role": "system", "content": "You are Coda, a helpful voice assistant. Do NOT output JSON or tool instructions."},
            {"role": "system", "content": f"The user asked: '{original_query}'"},
            {"role": "system", "content": f"The tool result is: {tool_result}"},
            {"role": "system", "content": "Now rephrase the result naturally in a friendly tone. Keep it brief and conversational. Do not mention that you used a tool or function."},
            {"role": "user", "content": "Please respond to my question using this information."}
        ]

        # Log the messages for debugging
        logger.info("Summarization messages:")
        for i, msg in enumerate(messages):
            logger.info(f"  Message {i}: role={msg['role']}, content={msg['content']}")

        # Generate a natural language summary
        summary = self.llm.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=256,
            stream=False
        )

        logger.info(f"Generated summary: {summary}")
        return summary

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

        # Initialize personality
        logger.info("Initializing personality...")
        self.personality = PersonalityLoader()

        # Generate system prompt from personality
        self.system_prompt = self.personality.generate_system_prompt()
        logger.info("Generated system prompt from personality")

        # Initialize memory manager
        logger.info("Initializing memory manager...")
        max_turns = config.get("memory.max_turns", 20)
        self.memory = MemoryManager(max_turns=max_turns)

        # Initialize tool router
        logger.info("Initializing tool router...")
        self.tool_router = get_tool_router()

        # Set memory manager reference for tools
        set_memory_manager(self.memory)
        logger.info("Set memory manager reference for tools")

        # Add system message to memory
        self.memory.add_turn("system", self.system_prompt)
        logger.info("Added system prompt to memory")

        # Add system message to conversation history (legacy)
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
            # Add user input to memory
            self.memory.add_turn("user", text)
            logger.info("Added user input to memory")

            # Get conversation context from memory
            max_tokens = self.config.get("memory.max_tokens", 800)
            context = self.memory.get_context(max_tokens=max_tokens)
            logger.info(f"Retrieved context with {len(context)} turns")

            # Generate initial response from LLM
            start_time = time.time()
            raw_response = self.llm.chat(
                messages=context,
                temperature=self.config.get("llm.temperature", 0.7),
                max_tokens=self.config.get("llm.max_tokens", 256),
                stream=False
            )
            end_time = time.time()

            logger.info(f"Initial LLM response generated in {end_time - start_time:.2f} seconds")
            logger.info(f"Raw LLM response: {raw_response}")

            # Store the original response for debugging
            original_response = raw_response
            response = raw_response

            # Check if the response contains a tool call
            tool_call_info = self.tool_router.extract_tool_call(response)
            if tool_call_info:
                tool_name = tool_call_info.get("name")
                tool_args = tool_call_info.get("args", {})

                logger.info(f"Detected tool call: {tool_name} with args {tool_args}")

                # Execute the tool
                tool_result = self.tool_router.execute_tool(tool_name, tool_args)
                logger.info(f"Tool result: {tool_result}")

                # Add the tool call and result to the conversation context
                augmented_context = context.copy()

                # Add the function call as assistant's response
                augmented_context.append({
                    "role": "assistant",
                    "content": None,
                    "function_call": {
                        "name": tool_name,
                        "arguments": json.dumps(tool_args)
                    }
                })

                # Format the tool result for better readability
                formatted_result = tool_result
                if tool_name == "get_time":
                    formatted_result = f"The current time is {tool_result}"
                elif tool_name == "get_date":
                    formatted_result = f"Today is {tool_result}"
                elif tool_name == "tell_joke":
                    formatted_result = f"Here's a joke: {tool_result}"
                elif tool_name == "list_memory_files":
                    formatted_result = f"Memory files: {tool_result}"
                elif tool_name == "count_conversation_turns":
                    formatted_result = f"Conversation turns: {tool_result}"

                # Add the function result
                augmented_context.append({
                    "role": "function",
                    "name": tool_name,
                    "content": formatted_result
                })

                # Log the augmented context for debugging
                logger.info(f"Augmented context with tool result, re-running LLM")
                for i, msg in enumerate(augmented_context):
                    role = msg.get("role", "unknown")
                    content = msg.get("content", "")
                    if role == "assistant" and "function_call" in msg:
                        logger.info(f"Context [{i}] - {role} with function_call: {msg['function_call']}")
                    else:
                        logger.info(f"Context [{i}] - {role}: {content[:50]}{'...' if len(content) > 50 else ''}")

                # Use the summarize_tool_result helper function to generate a natural language response
                start_time = time.time()
                logger.info("Using summarize_tool_result helper function for second pass")

                # Get the original user query
                original_query = text  # This is the original user input

                # Generate a natural language summary using a brand new context
                final_response = self.summarize_tool_result(original_query, formatted_result)

                # Log the result
                logger.info(f"Generated natural language summary: {final_response}")
                end_time = time.time()

                logger.info(f"Final LLM response generated in {end_time - start_time:.2f} seconds")
                logger.info(f"Final response: {final_response}")

                # Check if the final response is empty, too short, or contains JSON
                is_json = False
                contains_tool_call = False

                logger.info("Analyzing final response for JSON or tool call patterns")

                # Check for JSON format
                try:
                    # Try to parse the entire response as JSON
                    json_obj = json.loads(final_response)
                    is_json = isinstance(json_obj, dict)
                    contains_tool_call = is_json and "tool_call" in json_obj
                    logger.info(f"Final response is valid JSON: {is_json}, contains tool_call: {contains_tool_call}")

                    # If it's valid JSON, we need to use a fallback
                    logger.warning("Final response is valid JSON, using fallback response")
                    final_response = f"The current {tool_name.replace('get_', '')} is {tool_result}."
                except json.JSONDecodeError:
                    # Not valid JSON, but might contain JSON patterns
                    logger.info("Final response is not valid JSON, checking for JSON patterns")

                    # Check if the response contains a tool_call pattern
                    contains_tool_call = "tool_call" in final_response or ("{" in final_response and "}" in final_response)

                    if contains_tool_call:
                        logger.warning(f"Final response contains JSON-like patterns: {final_response}")

                        # Try to extract just the text part before any JSON
                        if "{" in final_response:
                            text_part = final_response.split("{")[0].strip()
                            logger.info(f"Extracted text part before JSON: '{text_part}'")

                            if text_part and len(text_part) > 5:
                                logger.info(f"Using extracted text part as final response")
                                final_response = text_part
                            else:
                                # If we couldn't extract a meaningful text part, use a fallback
                                logger.warning("Could not extract meaningful text from response with JSON patterns. Using fallback.")
                                final_response = f"The current {tool_name.replace('get_', '')} is {tool_result}."

                # Final check for empty or too short responses
                if not final_response or len(final_response.strip()) < 5:
                    logger.warning("Final response is empty or too short. Using fallback response.")
                    final_response = f"Based on the information I found, {formatted_result}."

                # Add original response and tool call to memory for debugging
                self.memory.add_turn("system", f"Original response: {original_response}")
                self.memory.add_turn("system", f"Tool call: {tool_name}({tool_args})")
                self.memory.add_turn("system", f"Tool result: {tool_result}")
                self.memory.add_turn("system", f"Final response: {final_response}")

                # Log which response is being returned
                logger.info(f"[DEBUG] Using SECOND PASS output: {final_response}")

                # Update the response with the final response from the second pass
                response = final_response
            else:
                # No tool call detected, use the original response
                logger.info("No tool call detected, using original response")

            # Add assistant response to memory
            self.memory.add_turn("assistant", response)
            logger.info("Added assistant response to memory")

            # Add assistant message to conversation history (legacy)
            self.conversation_history.append({"role": "assistant", "content": response})

            # Print the response
            name = self.personality.get_name()
            print(f"\n{name}: {response}")

            # Add the response to the TTS queue
            self.response_queue.put(response)

            # Legacy: Limit conversation history to last 10 messages (plus system prompt)
            if len(self.conversation_history) > 11:  # 1 system + 10 messages
                self.conversation_history = [self.conversation_history[0]] + self.conversation_history[-10:]
        except Exception as e:
            logger.error(f"Error generating response: {e}", exc_info=True)
            error_message = "I'm sorry, I encountered an error while processing your request."
            print(f"\nCoda: {error_message}")
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

        # Add user message to conversation history (legacy)
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
        name = self.personality.get_name()
        welcome_options = [
            f"Hello! I'm {name}, your voice assistant. How can I help you today?",
            f"Hi there! {name} here. What can I do for you?",
            f"Hey! I'm {name}. Ready when you are.",
            f"Greetings! {name} at your service. What do you need?"
        ]
        welcome_message = random.choice(welcome_options)
        print(f"\n{name}: {welcome_message}")
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

        # Export memory to file
        try:
            if hasattr(self, 'memory') and self.memory.get_turn_count() > 1:  # Only export if we have conversation turns
                timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                export_dir = self.config.get("memory.export_dir", "data/memory")
                export_path = f"{export_dir}/session_{timestamp}.json"
                self.memory.export(export_path)
                logger.info(f"Exported memory to {export_path}")
        except Exception as e:
            logger.error(f"Error exporting memory: {e}")

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

def signal_handler(sig, _):
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
