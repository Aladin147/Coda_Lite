"""
Intent routing system for Coda Lite.

This module provides a lightweight intent routing system that helps Coda
understand different types of user requests and route them appropriately.
"""

import re
import logging
from typing import Dict, Any, List, Optional, Tuple, Set
from enum import Enum, auto

logger = logging.getLogger("coda.intent.router")

class IntentType(Enum):
    """Enum for different types of intents."""
    UNKNOWN = auto()
    INFORMATION_REQUEST = auto()  # General questions, "what is X"
    MEMORY_RECALL = auto()        # "What do you remember about X"
    MEMORY_STORE = auto()         # "Remember that X"
    EXTERNAL_ACTION = auto()      # "Look up X", "Search for X"
    TOOL_USE = auto()             # "Calculate X", "Get the time"
    FUTURE_PLANNING = auto()      # "Remind me to X", "Schedule X"
    USER_PREFERENCE = auto()      # "I prefer X", "I like X"
    CONVERSATION_CONTROL = auto() # "Let's change the subject", "Stop"
    PERSONALITY_ADJUSTMENT = auto() # "Be more formal", "Be funnier"
    SYSTEM_COMMAND = auto()       # "#reset", "#debug_on"
    GREETING = auto()             # "Hello", "Hi"
    FAREWELL = auto()             # "Goodbye", "Bye"
    GRATITUDE = auto()            # "Thank you", "Thanks"
    FEEDBACK = auto()             # "That was helpful", "That's wrong"

