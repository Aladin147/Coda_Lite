"""
Advanced personality management for Coda Lite.

This module provides an integrated system for managing Coda's advanced personality features,
including behavioral conditioning, topic awareness, and session management.
"""

import os
import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

from .parameters import PersonalityParameters
from .behavioral_conditioning import BehavioralConditioner
from .topic_awareness import TopicAwareness
from .session_manager import SessionManager
from .enhanced_personality_loader import EnhancedPersonalityLoader
from .personal_lore import PersonalLoreManager
from .memory_conditioning import MemoryConditioner

logger = logging.getLogger("coda.personality.advanced_manager")

class AdvancedPersonalityManager:
    """
    Manages advanced personality features for Coda.

    This class integrates:
    - Personality parameters
    - Behavioral conditioning
    - Topic awareness
    - Session management
    - Enhanced personality loading

    It provides a unified interface for personality management.
    """

    def __init__(self,
                 memory_manager=None,
                 config: Optional[Dict[str, Any]] = None):
        """
        Initialize the advanced personality manager.

        Args:
            memory_manager: Memory manager for accessing conversation history
            config: Configuration dictionary
        """
        self.memory_manager = memory_manager
        self.config = config or {}

        # Initialize personality parameters
        self.parameters = PersonalityParameters()

        # Initialize enhanced personality loader
        personality_file = self.config.get("personality_file", "config/personality/coda_personality_enhanced.json")
        templates_dir = self.config.get("templates_dir", "config/prompts/templates")
        self.personality_loader = EnhancedPersonalityLoader(
            personality_file=personality_file,
            templates_dir=templates_dir
        )

        # Initialize behavioral conditioner
        self.behavioral_conditioner = BehavioralConditioner(
            memory_manager=memory_manager,
            personality_parameters=self.parameters
        )

        # Initialize topic awareness
        self.topic_awareness = TopicAwareness(
            memory_manager=memory_manager,
            personality_parameters=self.parameters
        )

        # Initialize session manager
        self.session_manager = SessionManager(
            memory_manager=memory_manager,
            personality_parameters=self.parameters
        )

        # Initialize personal lore manager
        lore_file = self.config.get("lore_file", "config/personality/personal_lore.json")
        self.lore_manager = PersonalLoreManager(lore_file=lore_file)

        # Initialize memory conditioner
        self.memory_conditioner = MemoryConditioner(
            memory_manager=memory_manager,
            personality_manager=self,
            behavioral_conditioner=self.behavioral_conditioner,
            config=self.config
        )

        # Feedback manager (will be set by main application)
        self.feedback_manager = None

        # Track context for prompt generation
        self.current_context = {
            "type": "default",
            "topic": None,
            "category": None,
            "in_closure_mode": False,
            "trigger_words": []
        }

        logger.info("Initialized advanced personality manager")

    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through all personality components.

        Args:
            user_input: User input text

        Returns:
            Dictionary with processing results
        """
        results = {}

        # Process through behavioral conditioner
        behavior_results = self.behavioral_conditioner.process_user_input(user_input)
        results["behavior"] = behavior_results

        # Process through topic awareness
        topic_results = self.topic_awareness.process_user_input(user_input)
        results["topic"] = topic_results

        # Update session manager
        self.session_manager.process_interaction("user", user_input)
        session_state = self.session_manager.get_session_state()
        results["session"] = session_state

        # Update current context
        self._update_current_context(topic_results, session_state)

        logger.info(f"Processed user input through personality components")
        return results

    def process_assistant_response(self, response: str) -> Dict[str, Any]:
        """
        Process assistant response through personality components.

        Args:
            response: Assistant response text

        Returns:
            Dictionary with processing results
        """
        results = {}

        # Update session manager
        self.session_manager.process_interaction("assistant", response)
        session_state = self.session_manager.get_session_state()
        results["session"] = session_state

        # Analyze interaction patterns periodically
        if self.session_manager.turn_count % 5 == 0:
            pattern_results = self.behavioral_conditioner.analyze_interaction_patterns()
            results["patterns"] = pattern_results

            # Apply feedback patterns periodically
            if hasattr(self, 'memory_conditioner') and self.session_manager.turn_count % 10 == 0:
                feedback_results = self.apply_feedback_patterns()
                if feedback_results.get("applied", False):
                    results["feedback_patterns"] = feedback_results

        logger.info(f"Processed assistant response through personality components")
        return results

    def _update_current_context(self, topic_results: Dict[str, Any], session_state: Dict[str, Any]) -> None:
        """
        Update the current context based on processing results.

        Args:
            topic_results: Results from topic awareness
            session_state: Results from session manager
        """
        # Determine context type
        context_type = "default"

        # Check for topic-based context
        if topic_results.get("category"):
            category = topic_results["category"]
            if category == "technical":
                context_type = "technical_topic"
            elif category == "creative":
                context_type = "creative_task"
            elif category == "business":
                context_type = "formal_context"
            elif category == "personal":
                context_type = "personal_context"
            elif category == "entertainment":
                context_type = "entertainment"
            elif category == "informational":
                context_type = "information_request"

        # Check for session closure mode
        if session_state.get("in_closure_mode"):
            context_type = "session_closure"

        # Extract trigger words for personal lore
        trigger_words = []
        if topic_results.get("topic"):
            trigger_words.append(topic_results["topic"])
        if topic_results.get("keywords"):
            trigger_words.extend(topic_results["keywords"])
        if topic_results.get("category"):
            trigger_words.append(topic_results["category"])

        # Update current context
        self.current_context = {
            "type": context_type,
            "topic": topic_results.get("topic"),
            "category": topic_results.get("category"),
            "in_closure_mode": session_state.get("in_closure_mode", False),
            "trigger_words": trigger_words
        }

        logger.info(f"Updated current context: {self.current_context}")

    def generate_system_prompt(self) -> str:
        """
        Generate a system prompt based on current context and personality.

        Returns:
            Generated system prompt
        """
        context_type = self.current_context.get("type", "default")
        trigger_words = self.current_context.get("trigger_words", [])

        # Generate prompt using enhanced personality loader
        prompt = self.personality_loader.generate_system_prompt(
            context_type=context_type,
            memory_manager=self.memory_manager
        )

        # Add session closure message if in closure mode
        if self.current_context.get("in_closure_mode"):
            closure_message = self.session_manager.get_closure_message()
            if closure_message:
                prompt += f"\n\nThe session appears to be winding down. Consider using this message: \"{closure_message}\""

        # Inject personal lore into prompt
        prompt = self.lore_manager.inject_lore_into_prompt(
            prompt=prompt,
            context_type=context_type,
            trigger_words=trigger_words
        )

        # Add current personality parameters
        param_info = "\n\nCurrent personality parameters:\n"
        for name, param in self.parameters.get_all_parameters().items():
            value = param.get("value", 0.5)
            param_info += f"- {name}: {value:.2f}\n"

        prompt += param_info

        logger.info(f"Generated system prompt for context: {context_type}")
        return prompt

    def format_response(self, response: str) -> str:
        """
        Format a response based on personality parameters.

        Args:
            response: Original response text

        Returns:
            Formatted response
        """
        # Get current parameters
        verbosity = self.parameters.get_parameter_value("verbosity") or 0.5

        # Get context information
        context_type = self.current_context.get("type", "default")
        trigger_words = self.current_context.get("trigger_words", [])
        user_emotion = "neutral"  # Could be enhanced with emotion detection

        # Apply formatting based on parameters
        formatted_response = response

        # Apply verbosity adjustment
        if verbosity < 0.3 and len(response) > 100:
            # Shorten response for low verbosity
            sentences = response.split('. ')
            if len(sentences) > 2:
                formatted_response = '. '.join(sentences[:2]) + '.'

        # Use enhanced personality loader's format_response
        formatted_response = self.personality_loader.format_response(
            formatted_response,
            response_type=None,
            user_emotion=user_emotion,
            context_type=context_type
        )

        # Apply personal lore formatting
        formatted_response = self.lore_manager.format_response_with_lore(
            response=formatted_response,
            context_type=context_type,
            trigger_words=trigger_words
        )

        logger.info(f"Formatted response based on personality parameters")
        return formatted_response

    def get_current_context(self) -> Dict[str, Any]:
        """
        Get the current context.

        Returns:
            Dictionary with current context
        """
        return self.current_context

    def get_behavior_profile(self) -> Dict[str, Any]:
        """
        Get the current behavior profile.

        Returns:
            Behavior profile dictionary
        """
        return self.behavioral_conditioner.get_behavior_profile()

    def get_current_topic(self) -> Dict[str, Any]:
        """
        Get the current conversation topic.

        Returns:
            Dictionary with current topic information
        """
        return self.topic_awareness.get_current_topic()

    def get_session_state(self) -> Dict[str, Any]:
        """
        Get the current session state.

        Returns:
            Dictionary with session state
        """
        return self.session_manager.get_session_state()

    def get_personality_parameters(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all personality parameters.

        Returns:
            Dictionary of all parameters
        """
        return self.parameters.get_all_parameters()

    def get_personal_lore(self) -> Dict[str, Any]:
        """
        Get personal lore information.

        Returns:
            Dictionary with personal lore information
        """
        return {
            "backstory": self.lore_manager.get_backstory(),
            "preferences": self.lore_manager.get_preferences(),
            "traits": self.lore_manager.get_traits(),
            "memories": self.lore_manager.get_formative_memories(),
            "usage_statistics": self.lore_manager.get_usage_statistics()
        }

    def apply_feedback_patterns(self) -> Dict[str, Any]:
        """
        Apply feedback patterns to personality parameters.

        Returns:
            Dictionary with application results
        """
        if not hasattr(self, 'memory_conditioner'):
            logger.warning("Memory conditioner not available")
            return {"applied": False, "reason": "memory_conditioner_not_available"}

        # Apply feedback patterns
        result = self.memory_conditioner.apply_feedback_patterns()

        if result.get("applied", False):
            logger.info(f"Applied {len(result.get('changes', []))} changes based on feedback patterns")
        else:
            logger.info(f"No changes applied from feedback patterns: {result.get('reason')}")

        return result

    def get_user_preference_insights(self) -> Dict[str, Any]:
        """
        Get insights into user preferences based on feedback.

        Returns:
            Dictionary with user preference insights
        """
        if not hasattr(self, 'memory_conditioner'):
            logger.warning("Memory conditioner not available")
            return {"available": False, "reason": "memory_conditioner_not_available"}

        # Get user preference insights
        insights = self.memory_conditioner.get_user_preference_insights()

        return insights

    def reset(self) -> None:
        """Reset the personality manager."""
        self.parameters.reset_to_defaults()
        self.behavioral_conditioner.reset()
        self.topic_awareness.reset()
        self.session_manager.reset()
        self.lore_manager.reset_usage_statistics()

        # Reset memory conditioner if available
        if hasattr(self, 'memory_conditioner'):
            self.memory_conditioner.reset()
            logger.info("Reset memory conditioner")

        # Reset feedback manager if available
        if self.feedback_manager and hasattr(self.feedback_manager, 'reset'):
            self.feedback_manager.reset()
            logger.info("Reset feedback manager")

        self.current_context = {
            "type": "default",
            "topic": None,
            "category": None,
            "in_closure_mode": False,
            "trigger_words": []
        }

        logger.info("Reset advanced personality manager")
