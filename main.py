#!/usr/bin/env python3
"""
Coda Lite - Core Operations & Digital Assistant
Main entry point for the Coda Lite voice assistant.

This module initializes and coordinates the core components:
- Speech-to-Text (STT)
- Language Model (LLM)
- Text-to-Speech (TTS)
- Tool execution
- Memory management
- Personality engine
- Intent routing
- Feedback system

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
from stt import WhisperSTT
from llm import OllamaLLM
# TTS imports are now handled in the initialization code

# Type definitions for conversation history
Message = Dict[str, str]
MessageList = List[Message]

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
    """Main Coda Lite assistant class."""

    def __init__(self, config: ConfigLoader):
        """Initialize the Coda assistant."""
        self.config = config
        self.conversation_history: MessageList = []
        self.running = True
        self.processing = False  # Flag to track if we're currently processing a request
        self.response_queue = Queue()  # Queue for responses to be spoken

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

        # Use the TTS factory to get the appropriate TTS instance
        from tts.factory import get_tts_instance, get_available_tts_engines

        # Get available TTS engines
        available_engines = get_available_tts_engines()
        logger.info(f"Available TTS engines: {available_engines}")

        # Get the configured TTS engine, defaulting to ElevenLabs
        tts_engine = config.get("tts.engine", "elevenlabs")

        # Check if the requested engine is available
        if tts_engine not in available_engines or not available_engines[tts_engine]:
            logger.warning(f"Requested TTS engine '{tts_engine}' is not available. Falling back to ElevenLabs.")
            tts_engine = "elevenlabs"

        try:
            # Initialize TTS with lazy loading
            self.tts = get_tts_instance(
                tts_type=tts_engine,
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

        # Initialize memory manager
        logger.info("Initializing memory manager...")
        long_term_enabled = config.get("memory.long_term_enabled", False)

        if long_term_enabled:
            logger.info("Using enhanced memory manager with long-term memory")
            self.memory = EnhancedMemoryManager(config.get_all())
        else:
            logger.info("Using standard short-term memory manager")
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

        # Generate a natural language summary
        logger.info("Generating summarization response...")
        summary = ""
        for chunk in self.llm.chat(
            messages=messages,
            temperature=0.7,
            max_tokens=256,
            stream=True
        ):
            summary += chunk

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
            max_tokens = self.config.get("memory.max_tokens", 800)

            # Use enhanced context if we have an EnhancedMemoryManager
            if isinstance(self.memory, EnhancedMemoryManager):
                context = self.memory.get_enhanced_context(text, max_tokens=max_tokens)
                logger.info(f"Retrieved enhanced context with {len(context)} turns (including long-term memories)")
            else:
                context = self.memory.get_context(max_tokens=max_tokens)
                logger.info(f"Retrieved context with {len(context)} turns")

            # Generate initial response from LLM
            start_time = time.time()
            logger.info("Generating initial LLM response...")
            raw_response = ""
            for chunk in self.llm.chat(
                messages=context,
                temperature=self.config.get("llm.temperature", 0.7),
                max_tokens=self.config.get("llm.max_tokens", 256),
                stream=True
            ):
                raw_response += chunk
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

                    # Make sure we have a valid tool result
                    if not tool_result:
                        logger.warning(f"Tool {tool_name} returned empty result, using fallback")
                        # Generate fallback results based on tool name
                        if tool_name == "get_time":
                            tool_result = datetime.now().strftime("It's %H:%M.")
                        elif tool_name == "get_date":
                            tool_result = datetime.now().strftime("Today is %A, %B %d, %Y.")
                        elif tool_name == "tell_joke":
                            tool_result = "Why don't scientists trust atoms? Because they make up everything!"
                        else:
                            tool_result = f"No result available from {tool_name}."

                        logger.info(f"Using fallback tool result: {tool_result}")
                except Exception as e:
                    logger.error(f"Error executing tool {tool_name}: {e}")
                    # Generate fallback results based on tool name
                    if tool_name == "get_time":
                        tool_result = datetime.now().strftime("It's %H:%M.")
                    elif tool_name == "get_date":
                        tool_result = datetime.now().strftime("Today is %A, %B %d, %Y.")
                    elif tool_name == "tell_joke":
                        tool_result = "Why don't scientists trust atoms? Because they make up everything!"
                    else:
                        tool_result = f"Error executing {tool_name}."

                    logger.info(f"Using fallback tool result due to error: {tool_result}")

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

                # The tool result should already be properly formatted
                # Just use it directly without additional formatting
                formatted_result = tool_result

                # Clean up any JSON that might be in the tool result
                if isinstance(formatted_result, str) and ('{' in formatted_result or '}' in formatted_result):
                    formatted_result = extract_clean_response(formatted_result)

                logger.info(f"Final formatted tool result: {formatted_result}")

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

                # Create a brand new context for the second pass
                start_time = time.time()
                logger.info("Creating brand new context for second pass")

                # Get the original user query
                original_query = text  # This is the original user input

                # Create a completely new context with very explicit instructions
                second_pass_messages = [
                    {"role": "system", "content": "You are Coda, a helpful and natural-sounding voice assistant.\n\nYou have received the result of a tool call. DO NOT output any JSON.\nDO NOT repeat the tool call. DO NOT re-call the tool.\nDO NOT include any curly braces {} in your response.\nDO NOT mention tools, functions, or APIs.\nDO NOT use phrases like \"according to the tool\" or \"the tool says\".\n\nRespond clearly and casually with just the final answer. Do not say things like \"Let me check\" or \"I found that\". Just deliver the result naturally.\n\nKeep your response brief, conversational, and completely free of any JSON formatting."},
                    {"role": "system", "content": f"[TOOL RESULT] {formatted_result}"},
                    {"role": "user", "content": original_query}
                ]

                # Log the messages for debugging
                logger.info("Second pass messages:")
                for i, msg in enumerate(second_pass_messages):
                    logger.info(f"  Message {i}: role={msg['role']}, content={msg['content']}")

                # Generate a natural language summary
                logger.info("Generating second pass response...")
                logger.info("CRITICAL: Starting second LLM call with tool result")
                raw_summary = ""
                try:
                    for chunk in self.llm.chat(
                        messages=second_pass_messages,
                        temperature=0.5,  # Lower temperature for more deterministic output
                        max_tokens=512,  # Use a higher max_tokens for the second pass
                        stream=True
                    ):
                        raw_summary += chunk
                        logger.info(f"Received chunk: {chunk}")
                    logger.info(f"CRITICAL: Second pass complete, raw_summary: {raw_summary}")
                except Exception as e:
                    logger.error(f"CRITICAL ERROR in second pass: {e}", exc_info=True)
                    raw_summary = f"It's {datetime.now().strftime('%H:%M')}."  # Fallback

                # For time and date tools, consider using direct fallbacks first
                if tool_name == "get_time":
                    direct_fallback = f"It's {datetime.now().strftime('%H:%M')}."
                    logger.info(f"Direct fallback for time: {direct_fallback}")

                    # If the raw summary contains the correct time, use it
                    # Otherwise use the fallback
                    if datetime.now().strftime('%H:%M') in raw_summary or datetime.now().strftime('%I:%M') in raw_summary:
                        logger.info("Raw summary contains correct time, cleaning it")
                        final_response = extract_clean_response(raw_summary)
                    else:
                        logger.info("Using direct fallback for time")
                        final_response = direct_fallback

                elif tool_name == "get_date":
                    direct_fallback = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
                    logger.info(f"Direct fallback for date: {direct_fallback}")

                    # If the raw summary contains today's date, use it
                    # Otherwise use the fallback
                    if datetime.now().strftime('%B') in raw_summary and datetime.now().strftime('%d') in raw_summary:
                        logger.info("Raw summary contains correct date, cleaning it")
                        final_response = extract_clean_response(raw_summary)
                    else:
                        logger.info("Using direct fallback for date")
                        final_response = direct_fallback
                else:
                    # For other tools, clean the response
                    final_response = extract_clean_response(raw_summary)

                # Log the result
                logger.info(f"Generated raw summary: {raw_summary}")
                logger.info(f"Cleaned final response: {final_response}")
                end_time = time.time()

                logger.info(f"Final LLM response generated in {end_time - start_time:.2f} seconds")

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

                # Apply one final safety check to ensure no JSON leaks through
                logger.warning("CRITICAL: Applying aggressive JSON cleaning to final response")

                # First, check if we have a JSON tool call in the response
                if '[' in final_response or '{' in final_response or '}' in final_response or 'tool_call' in final_response.lower():
                    logger.warning("JSON detected in final response, applying aggressive cleaning")

                    # Try to extract just the natural language part after any JSON
                    json_end = max(final_response.rfind('}'), final_response.rfind(']'))
                    if json_end > 0 and json_end < len(final_response) - 1:
                        # There's text after the JSON, use that
                        natural_text = final_response[json_end+1:].strip()
                        if len(natural_text) > 5:
                            logger.info(f"Extracted natural text after JSON: {natural_text}")
                            final_response = natural_text

                    # Apply regex cleaning
                    final_response = extract_clean_response(final_response)

                    # If we still have JSON after cleaning, use a simple fallback
                    if '{' in final_response or '}' in final_response or '[' in final_response or ']' in final_response:
                        logger.warning("JSON persists after cleaning, using simple fallback")
                        if tool_name == "get_time":
                            final_response = f"It's {datetime.now().strftime('%H:%M')}."
                        elif tool_name == "get_date":
                            final_response = f"Today is {datetime.now().strftime('%A, %B %d, %Y')}."
                        else:
                            final_response = f"{formatted_result}"

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

            # Check if we should request feedback
            if self.feedback_manager and intent_result:
                if self.feedback_manager.should_request_feedback(intent_result):
                    feedback_request = self.feedback_manager.generate_feedback_prompt(intent_result)

                    if feedback_request:
                        # Add a short delay before asking for feedback
                        time.sleep(1.0)

                        # Add the feedback prompt to memory
                        self.memory.add_turn("assistant", feedback_request["prompt"])

                        # Queue the feedback prompt for TTS
                        self.response_queue.put(feedback_request["prompt"])

                        logger.info(f"Requested feedback: {feedback_request['prompt']}")

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

        # Handle memory cleanup
        try:
            if hasattr(self, 'memory'):
                if isinstance(self.memory, EnhancedMemoryManager):
                    # For enhanced memory manager, close it (which will persist short-term memory)
                    logger.info("Closing enhanced memory manager")
                    self.memory.close()
                    logger.info("Enhanced memory manager closed")
                elif self.memory.get_turn_count() > 1:  # Only export if we have conversation turns
                    # For standard memory manager, export to file
                    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
                    export_dir = self.config.get("memory.export_dir", "data/memory")
                    export_path = f"{export_dir}/session_{timestamp}.json"
                    self.memory.export(export_path)
                    logger.info(f"Exported memory to {export_path}")
        except Exception as e:
            logger.error(f"Error handling memory cleanup: {e}")

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
            try:
                from tts.factory import unload_current_tts
                unload_current_tts()
                logger.info("Unloaded TTS module using factory")
            except Exception as e:
                logger.warning(f"Error unloading TTS module using factory: {e}")

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
