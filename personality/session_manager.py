"""
Session management system for Coda Lite.

This module provides a system for tracking session state and managing session closure,
allowing Coda to provide appropriate session summaries and closure.
"""

import os
import json
import logging
import re
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union, Tuple
from collections import Counter

from .parameters import PersonalityParameters

logger = logging.getLogger("coda.personality.session_manager")

class SessionManager:
    """
    Manages conversation session state and closure.

    This class:
    - Tracks session duration and idle time
    - Detects when a session should enter closure mode
    - Generates session summaries
    - Adjusts personality for session closure
    """

    def __init__(self,
                 memory_manager=None,
                 personality_parameters: Optional[PersonalityParameters] = None):
        """
        Initialize the session manager.

        Args:
            memory_manager: Memory manager for accessing conversation history
            personality_parameters: Personality parameters to adjust
        """
        self.memory_manager = memory_manager

        # Initialize personality parameters
        if personality_parameters:
            self.parameters = personality_parameters
        else:
            self.parameters = PersonalityParameters()

        # Initialize session state
        self.session_start_time = datetime.now()
        self.last_interaction_time = datetime.now()
        self.session_duration = 0
        self.idle_time = 0
        self.turn_count = 0

        # Session closure settings
        self.long_session_threshold = 1800  # 30 minutes
        self.idle_threshold = 600  # 10 minutes
        self.in_closure_mode = False

        # Session summary
        self.session_summary = {}

        logger.info("Initialized session manager")

    def update(self) -> Dict[str, Any]:
        """
        Update session state.

        Returns:
            Dictionary with updated session state
        """
        now = datetime.now()
        self.session_duration = (now - self.session_start_time).total_seconds()
        self.idle_time = (now - self.last_interaction_time).total_seconds()

        # Check if we should enter closure mode
        if not self.in_closure_mode:
            # Check thresholds directly to avoid recursion
            if (self.session_duration > self.long_session_threshold or
                self.idle_time > self.idle_threshold):
                self.in_closure_mode = True
                self._apply_closure_adjustments()

                # Generate session summary if we have a memory manager
                if self.memory_manager:
                    self.session_summary = self.generate_session_summary()

        return {
            "session_duration": self.session_duration,
            "idle_time": self.idle_time,
            "turn_count": self.turn_count,
            "in_closure_mode": self.in_closure_mode
        }

    def process_interaction(self, role: str, content: str) -> None:
        """
        Process a new interaction.

        Args:
            role: Speaker role
            content: Message content
        """
        # Update last interaction time
        self.last_interaction_time = datetime.now()

        # Increment turn count if it's a user or assistant message
        if role in ["user", "assistant"]:
            self.turn_count += 1

        # Reset closure mode if we were in it
        if self.in_closure_mode:
            self.in_closure_mode = False
            self._reset_closure_adjustments()

    def should_enter_closure_mode(self) -> bool:
        """
        Determine if we should enter session closure mode.

        Returns:
            True if we should enter closure mode, False otherwise
        """
        # Update session state without calling this method again
        now = datetime.now()
        self.session_duration = (now - self.session_start_time).total_seconds()
        self.idle_time = (now - self.last_interaction_time).total_seconds()

        # Enter closure mode if session is long or idle time is significant
        if self.session_duration > self.long_session_threshold:
            logger.info(f"Entering closure mode due to long session: {self.session_duration:.1f}s")
            return True

        if self.idle_time > self.idle_threshold:
            logger.info(f"Entering closure mode due to idle time: {self.idle_time:.1f}s")
            return True

        return False

    def _apply_closure_adjustments(self) -> None:
        """Apply personality adjustments for closure mode."""
        # Adjust personality parameters for closure mode
        adjustments = {
            "verbosity": 0.2,  # More verbose for summaries
            "formality": 0.1,  # Slightly more formal
            "proactivity": 0.3  # More proactive for suggestions
        }

        for param_name, adjustment in adjustments.items():
            current_value = self.parameters.get_parameter_value(param_name)
            self.parameters.set_parameter_value(
                param_name,
                current_value + adjustment,
                reason="session_closure"
            )

        logger.info("Applied closure mode personality adjustments")

    def _reset_closure_adjustments(self) -> None:
        """Reset personality adjustments after leaving closure mode."""
        # Reset personality parameters to pre-closure values
        self.parameters.reset_to_defaults()
        logger.info("Reset personality parameters after closure mode")

    def generate_session_summary(self) -> Dict[str, Any]:
        """
        Generate a summary of the current session.

        Returns:
            Dictionary with session summary
        """
        summary = {
            "duration_minutes": int(self.session_duration / 60),
            "turn_count": self.turn_count,
            "start_time": self.session_start_time.isoformat(),
            "topics": [],
            "actions": []
        }

        # Extract information from memory if available
        if self.memory_manager:
            try:
                # Get turns from memory
                if hasattr(self.memory_manager, 'short_term') and hasattr(self.memory_manager.short_term, 'turns'):
                    turns = self.memory_manager.short_term.turns

                    # Extract topics and actions
                    topics = set()
                    actions = []

                    for turn in turns:
                        if turn["role"] == "user":
                            # Try to extract topics if we have an encoder
                            if hasattr(self.memory_manager, 'encoder') and hasattr(self.memory_manager.encoder, '_extract_topics'):
                                turn_topics = self.memory_manager.encoder._extract_topics(turn["content"])
                                topics.update(turn_topics)

                        # Look for tool calls in system messages
                        if turn["role"] == "system" and "Tool call:" in turn.get("content", ""):
                            tool_match = re.search(r"Tool call: (\w+)", turn.get("content", ""))
                            if tool_match:
                                actions.append(tool_match.group(1))

                    summary["topics"] = list(topics)
                    summary["actions"] = actions

                # Get recent topics if available
                if hasattr(self.memory_manager, 'get_recent_topics'):
                    recent_topics = self.memory_manager.get_recent_topics()
                    if recent_topics:
                        summary["recent_topics"] = recent_topics

            except Exception as e:
                logger.error(f"Error generating session summary: {e}")

        logger.info(f"Generated session summary: {summary}")
        return summary

    def get_closure_message(self) -> str:
        """
        Get a session closure message.

        Returns:
            Session closure message
        """
        if not self.in_closure_mode:
            return ""

        # Generate a closure message based on session summary
        summary = self.session_summary

        message = f"We've been talking for about {summary.get('duration_minutes', 0)} minutes. "

        # Add topic summary if available
        topics = summary.get('topics', [])
        if topics:
            message += f"We discussed topics like {', '.join(topics[:3])}. "

        # Add action summary if available
        actions = summary.get('actions', [])
        if actions:
            action_counts = Counter(actions)
            top_actions = action_counts.most_common(2)
            action_str = ", ".join([f"{action} ({count} times)" for action, count in top_actions])
            message += f"I helped you with {action_str}. "

        # Add closure question
        message += "Would you like me to save a summary of our conversation for next time? Or is there anything else you'd like to discuss before we wrap up?"

        return message

    def get_session_state(self) -> Dict[str, Any]:
        """
        Get the current session state.

        Returns:
            Dictionary with session state
        """
        self.update()

        return {
            "session_duration": self.session_duration,
            "idle_time": self.idle_time,
            "turn_count": self.turn_count,
            "in_closure_mode": self.in_closure_mode,
            "session_summary": self.session_summary
        }

    def reset(self) -> None:
        """Reset the session manager."""
        self.session_start_time = datetime.now()
        self.last_interaction_time = datetime.now()
        self.session_duration = 0
        self.idle_time = 0
        self.turn_count = 0
        self.in_closure_mode = False
        self.session_summary = {}

        logger.info("Reset session manager")
