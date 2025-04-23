#!/usr/bin/env python3
"""
Coda Lite - Core Operations & Digital Assistant with WebSocket Integration
Main entry point for the Coda Lite voice assistant with WebSocket support.

This module initializes and coordinates the core components:
- Speech-to-Text (STT) with WebSocket events
- Language Model (LLM) with WebSocket events
- Text-to-Speech (TTS) with WebSocket events
- Tool execution with WebSocket events
- Memory management with WebSocket events
- Personality engine
- Intent routing
- Feedback system
- WebSocket server for real-time monitoring

See version.py for current version information.
"""

import os
import sys
import time
import logging
import signal
import threading
import random
import json
import re
import asyncio
from datetime import datetime
from typing import List, Dict
from queue import Queue

from version import __version__, __version_name__, get_full_version_string

from personality import PersonalityLoader, AdvancedPersonalityManager
from memory import MemoryManager, EnhancedMemoryManager
from tools import get_tool_router
from tools.basic_tools import set_memory_manager
from tools.memory_tools import set_memory_manager as set_memory_tools_manager
from intent import IntentManager
from feedback import FeedbackManager

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

# Log version information
logger.info(get_full_version_string())

# Import modules
from config.config_loader import ConfigLoader
from stt import WebSocketWhisperSTT
from llm import WebSocketOllamaLLM
from tts.factory import get_tts_instance, get_available_tts_engines
from memory import WebSocketEnhancedMemoryManager, MemoryManager
from websocket import CodaWebSocketServer, CodaWebSocketIntegration
from websocket.perf_integration import WebSocketPerfIntegration

# Type definitions for conversation history
Message = Dict[str, str]
MessageList = List[Message]

# Global variables
assistant = None
websocket_server = None
websocket_integration = None
perf_integration = None

def extract_clean_response(response: str) -> str:
    """Remove any JSON blocks and clean up the response.

    Args:
        response: The response string that might contain JSON

    Returns:
        A cleaned response with JSON blocks removed
    """
    # First, try to find natural language after JSON
    json_end = max(response.rfind('}'), response.rfind(']'))
    if json_end > 0 and json_end < len(response) - 1:
        # There's text after the JSON, use that
        natural_text = response[json_end+1:].strip()
        if len(natural_text) > 5:
            response = natural_text

    # Remove any JSON blocks (ultra-aggressive pattern)
    response = re.sub(r'\[.*?\]', '', response, flags=re.DOTALL)  # Remove array blocks
    response = re.sub(r'\{.*?"tool_call".*?\}', '', response, flags=re.DOTALL)  # Remove tool_call blocks
    response = re.sub(r'\{.*?\}', '', response, flags=re.DOTALL)  # Remove any remaining JSON objects

    # Remove any trailing/leading whitespace and normalize spacing
    response = response.strip()
    response = re.sub(r'\s+', ' ', response)

    # Remove any tool-related mentions
    response = re.sub(r'tool_call', '', response, flags=re.IGNORECASE)
    response = re.sub(r'tool result', '', response, flags=re.IGNORECASE)
    response = re.sub(r'according to the tool', '', response, flags=re.IGNORECASE)
    response = re.sub(r'the tool says', '', response, flags=re.IGNORECASE)
    response = re.sub(r'based on the tool', '', response, flags=re.IGNORECASE)

    # Remove phrases like "Let me check" or "I found that"
    response = re.sub(r'let me check', '', response, flags=re.IGNORECASE)
    response = re.sub(r'i found that', '', response, flags=re.IGNORECASE)
    response = re.sub(r'i can tell you that', '', response, flags=re.IGNORECASE)
    response = re.sub(r'i need to use a tool', '', response, flags=re.IGNORECASE)
    response = re.sub(r'i\'ll check', '', response, flags=re.IGNORECASE)

    # Clean up any double spaces or punctuation issues from the removals
    response = re.sub(r'\s+', ' ', response)  # Normalize spaces again
    response = re.sub(r'\s+\.', '.', response)  # Fix spaces before periods
    response = re.sub(r'^[,\.\s]+', '', response)  # Remove leading punctuation
    response = re.sub(r'\s+$', '', response)  # Remove trailing spaces

    # If the response is too short after cleaning, return a generic message
    if len(response) < 5:
        return "I'm sorry, I couldn't process that properly."

    return response