class IntentRouter:
    """
    Lightweight intent router for Coda.

    This class:
    - Analyzes user input to detect intent
    - Routes intents to appropriate handlers
    - Tracks intent history for context
    """

    def __init__(self):
        """Initialize the intent router."""
        # Intent patterns
        self.intent_patterns = {
            IntentType.INFORMATION_REQUEST: [
                r"(?:what|who|where|when|why|how|tell me about|explain|describe|define)\s.+\??",
                r"(?:do you know|can you tell me|i want to know|i'd like to know)\s.+\??",
                r"(?:what is|who is|where is|when is|why is|how is)\s.+\??",
            ],
            IntentType.MEMORY_RECALL: [
                r"(?:what do you remember|do you remember|can you recall|recall)\s.+\??",
                r"(?:have i told you|did i mention|did we talk about)\s.+\??",
                r"(?:what do you know about me|what have i told you about)\s.+\??",
            ],
            IntentType.MEMORY_STORE: [
                r"(?:remember|note|keep in mind|don't forget|store this|save this)\s.+",
                r"(?:i want you to remember|please remember|make a note that)\s.+",
                r"(?:this is important|remember for next time|save for later)\s?:?\s.+",
            ],
            IntentType.EXTERNAL_ACTION: [
                r"(?:look up|search for|find|google|search|look for)\s.+",
                r"(?:can you look up|can you search for|can you find|can you check)\s.+\??",
                r"(?:i need information on|i need to know about|get me information about)\s.+",
            ],
            IntentType.TOOL_USE: [
                r"(?:calculate|compute|convert|translate|get the time|get the date|set a timer|set an alarm)\s.+",
                r"(?:can you calculate|can you compute|can you convert|can you translate)\s.+\??",
                r"(?:what time is it|what's the date|what day is it|tell me the time|tell me the date)\??",
            ],
            IntentType.FUTURE_PLANNING: [
                r"(?:remind me to|remind me about|schedule|plan|set a reminder for)\s.+",
                r"(?:can you remind me to|can you remind me about|can you schedule)\s.+\??",
                r"(?:i need to remember to|don't let me forget to|make sure i)\s.+",
            ],
            IntentType.USER_PREFERENCE: [
                r"(?:i prefer|i like|i love|i enjoy|i don't like|i hate|i dislike)\s.+",
                r"(?:my favorite|i'm a fan of|i'm not a fan of|i'm interested in)\s.+",
                r"(?:i want you to|i'd like you to|please)\s.+",
            ],
            IntentType.CONVERSATION_CONTROL: [
                r"(?:let's talk about|let's discuss|change the subject|change topic|move on)\s?",
                r"(?:stop|pause|wait|hold on|never mind|cancel|forget it)\s?",
                r"(?:start over|reset|let's start again|begin again)\s?",
            ],
            IntentType.PERSONALITY_ADJUSTMENT: [
                r"(?:be more|be less|sound more|sound less|try to be more|try to be less)\s.+",
                r"(?:i want you to be more|i want you to be less|can you be more|can you be less)\s.+\??",
                r"(?:you're too|you are too|you're not|you aren't)\s.+",
            ],
            IntentType.SYSTEM_COMMAND: [
                r"^#\w+",  # Starts with # followed by word characters
                r"^/\w+",  # Starts with / followed by word characters
                r"^!\w+",  # Starts with ! followed by word characters
            ],
            IntentType.GREETING: [
                r"^(?:hello|hi|hey|greetings|good morning|good afternoon|good evening)\b",
                r"^(?:what's up|sup|yo|howdy)\b",
                r"^(?:nice to meet you|nice to see you|good to see you)\b",
            ],
            IntentType.FAREWELL: [
                r"(?:goodbye|bye|see you|talk to you later|until next time|have a good day)\s?",
                r"(?:i'm leaving|i have to go|i need to go|i'm heading out)\s?",
                r"(?:that's all|that will be all|we're done|we are done|end session)\s?",
            ],
            IntentType.GRATITUDE: [
                r"(?:thank you|thanks|appreciate it|i appreciate|much appreciated|thank you for)\s?",
                r"(?:that was helpful|you've been helpful|you're helpful|you helped|you're a lifesaver)\s?",
                r"(?:good job|well done|nice work|excellent work|great job)\s?",
            ],
            IntentType.FEEDBACK: [
                r"(?:that's wrong|that's incorrect|that's not right|you're wrong|you are wrong)\s?",
                r"(?:that's right|that's correct|you're right|you are right|that's helpful)\s?",
                r"(?:i like how you|i don't like how you|that's better|that's worse)\s?",
            ],
        }

        # System command patterns
        self.system_commands = {
            # Personality commands
            "reset_tone": r"^#reset_tone\s+(\w+)$",
            "mood_reset": r"^#mood_reset$",
            "personality_insight": r"^#personality_insight$",

            # Memory commands
            "show_memory": r"^#show_memory$",
            "summarize_session": r"^#summarize_session$",
            "summarize_day": r"^#summarize_day$",
            "view_feedback": r"^#view_feedback(?:\s+(\w+))?$",

            # Feedback commands
            "feedback": r"^#feedback(?:\s+(\w+))?$",

            # System commands
            "debug_on": r"^#debug_on$",
            "debug_off": r"^#debug_off$",
            "help": r"^#help$",
        }

        # Intent history
        self.intent_history = []
        self.max_history = 10

        # Intent handlers
        self.intent_handlers = {}

        logger.info("Intent router initialized")

    def detect_intent(self, user_input: str) -> Tuple[IntentType, Dict[str, Any]]:
        """
        Detect the intent of a user input.

        Args:
            user_input: User input text

        Returns:
            Tuple of (IntentType, metadata)
        """
        user_input = user_input.strip()

        # Check for system commands first
        for command, pattern in self.system_commands.items():
            match = re.match(pattern, user_input, re.IGNORECASE)
            if match:
                metadata = {
                    "command": command,
                    "args": match.groups() if match.groups() else [],
                    "raw_input": user_input
                }
                logger.info(f"Detected system command: {command}")
                return IntentType.SYSTEM_COMMAND, metadata

        # Check other intent patterns
        for intent_type, patterns in self.intent_patterns.items():
            for pattern in patterns:
                if re.search(pattern, user_input, re.IGNORECASE):
                    metadata = {
                        "pattern_matched": pattern,
                        "raw_input": user_input
                    }
                    logger.info(f"Detected intent: {intent_type.name}")
                    return intent_type, metadata

        # Default to unknown intent
        logger.info("No specific intent detected, defaulting to UNKNOWN")
        return IntentType.UNKNOWN, {"raw_input": user_input}

    def extract_entities(self, user_input: str, intent_type: IntentType) -> Dict[str, Any]:
        """
        Extract entities from user input based on intent type.

        Args:
            user_input: User input text
            intent_type: Detected intent type

        Returns:
            Dictionary of extracted entities
        """
        entities = {}

        if intent_type == IntentType.MEMORY_RECALL:
            # Extract what to recall
            recall_match = re.search(r"(?:remember|recall|know about|told you about)\s+(.+?)(?:\?|$)", user_input, re.IGNORECASE)
            if recall_match:
                entities["recall_subject"] = recall_match.group(1).strip()

        elif intent_type == IntentType.MEMORY_STORE:
            # Extract what to remember
            store_match = re.search(r"(?:remember|note|keep in mind|don't forget|store|save)\s+(?:that|this|:)?\s*(.+?)(?:\.|$)", user_input, re.IGNORECASE)
            if store_match:
                entities["store_content"] = store_match.group(1).strip()

        elif intent_type == IntentType.EXTERNAL_ACTION:
            # Extract what to look up
            lookup_match = re.search(r"(?:look up|search for|find|google|search|look for)\s+(.+?)(?:\?|$)", user_input, re.IGNORECASE)
            if lookup_match:
                entities["lookup_query"] = lookup_match.group(1).strip()

        elif intent_type == IntentType.FUTURE_PLANNING:
            # Extract what to remind
            remind_match = re.search(r"(?:remind me to|remind me about|schedule|plan|reminder for)\s+(.+?)(?:\.|$)", user_input, re.IGNORECASE)
            if remind_match:
                entities["reminder_content"] = remind_match.group(1).strip()

            # Try to extract time
            time_match = re.search(r"(?:at|on|in|tomorrow|next|later|tonight|morning|afternoon|evening)\s+(.+?)(?:\.|$)", user_input, re.IGNORECASE)
            if time_match:
                entities["reminder_time"] = time_match.group(0).strip()

        elif intent_type == IntentType.PERSONALITY_ADJUSTMENT:
            # Extract personality adjustment
            adj_match = re.search(r"(?:be more|be less|sound more|sound less)\s+(.+?)(?:\.|$)", user_input, re.IGNORECASE)
            if adj_match:
                entities["adjustment_trait"] = adj_match.group(1).strip()
                entities["adjustment_direction"] = "more" if "more" in adj_match.group(0) else "less"

        elif intent_type == IntentType.SYSTEM_COMMAND:
            # Extract command and args
            for command, pattern in self.system_commands.items():
                match = re.match(pattern, user_input, re.IGNORECASE)
                if match:
                    entities["command"] = command
                    entities["args"] = list(match.groups()) if match.groups() else []
                    break

        logger.info(f"Extracted entities: {entities}")
        return entities

    def register_intent_handler(self, intent_type: IntentType, handler_func):
        """
        Register a handler function for a specific intent type.

        Args:
            intent_type: Intent type to handle
            handler_func: Function to call for this intent
        """
        self.intent_handlers[intent_type] = handler_func
        logger.info(f"Registered handler for intent: {intent_type.name}")

    def route_intent(self, user_input: str) -> Dict[str, Any]:
        """
        Route user input to appropriate handler based on intent.

        Args:
            user_input: User input text

        Returns:
            Dictionary with routing results
        """
        # Detect intent
        intent_type, metadata = self.detect_intent(user_input)

        # Extract entities
        entities = self.extract_entities(user_input, intent_type)

        # Update intent history
        self.intent_history.append({
            "intent_type": intent_type,
            "user_input": user_input,
            "entities": entities,
            "metadata": metadata
        })

        # Trim history if needed
        if len(self.intent_history) > self.max_history:
            self.intent_history = self.intent_history[-self.max_history:]

        # Call handler if registered
        result = {
            "intent_type": intent_type,
            "entities": entities,
            "metadata": metadata,
            "handled": False,
            "response": None
        }

        if intent_type in self.intent_handlers:
            try:
                handler_result = self.intent_handlers[intent_type](user_input, entities, metadata)
                result["handled"] = True
                result["response"] = handler_result
                logger.info(f"Successfully handled intent: {intent_type.name}")
            except Exception as e:
                logger.error(f"Error handling intent {intent_type.name}: {e}")
                result["error"] = str(e)
        else:
            logger.info(f"No handler registered for intent: {intent_type.name}")

        return result

    def get_intent_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get intent history.

        Args:
            limit: Maximum number of history items to return

        Returns:
            List of intent history items
        """
        if limit is None or limit > len(self.intent_history):
            return self.intent_history
        return self.intent_history[-limit:]

    def get_recent_intents(self, count: int = 3) -> List[IntentType]:
        """
        Get the most recent intent types.

        Args:
            count: Number of recent intents to return

        Returns:
            List of recent intent types
        """
        recent = []
        for item in reversed(self.intent_history):
            if len(recent) >= count:
                break
            recent.append(item["intent_type"])
        return recent

    def clear_history(self) -> None:
        """Clear intent history."""
        self.intent_history = []
        logger.info("Cleared intent history")

    def get_intent_distribution(self) -> Dict[IntentType, int]:
        """
        Get distribution of intents in history.

        Returns:
            Dictionary mapping intent types to counts
        """
        distribution = {}
        for item in self.intent_history:
            intent_type = item["intent_type"]
            if intent_type not in distribution:
                distribution[intent_type] = 0
            distribution[intent_type] += 1
        return distribution
