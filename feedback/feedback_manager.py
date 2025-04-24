"""
Feedback manager for Coda Lite.

This module provides a manager class for collecting and processing user feedback.
"""

import logging
import random
from datetime import datetime
from enum import Enum, auto
from typing import Dict, Any, List, Optional, Tuple, Set

logger = logging.getLogger("coda.feedback.manager")

class FeedbackType(Enum):
    """Enum for different types of feedback."""
    HELPFULNESS = auto()  # Was the response helpful?
    MEMORY = auto()       # Should this be remembered?
    TONE = auto()         # Was the tone appropriate?
    VERBOSITY = auto()    # Was the response length appropriate?
    ACCURACY = auto()     # Was the information accurate?
    GENERAL = auto()      # General feedback

class FeedbackPrompt(Enum):
    """Enum for different feedback prompts."""
    HELPFULNESS = [
        "Was that helpful?",
        "Did that answer your question?",
        "Was that what you were looking for?",
        "Did that help?",
        "Was that response useful?"
    ]
    MEMORY = [
        "Would you like me to remember that?",
        "Should I make a note of that for future reference?",
        "Would you like me to save that information?",
        "Should I remember this conversation?",
        "Would it be helpful if I remembered this for next time?"
    ]
    TONE = [
        "Was my tone appropriate?",
        "Would you prefer a different tone?",
        "Was that the right level of formality?",
        "Should I adjust my communication style?",
        "Was my response style suitable?"
    ]
    VERBOSITY = [
        "Was that too detailed or too brief?",
        "Would you prefer more concise or more detailed responses?",
        "Was the length of my response appropriate?",
        "Should I be more brief or more thorough?",
        "Was that the right amount of information?"
    ]
    ACCURACY = [
        "Was that information accurate?",
        "Did I get anything wrong?",
        "Was my response correct?",
        "Did I make any mistakes?",
        "Was that factually accurate?"
    ]
    GENERAL = [
        "How was that response?",
        "Any feedback on my response?",
        "How am I doing?",
        "Any suggestions for improvement?",
        "Was there anything you'd like me to do differently?"
    ]