def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/audio", exist_ok=True)
    os.makedirs("data/temp", exist_ok=True)
    os.makedirs("data/memory", exist_ok=True)
    os.makedirs("data/memory/long_term", exist_ok=True)

def load_system_prompt(file_path: str) -> str:
    """Load system prompt from file."""
    try:
        with open(file_path, 'r') as f:
            return f.read().strip()
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        return "You are Coda, a helpful voice assistant running locally on the user's computer."

class CodaAssistant:
    """Main Coda Lite assistant class with WebSocket integration."""

    def __init__(self, config: ConfigLoader, websocket_integration: CodaWebSocketIntegration, perf_integration: WebSocketPerfIntegration):
        """Initialize the Coda assistant with WebSocket integration."""
        self.config = config
        self.conversation_history: MessageList = []
        self.running = True
        self.processing = False  # Flag to track if we're currently processing a request
        self.response_queue = Queue()  # Queue for responses to be spoken
        self.ws = websocket_integration
        self.perf = perf_integration

        # Start a new session
        self.ws.start_session()

        # Send system information
        self.perf.send_system_info()

        # Initialize STT module with WebSocket integration
        logger.info("Initializing Speech-to-Text module with WebSocket integration...")
        self.stt = WebSocketWhisperSTT(
            websocket_integration=self.ws,
            model_size=config.get("stt.model_size", "base"),
            device=config.get("stt.device", "cuda"),
            compute_type=config.get("stt.compute_type", "float16"),
            language=config.get("stt.language", "en"),
            vad_filter=True
        )

        # Initialize LLM module with WebSocket integration
        logger.info("Initializing Language Model module with WebSocket integration...")
        self.llm = WebSocketOllamaLLM(
            websocket_integration=self.ws,
            model_name=config.get("llm.model_name", "llama3"),
            host="http://localhost:11434",
            timeout=120
        )

        # Initialize TTS module with WebSocket integration
        logger.info("Initializing Text-to-Speech module with WebSocket integration...")

        # Use ElevenLabs TTS as requested by the user
        tts_engine = config.get("tts.engine", "elevenlabs")

        # Get available TTS engines
        available_engines = get_available_tts_engines()
        logger.info(f"Available TTS engines: {available_engines}")

        # Check if the requested engine is available
        if tts_engine not in available_engines or not available_engines[tts_engine]:
            logger.warning(f"Requested TTS engine '{tts_engine}' is not available. Falling back to ElevenLabs.")
            tts_engine = "elevenlabs"

        try:
            # Initialize TTS with lazy loading
            self.tts = get_tts_instance(
                tts_type=tts_engine,
                websocket_integration=self.ws,
                config=config.get_all()
            )

            if tts_engine == "elevenlabs":
                logger.info(f"Initialized ElevenLabs TTS with voice: {config.get('tts.elevenlabs_voice_id', '21m00Tcm4TlvDq8ikWAM')}")
            elif tts_engine == "csm":
                logger.info(f"Initialized CSM TTS with language: {config.get('tts.language', 'EN')}")
            elif tts_engine == "dia":
                logger.info(f"Initialized Dia TTS with model: {config.get('tts.dia_model_path', 'default')}")
        except Exception as e:
            logger.error(f"Error initializing TTS engine '{tts_engine}': {e}")
            logger.info("Falling back to ElevenLabs TTS")

            # Fallback to ElevenLabs TTS
            self.tts = get_tts_instance(
                tts_type="elevenlabs",
                websocket_integration=self.ws,
                config=config.get_all()
            )
            logger.info(f"Initialized ElevenLabs TTS with voice: {config.get('tts.elevenlabs_voice_id', '21m00Tcm4TlvDq8ikWAM')}")

        # Initialize personality
        logger.info("Initializing personality...")
        self.personality = PersonalityLoader()

        # Initialize advanced personality manager if enabled
        use_advanced_personality = config.get("personality.use_advanced", False)
        if use_advanced_personality:
            logger.info("Initializing advanced personality manager...")
            self.advanced_personality = AdvancedPersonalityManager(
                memory_manager=None,  # Will be set after memory manager is initialized
                config=config.get_all()
            )
        else:
            self.advanced_personality = None

        # Generate system prompts from personality
        self.system_prompt = self.personality.generate_system_prompt("tool_detection")
        self.summarization_prompt = self.personality.generate_system_prompt("summarization")
        logger.info("Generated system prompts from personality")

        # Initialize memory manager with WebSocket integration
        logger.info("Initializing memory manager with WebSocket integration...")
        long_term_enabled = config.get("memory.long_term_enabled", False)

        if long_term_enabled:
            logger.info("Using enhanced memory manager with long-term memory and WebSocket integration")
            self.memory = WebSocketEnhancedMemoryManager(
                websocket_integration=self.ws,
                config=config.get_all()
            )
        else:
            logger.info("Using standard short-term memory manager (without WebSocket integration)")
            max_turns = config.get("memory.max_turns", 20)
            self.memory = MemoryManager(max_turns=max_turns)

        # Initialize tool router
        logger.info("Initializing tool router...")
        self.tool_router = get_tool_router()

        # Set memory manager reference for tools
        set_memory_manager(self.memory)
        set_memory_tools_manager(self.memory)
        logger.info("Set memory manager reference for tools")

        # Set memory manager for advanced personality manager if enabled
        if self.advanced_personality:
            self.advanced_personality.memory_manager = self.memory
            logger.info("Set memory manager for advanced personality manager")

        # Add tool descriptions to the system prompt (only for tool detection)
        tool_descriptions = self.tool_router.format_tool_descriptions(include_json_format=True)
        self.system_prompt += f"\n\n{tool_descriptions}"

        # Add system message to memory
        self.memory.add_turn("system", self.system_prompt)
        logger.info("Added system prompt to memory")

        # Add system message to conversation history (legacy)
        self.conversation_history.append({"role": "system", "content": self.system_prompt})

        # Initialize intent manager if enabled
        intent_enabled = config.get("intent.enabled", False)
        if intent_enabled:
            logger.info("Initializing intent manager...")
            self.intent_manager = IntentManager(
                memory_manager=self.memory,
                tool_router=self.tool_router,
                personality_manager=self.advanced_personality
            )

            # Set debug mode if configured
            debug_mode = config.get("intent.debug_mode", False)
            if debug_mode:
                self.intent_manager.set_debug_mode(True)
                logger.info("Intent manager debug mode enabled")

            logger.info("Intent manager initialized")
        else:
            self.intent_manager = None
            logger.info("Intent routing disabled")

        # Initialize feedback manager if enabled
        feedback_enabled = config.get("feedback.enabled", False)
        if feedback_enabled:
            logger.info("Initializing feedback manager...")
            self.feedback_manager = FeedbackManager(
                memory_manager=self.memory,
                personality_manager=self.advanced_personality,
                config=config.get_all()
            )

            # Connect feedback manager to personality manager
            if self.advanced_personality:
                self.advanced_personality.feedback_manager = self.feedback_manager
                logger.info("Connected feedback manager to personality manager")

            logger.info("Feedback manager initialized")
        else:
            self.feedback_manager = None
            logger.info("Feedback hooks disabled")

        # Start the TTS worker thread
        self.tts_thread = threading.Thread(target=self._tts_worker, daemon=True)
        self.tts_thread.start()

        logger.info("Coda assistant initialized successfully")

    def summarize_tool_result(self, original_query: str, tool_result: str) -> str:
        """Helper function to summarize a tool result in a natural way.

        Args:
            original_query: The original user query that triggered the tool call
            tool_result: The result from the tool execution

        Returns:
            A natural language summary of the tool result
        """
        logger.info(f"Summarizing tool result: {tool_result} for query: {original_query}")

        # Create a brand new context for the second pass using the dedicated summarization prompt
        messages = [
            {"role": "system", "content": self.summarization_prompt},
            {"role": "system", "content": f"[TOOL RESULT] {tool_result}"},
            {"role": "user", "content": original_query}
        ]

        # Log the messages for debugging
        logger.info("Summarization messages:")
        for i, msg in enumerate(messages):
            logger.info(f"  Message {i}: role={msg['role']}, content={msg['content']}")

        # Signal start of LLM processing
        self.ws.llm_start(
            model=self.config.get("llm.model_name", "llama3"),
            prompt_tokens=sum(len(msg["content"]) for msg in messages) // 4,  # Rough estimate
            system_prompt_preview=self.summarization_prompt[:100] + "..."
        )

        # Generate a natural language summary
        logger.info("Generating summarization response...")
        summary = ""
        token_index = 0
        for chunk in self.llm.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=256,
            stream=True
        ):
            summary += chunk

            # Send token event
            self.ws.llm_token(chunk, token_index)
            token_index += 1

        # Send LLM result event
        self.ws.llm_result(
            text=summary,
            total_tokens=token_index,
            has_tool_calls=False
        )

        logger.info(f"Generated summary: {summary}")
        return summary

    def _tts_worker(self):
        """Worker thread for TTS processing."""
        while self.running:
            try:
                # Get the next response from the queue (blocking with timeout)
                try:
                    response = self.response_queue.get(timeout=0.5)
                except Exception:  # Queue.Empty
                    continue

                # Mark the start of TTS processing
                self.perf.mark_component("tts", "speak", start=True)

                # Speak the response
                # WebSocket events are handled by the WebSocketElevenLabsTTS class
                self.tts.speak(response)

                # Mark the end of TTS processing
                self.perf.mark_component("tts", "speak", start=False)

                # Mark the task as done
                self.response_queue.task_done()

                # Send latency trace after TTS completes
                self.perf.send_latency_trace()
            except Exception as e:
                logger.error(f"Error in TTS worker: {e}", exc_info=True)

                # Mark the end of TTS processing (even though it failed)
                self.perf.mark_component("tts", "speak", start=False)

    def _process_user_input(self, text: str):
        """Process user input in a separate thread."""
        try:
            # Mark the start of processing
            self.perf.mark_component("assistant", "process_input", start=True)

            # Add user input to memory
            self.memory.add_turn("user", text)
            logger.info("Added user input to memory")

            # Check if this is a response to a feedback prompt
            if self.feedback_manager and self.feedback_manager.active_feedback_request:
                if self.feedback_manager.is_feedback_response(text):
                    logger.info("Processing feedback response")
                    feedback_result = self.feedback_manager.process_feedback_response(text)

                    if feedback_result.get("processed", False):
                        # Add a simple acknowledgment to the conversation
                        acknowledgment = "Thanks for your feedback!"
                        self.memory.add_turn("assistant", acknowledgment)

                        # Queue the response for TTS
                        self.response_queue.put(acknowledgment)

                        # We're done processing this input
                        self.processing = False
                        return

            # Process through intent manager if available
            intent_result = None
            if self.intent_manager:
                logger.info("Processing through intent manager")
                intent_result = self.intent_manager.process_input(text)
                logger.info(f"Intent detected: {intent_result.get('intent_type').name if intent_result else 'None'}")

                # Check if the intent was handled and requires special processing
                if intent_result and intent_result.get('handled', False):
                    action = intent_result.get('action')
                    logger.info(f"Intent handled with action: {action}")

                    # For system commands, we might want to return immediately
                    if action == 'system_command':
                        command = intent_result.get('command')
                        message = intent_result.get('message')
                        logger.info(f"Executed system command: {command} - {message}")

                        # Add the result to memory
                        self.memory.add_turn("assistant", message)

                        # Queue the response for TTS
                        self.response_queue.put(message)

                        # For some commands, we might want to return immediately
                        if command in ['debug_on', 'debug_off', 'help']:
                            self.processing = False
                            return

                    # For memory store, we might want to acknowledge
                    elif action == 'memory_store':
                        message = intent_result.get('message')
                        logger.info(f"Stored memory: {message}")

                        # Add the result to memory
                        self.memory.add_turn("assistant", message)

                        # Queue the response for TTS
                        self.response_queue.put(message)
                        self.processing = False
                        return

                    # For memory recall, we might want to present the results
                    elif action == 'memory_recall':
                        message = intent_result.get('message')
                        memories = intent_result.get('memories', [])
                        logger.info(f"Recalled memories: {len(memories)}")

                        # If we have memories, format them nicely
                        if memories and len(memories) > 0:
                            memory_text = "\n".join([f"- {memory.get('content', '')}" for memory in memories])
                            message = f"Here's what I remember about that:\n{memory_text}"

                        # Add the result to memory
                        self.memory.add_turn("assistant", message)

                        # Queue the response for TTS
                        self.response_queue.put(message)
                        self.processing = False
                        return

                    # For personality adjustment, acknowledge the change
                    elif action == 'personality_adjustment':
                        message = intent_result.get('message')
                        parameter = intent_result.get('parameter')
                        new_value = intent_result.get('new_value')
                        logger.info(f"Adjusted personality parameter {parameter} to {new_value}")

                        # Add the result to memory
                        self.memory.add_turn("assistant", message)

                        # Queue the response for TTS
                        self.response_queue.put(message)
                        self.processing = False
                        return

            # Get conversation context from memory
            self.perf.mark_component("memory", "get_context", start=True)
            max_tokens = self.config.get("memory.max_tokens", 800)

            # Use enhanced context if we have an EnhancedMemoryManager
            if isinstance(self.memory, EnhancedMemoryManager):
                context = self.memory.get_enhanced_context(text, max_tokens=max_tokens)
                logger.info(f"Retrieved enhanced context with {len(context)} turns (including long-term memories)")

                # Send memory retrieve event if memories were retrieved
                if hasattr(self.memory, 'last_retrieved_memories') and self.memory.last_retrieved_memories:
                    self.ws.memory_retrieve(
                        query=text,
                        results=self.memory.last_retrieved_memories
                    )
            else:
                context = self.memory.get_context(max_tokens=max_tokens)
                logger.info(f"Retrieved context with {len(context)} turns")

            self.perf.mark_component("memory", "get_context", start=False)

            # Signal start of LLM processing
            self.ws.llm_start(
                model=self.config.get("llm.model_name", "llama3"),
                prompt_tokens=sum(len(msg["content"]) for msg in context) // 4,  # Rough estimate
                system_prompt_preview=self.system_prompt[:100] + "..."
            )

            # Generate initial response from LLM
            self.perf.mark_component("llm", "generate_response", start=True)
            start_time = time.time()
            logger.info("Generating initial LLM response...")
            raw_response = ""
            token_index = 0
            for chunk in self.llm.chat(
                messages=context,
                temperature=self.config.get("llm.temperature", 0.7),
                max_tokens=self.config.get("llm.max_tokens", 256),
                stream=True
            ):
                raw_response += chunk

                # Send token event
                self.ws.llm_token(chunk, token_index)
                token_index += 1

            end_time = time.time()
            self.perf.mark_component("llm", "generate_response", start=False)

            logger.info(f"Initial LLM response generated in {end_time - start_time:.2f} seconds")
            logger.info(f"Raw LLM response: {raw_response}")

            # Store the original response for debugging if needed
            # original_response = raw_response
            response = raw_response

            # Check if the response contains a tool call
            tool_call_info = self.tool_router.extract_tool_call(response)
            if tool_call_info:
                tool_name = tool_call_info.get("name")
                tool_args = tool_call_info.get("args", {})

                logger.info(f"Detected tool call: {tool_name} with args {tool_args}")

                # Signal tool call
                self.ws.tool_call(tool_name, tool_args)

                # Execute the tool
                logger.info(f"Executing tool: {tool_name} with args: {tool_args}")

                # Track the tool usage in memory manager if it's an EnhancedMemoryManager
                if isinstance(self.memory, EnhancedMemoryManager):
                    self.memory.set_last_tool_used(tool_name)
                    logger.info(f"Tracked tool usage in memory: {tool_name}")

                try:
                    # Force real-time values for time and date tools
                    if tool_name == "get_time":
                        tool_result = datetime.now().strftime("It's %H:%M.")
                        logger.info(f"Using real-time value for get_time: {tool_result}")
                    elif tool_name == "get_date":
                        tool_result = datetime.now().strftime("Today is %A, %B %d, %Y.")
                        logger.info(f"Using real-time value for get_date: {tool_result}")
                    else:
                        # For other tools, use the tool router
                        tool_result = self.tool_router.execute_tool(tool_name, tool_args)
                        logger.info(f"Tool result from router: {tool_result}")

                    # Signal tool result
                    self.ws.tool_result(tool_name, tool_result)

                    # Now, generate a natural language response based on the tool result
                    logger.info("Generating natural language response from tool result...")
                    response = self.summarize_tool_result(text, tool_result)
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}", exc_info=True)

                    # Signal tool error
                    self.ws.tool_error(tool_name, str(e))

                    response = f"I'm sorry, I encountered an error while trying to {tool_name}: {str(e)}"
            else:
                # Send LLM result event
                self.ws.llm_result(
                    text=raw_response,
                    total_tokens=token_index,
                    has_tool_calls=False
                )

            # Clean up the response
            clean_response = extract_clean_response(response)
            logger.info(f"Clean response: {clean_response}")

            # Add the response to memory
            self.memory.add_turn("assistant", clean_response)
            logger.info("Added assistant response to memory")

            # Add the response to conversation history (legacy)
            self.conversation_history.append({"role": "assistant", "content": clean_response})

            # Queue the response for TTS
            self.response_queue.put(clean_response)
            logger.info("Queued response for TTS")

            # Check if we should request feedback
            if self.feedback_manager and self.feedback_manager.should_request_feedback():
                logger.info("Requesting feedback")
                feedback_request = self.feedback_manager.generate_feedback_request()
                if feedback_request:
                    # Queue the feedback request for TTS
                    self.response_queue.put(feedback_request)
                    logger.info(f"Queued feedback request for TTS: {feedback_request}")

            # We're done processing this input
            self.processing = False

            # Mark the end of processing
            self.perf.mark_component("assistant", "process_input", start=False)

            # Send component stats
            self.perf.send_component_stats()
        except Exception as e:
            logger.error(f"Error processing user input: {e}", exc_info=True)

            # Signal LLM error
            self.ws.llm_error(str(e))

            # Add an error message to memory
            error_message = f"I'm sorry, I encountered an error: {str(e)}"
            self.memory.add_turn("assistant", error_message)

            # Queue the error message for TTS
            self.response_queue.put(error_message)

            # We're done processing this input
            self.processing = False

            # Mark the end of processing (even though it failed)
            self.perf.mark_component("assistant", "process_input", start=False)

    def handle_transcription(self, text: str) -> None:
        """Handle transcribed text from STT."""
        # Mark the start of STT handling
        self.perf.mark_component("stt", "handle_transcription", start=True)

        if not text.strip():
            logger.info("Empty transcription, ignoring")
            # Mark the end of STT handling (early return)
            self.perf.mark_component("stt", "handle_transcription", start=False)
            return

        # If we're already processing a request, ignore this one
        if self.processing:
            logger.info("Already processing a request, ignoring")
            # Mark the end of STT handling (early return)
            self.perf.mark_component("stt", "handle_transcription", start=False)
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

        # Mark the end of STT handling
        self.perf.mark_component("stt", "handle_transcription", start=False)

    def run(self) -> None:
        """Run the conversation loop."""
        # Get the name from the personality
        name = self.personality.get_name()
        logger.info(f"Starting conversation loop with name: {name}")

        # Welcome message
        welcome_options = [
            f"Hello, I'm {name}. How can I help you today?",
            f"Hi there! I'm {name}, your voice assistant. What can I do for you?",
            f"Welcome! I'm {name}. I'm here to assist you. What would you like to know?",
            f"Greetings! I'm {name}, ready to help. What can I do for you today?",
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

    def should_stop(self) -> bool:
        """Check if the conversation loop should stop."""
        return not self.running

    def cleanup(self) -> None:
        """Clean up resources."""
        logger.info("Cleaning up resources")

        # End the WebSocket session
        self.ws.end_session()

        # Close the STT module
        if hasattr(self, 'stt') and self.stt:
            self.stt.close()
            logger.info("Closed STT module")

        # Close the TTS module
        if hasattr(self, 'tts') and self.tts:
            # Try to close the TTS module
            try:
                # First try the close method if it exists
                if hasattr(self.tts, 'close'):
                    self.tts.close()
                    logger.info("Closed TTS module using close() method")
                # Then try the unload method if it exists
                elif hasattr(self.tts, 'unload'):
                    self.tts.unload()
                    logger.info("Closed TTS module using unload() method")
            except Exception as e:
                logger.warning(f"Error closing TTS module: {e}")

            # Use the factory's unload function to ensure proper cleanup
            from tts.factory import unload_current_tts
            unload_current_tts()
            logger.info("Unloaded TTS module using factory")

        # Close the memory manager
        if hasattr(self, 'memory') and self.memory:
            if hasattr(self.memory, 'close'):
                self.memory.close()
                logger.info("Closed memory manager")

        logger.info("Cleanup complete")

def signal_handler(sig, _):
    """Handle signals for graceful shutdown."""
    global assistant, websocket_server, perf_integration

    logger.info(f"Received signal {sig}, shutting down...")

    if assistant:
        assistant.stop()

    # Stop performance monitoring
    if perf_integration:
        perf_integration.get_tracker().stop_monitoring()

    # Schedule the WebSocket server to stop
    if websocket_server:
        asyncio.create_task(websocket_server.stop())

async def main_async():
    """Async main entry point for Coda Lite."""
    global assistant, websocket_server, websocket_integration, perf_integration

    logger.info(f"Starting Coda Lite {__version__} ({__version_name__})")
    ensure_directories()

    # Set up signal handlers for graceful shutdown
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    # Load configuration
    config = ConfigLoader()

    try:
        # Initialize WebSocket server
        logger.info("Initializing WebSocket server...")
        websocket_server = CodaWebSocketServer(
            host=config.get("websocket.host", "localhost"),
            port=config.get("websocket.port", 8765)
        )

        # Initialize WebSocket integration
        logger.info("Initializing WebSocket integration...")
        websocket_integration = CodaWebSocketIntegration(websocket_server)

        # Initialize performance integration
        logger.info("Initializing performance tracking...")
        perf_integration = WebSocketPerfIntegration(
            server=websocket_server,
            monitoring_interval=config.get("performance.monitoring_interval", 5.0)
        )

        # Start the WebSocket server
        await websocket_server.start()
        logger.info("WebSocket server started")

        # Initialize and run the assistant
        assistant = CodaAssistant(config, websocket_integration, perf_integration)
        logger.info("Coda Lite is ready. Press Ctrl+C to exit.")

        # Run the assistant in a separate thread
        assistant_thread = threading.Thread(target=assistant.run, daemon=True)
        assistant_thread.start()

        # Keep the main thread alive
        while assistant.running:
            await asyncio.sleep(1)

    except Exception as e:
        logger.error(f"Error in main: {e}", exc_info=True)
    finally:
        # Stop the WebSocket server
        if websocket_server:
            await websocket_server.stop()
            logger.info("WebSocket server stopped")

        logger.info("Coda Lite shutdown complete. Goodbye!")

def main():
    """Main entry point for Coda Lite."""
    asyncio.run(main_async())

if __name__ == "__main__":
    main()