class FeedbackManager:
    """
    Manager for collecting and processing user feedback.

    This class:
    - Determines when to ask for feedback
    - Generates appropriate feedback prompts
    - Processes and stores feedback responses
    - Learns from feedback to improve future interactions
    """

    def __init__(self, memory_manager=None, personality_manager=None, config=None):
        """
        Initialize the feedback manager.

        Args:
            memory_manager: Memory manager for storing feedback
            personality_manager: Personality manager for adjusting based on feedback
            config: Configuration dictionary
        """
        self.memory_manager = memory_manager
        self.personality_manager = personality_manager
        self.config = config or {}

        # Feedback history
        self.feedback_history = []
        self.max_history = 100

        # Intent feedback mapping
        self.intent_feedback_mapping = {
            "INFORMATION_REQUEST": FeedbackType.HELPFULNESS,
            "MEMORY_RECALL": FeedbackType.ACCURACY,
            "MEMORY_STORE": FeedbackType.MEMORY,
            "EXTERNAL_ACTION": FeedbackType.HELPFULNESS,
            "TOOL_USE": FeedbackType.HELPFULNESS,
            "FUTURE_PLANNING": FeedbackType.HELPFULNESS,
            "USER_PREFERENCE": FeedbackType.MEMORY,
            "CONVERSATION_CONTROL": FeedbackType.GENERAL,
            "PERSONALITY_ADJUSTMENT": FeedbackType.TONE,
            "SYSTEM_COMMAND": None,  # No feedback for system commands
            "GREETING": None,  # No feedback for greetings
            "FAREWELL": None,  # No feedback for farewells
            "GRATITUDE": None,  # No feedback for gratitude
            "FEEDBACK": None,  # No feedback for feedback (meta!)
            "UNKNOWN": FeedbackType.GENERAL
        }

        # Feedback frequency settings
        self.feedback_frequency = self.config.get("feedback.frequency", 0.3)  # 30% chance by default
        self.feedback_cooldown = self.config.get("feedback.cooldown", 5)  # Wait at least 5 turns
        self.last_feedback_turn = 0
        self.current_turn = 0

        # Feedback prompt history to avoid repetition
        self.recent_prompt_types = []
        self.max_recent_prompts = 3

        # Active feedback request
        self.active_feedback_request = None

        logger.info("Feedback manager initialized")

    def should_request_feedback(self, intent_result: Dict[str, Any] = None) -> bool:
        """
        Determine if feedback should be requested.

        Args:
            intent_result: Optional result from intent processing

        Returns:
            True if feedback should be requested, False otherwise
        """
        # Increment turn counter
        self.current_turn += 1

        # Check if we have an active feedback request
        if self.active_feedback_request:
            return False

        # If no intent result is provided, use a simple frequency check
        if intent_result is None:
            # Check cooldown
            if self.current_turn - self.last_feedback_turn < self.feedback_cooldown:
                return False

            # Apply frequency check
            if random.random() > self.feedback_frequency:
                return False

            # All checks passed, request feedback
            logger.info("Requesting general feedback")
            return True

        # Process with intent result
        # Get intent type
        intent_type = intent_result.get("intent_type")
        if not intent_type:
            return False

        # Convert intent type to string if it's an enum
        intent_type_str = intent_type.name if hasattr(intent_type, "name") else str(intent_type)

        # Check if this intent type has a feedback mapping
        feedback_type = self.intent_feedback_mapping.get(intent_type_str)
        if not feedback_type:
            return False

        # Check cooldown
        if self.current_turn - self.last_feedback_turn < self.feedback_cooldown:
            return False

        # Apply frequency check
        if random.random() > self.feedback_frequency:
            return False

        # All checks passed, request feedback
        logger.info(f"Requesting feedback for intent: {intent_type_str}")
        return True

    def generate_feedback_prompt(self, intent_result: Dict[str, Any] = None) -> Optional[Dict[str, Any]]:
        """
        Generate a feedback prompt for the given intent result.

        Args:
            intent_result: Optional result from intent processing

        Returns:
            Dictionary with feedback prompt information or None
        """
        # If no intent result is provided, use general feedback
        if intent_result is None:
            feedback_type = FeedbackType.GENERAL
            intent_type_str = "GENERAL"
        else:
            # Get intent type
            intent_type = intent_result.get("intent_type")
            if not intent_type:
                return None

            # Convert intent type to string if it's an enum
            intent_type_str = intent_type.name if hasattr(intent_type, "name") else str(intent_type)

            # Get feedback type for this intent
            feedback_type = self.intent_feedback_mapping.get(intent_type_str)
            if not feedback_type:
                return None

        # Avoid repeating the same type of prompt too often
        if feedback_type in self.recent_prompt_types:
            # Try to find an alternative
            alternative_types = [
                ft for ft in FeedbackType
                if ft not in self.recent_prompt_types and ft != feedback_type
            ]
            if alternative_types:
                feedback_type = random.choice(alternative_types)

        # Update recent prompt types
        self.recent_prompt_types.append(feedback_type)
        if len(self.recent_prompt_types) > self.max_recent_prompts:
            self.recent_prompt_types.pop(0)

        # Get prompt options for this feedback type
        prompt_options = getattr(FeedbackPrompt, feedback_type.name).value

        # Select a random prompt
        prompt_text = random.choice(prompt_options)

        # Create feedback request
        feedback_request = {
            "id": f"feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}",
            "type": feedback_type,
            "prompt": prompt_text,
            "intent_type": intent_type_str,
            "intent_result": intent_result or {},
            "timestamp": datetime.now().isoformat(),
            "turn": self.current_turn
        }

        # Set as active feedback request
        self.active_feedback_request = feedback_request

        # Update last feedback turn
        self.last_feedback_turn = self.current_turn

        logger.info(f"Generated feedback prompt: {prompt_text}")
        return feedback_request

    def generate_feedback_request(self) -> Optional[str]:
        """
        Generate a feedback request string.

        Returns:
            Feedback request string or None if no feedback should be requested
        """
        # Check if we should request feedback
        if not self.should_request_feedback():
            return None

        # Generate a feedback prompt
        feedback_request = self.generate_feedback_prompt()
        if not feedback_request:
            return None

        # Return the prompt text
        return feedback_request.get("prompt")

    def process_feedback_response(self, user_input: str) -> Dict[str, Any]:
        """
        Process a user response to a feedback prompt.

        Args:
            user_input: User input text

        Returns:
            Dictionary with processing results
        """
        if not self.active_feedback_request:
            return {"processed": False, "reason": "No active feedback request"}

        # Analyze the response sentiment
        sentiment = self._analyze_sentiment(user_input)

        # Create feedback record
        feedback = {
            "id": self.active_feedback_request["id"],
            "type": self.active_feedback_request["type"],
            "prompt": self.active_feedback_request["prompt"],
            "response": user_input,
            "sentiment": sentiment,
            "intent_type": self.active_feedback_request["intent_type"],
            "intent_result": self.active_feedback_request["intent_result"],
            "timestamp": datetime.now().isoformat(),
            "turn": self.current_turn
        }

        # Add to history
        self.feedback_history.append(feedback)
        if len(self.feedback_history) > self.max_history:
            self.feedback_history = self.feedback_history[-self.max_history:]

        # Store in memory if available
        if self.memory_manager and hasattr(self.memory_manager, 'add_feedback'):
            try:
                self.memory_manager.add_feedback(feedback)
                logger.info(f"Stored feedback in memory: {feedback['id']}")
            except Exception as e:
                logger.error(f"Error storing feedback in memory: {e}")

        # Apply feedback if appropriate
        self._apply_feedback(feedback)

        # Clear active feedback request
        self.active_feedback_request = None

        logger.info(f"Processed feedback response with sentiment: {sentiment}")
        return {"processed": True, "feedback": feedback}

    def _analyze_sentiment(self, text: str) -> str:
        """
        Analyze the sentiment of a feedback response.

        Args:
            text: Feedback response text

        Returns:
            Sentiment as "positive", "negative", or "neutral"
        """
        # Simple keyword-based sentiment analysis
        positive_keywords = [
            "yes", "yeah", "yep", "sure", "good", "great", "excellent", "perfect",
            "helpful", "useful", "thanks", "thank", "correct", "right", "accurate",
            "appropriate", "fine", "ok", "okay", "nice", "love", "like", "awesome"
        ]

        negative_keywords = [
            "no", "nope", "not", "bad", "poor", "terrible", "unhelpful", "useless",
            "wrong", "incorrect", "inaccurate", "inappropriate", "too long", "too short",
            "confusing", "confused", "unclear", "don't", "didn't", "wasn't", "isn't"
        ]

        # Convert to lowercase for comparison
        text_lower = text.lower()

        # Count positive and negative keywords
        positive_count = sum(1 for word in positive_keywords if word in text_lower)
        negative_count = sum(1 for word in negative_keywords if word in text_lower)

        # Determine sentiment
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    def _apply_feedback(self, feedback: Dict[str, Any]) -> None:
        """
        Apply feedback to improve future interactions.

        Args:
            feedback: Feedback record
        """
        feedback_type = feedback["type"]
        sentiment = feedback["sentiment"]

        # Only apply adjustments for clear positive/negative sentiment
        if sentiment == "neutral":
            return

        # Apply feedback based on type
        if self.personality_manager and hasattr(self.personality_manager, 'parameters'):
            try:
                if feedback_type == FeedbackType.TONE:
                    # Adjust formality based on tone feedback
                    if sentiment == "negative":
                        # If negative feedback about tone, try the opposite of current setting
                        current_formality = self.personality_manager.parameters.get_parameter_value("formality")
                        if current_formality > 0.5:
                            # Currently formal, try more casual
                            self.personality_manager.parameters.set_parameter_value(
                                "formality", 0.3, reason="feedback:tone"
                            )
                        else:
                            # Currently casual, try more formal
                            self.personality_manager.parameters.set_parameter_value(
                                "formality", 0.7, reason="feedback:tone"
                            )
                        logger.info("Adjusted formality based on tone feedback")

                elif feedback_type == FeedbackType.VERBOSITY:
                    # Adjust verbosity based on feedback
                    if sentiment == "negative":
                        # If negative feedback about verbosity, try the opposite of current setting
                        current_verbosity = self.personality_manager.parameters.get_parameter_value("verbosity")
                        if current_verbosity > 0.5:
                            # Currently verbose, try more concise
                            self.personality_manager.parameters.set_parameter_value(
                                "verbosity", 0.3, reason="feedback:verbosity"
                            )
                        else:
                            # Currently concise, try more verbose
                            self.personality_manager.parameters.set_parameter_value(
                                "verbosity", 0.7, reason="feedback:verbosity"
                            )
                        logger.info("Adjusted verbosity based on feedback")

                elif feedback_type == FeedbackType.HELPFULNESS:
                    # For helpfulness feedback, adjust proactivity
                    if sentiment == "positive":
                        # If positive feedback, slightly increase proactivity
                        self.personality_manager.parameters.set_parameter_value(
                            "proactivity",
                            min(0.8, self.personality_manager.parameters.get_parameter_value("proactivity") + 0.1),
                            reason="feedback:helpfulness"
                        )
                    elif sentiment == "negative":
                        # If negative feedback, slightly decrease proactivity
                        self.personality_manager.parameters.set_parameter_value(
                            "proactivity",
                            max(0.2, self.personality_manager.parameters.get_parameter_value("proactivity") - 0.1),
                            reason="feedback:helpfulness"
                        )
                    logger.info("Adjusted proactivity based on helpfulness feedback")

            except Exception as e:
                logger.error(f"Error applying feedback: {e}")

    def is_feedback_response(self, user_input: str) -> bool:
        """
        Determine if user input is a response to a feedback prompt.

        Args:
            user_input: User input text

        Returns:
            True if input is a feedback response, False otherwise
        """
        if not self.active_feedback_request:
            return False

        # Simple heuristic: short responses are likely feedback responses
        if len(user_input.split()) <= 5:
            return True

        # Check for common feedback response patterns
        feedback_patterns = [
            "yes", "no", "yeah", "nope", "sure", "not really",
            "it was", "it wasn't", "that was", "that wasn't",
            "i like", "i don't like", "better", "worse",
            "too much", "too little", "just right", "perfect",
            "helpful", "unhelpful", "useful", "useless",
            "correct", "incorrect", "right", "wrong"
        ]

        user_input_lower = user_input.lower()
        for pattern in feedback_patterns:
            if pattern in user_input_lower:
                return True

        # If we can't determine, assume it's not a feedback response
        return False

    def get_feedback_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """
        Get feedback history.

        Args:
            limit: Maximum number of history items to return

        Returns:
            List of feedback history items
        """
        if limit is None or limit > len(self.feedback_history):
            return self.feedback_history
        return self.feedback_history[-limit:]

    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get statistics about collected feedback.

        Returns:
            Dictionary with feedback statistics
        """
        if not self.feedback_history:
            return {
                "total": 0,
                "positive": 0,
                "negative": 0,
                "neutral": 0,
                "by_type": {},
                "by_intent": {}
            }

        # Count by sentiment
        sentiment_counts = {"positive": 0, "negative": 0, "neutral": 0}
        for feedback in self.feedback_history:
            sentiment_counts[feedback["sentiment"]] += 1

        # Count by type
        type_counts = {}
        for feedback in self.feedback_history:
            feedback_type = feedback["type"].name if hasattr(feedback["type"], "name") else str(feedback["type"])
            if feedback_type not in type_counts:
                type_counts[feedback_type] = 0
            type_counts[feedback_type] += 1

        # Count by intent
        intent_counts = {}
        for feedback in self.feedback_history:
            intent_type = feedback["intent_type"]
            if intent_type not in intent_counts:
                intent_counts[intent_type] = 0
            intent_counts[intent_type] += 1

        return {
            "total": len(self.feedback_history),
            "positive": sentiment_counts["positive"],
            "negative": sentiment_counts["negative"],
            "neutral": sentiment_counts["neutral"],
            "by_type": type_counts,
            "by_intent": intent_counts
        }

    def clear_history(self) -> None:
        """Clear feedback history."""
        self.feedback_history = []
        self.active_feedback_request = None
        logger.info("Cleared feedback history")

    def reset(self) -> None:
        """Reset the feedback manager."""
        self.feedback_history = []
        self.active_feedback_request = None
        self.recent_prompt_types = []
        self.last_feedback_turn = 0
        self.current_turn = 0
        logger.info("Reset feedback manager")
