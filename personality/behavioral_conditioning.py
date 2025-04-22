"""
Behavioral conditioning system for Coda Lite.

This module provides a system for tracking and adapting to user behavior patterns,
allowing Coda to adjust its personality based on user preferences.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple

from .parameters import PersonalityParameters

logger = logging.getLogger("coda.personality.behavioral_conditioning")

class BehavioralConditioner:
    """
    Tracks and adapts to user behavior patterns.
    
    This class:
    - Analyzes user interactions for behavioral patterns
    - Detects user preferences for response style
    - Adjusts personality parameters based on observed patterns
    - Maintains a behavior profile in long-term memory
    """
    
    def __init__(self, 
                 memory_manager=None, 
                 personality_parameters: Optional[PersonalityParameters] = None):
        """
        Initialize the behavioral conditioner.
        
        Args:
            memory_manager: Memory manager for storing behavior profiles
            personality_parameters: Personality parameters to adjust
        """
        self.memory_manager = memory_manager
        
        # Initialize personality parameters
        if personality_parameters:
            self.parameters = personality_parameters
        else:
            self.parameters = PersonalityParameters()
        
        # Initialize behavior profile
        self.behavior_profile = self._load_behavior_profile()
        
        # Patterns for detecting preferences
        self.preference_patterns = {
            "verbosity": {
                "increase": [
                    r"(?:more|longer|detailed|elaborate|in-depth|comprehensive)",
                    r"(?:tell me more|explain more|give me details|be more specific)"
                ],
                "decrease": [
                    r"(?:shorter|briefer|concise|to the point|less verbose|too long)",
                    r"(?:be brief|keep it short|summarize|too much detail)"
                ]
            },
            "assertiveness": {
                "increase": [
                    r"(?:more assertive|more confident|more direct|stronger|firmer)",
                    r"(?:be more assertive|be more direct|don't hedge)"
                ],
                "decrease": [
                    r"(?:less assertive|gentler|softer|more tentative|too harsh)",
                    r"(?:be gentler|be less direct|tone it down)"
                ]
            },
            "humor": {
                "increase": [
                    r"(?:funnier|more humor|more jokes|lighten up|more fun)",
                    r"(?:be funnier|make me laugh|add some humor)"
                ],
                "decrease": [
                    r"(?:less humor|more serious|fewer jokes|too funny)",
                    r"(?:be more serious|no jokes|less joking)"
                ]
            },
            "formality": {
                "increase": [
                    r"(?:more formal|more professional|less casual)",
                    r"(?:be more formal|be more professional|speak formally)"
                ],
                "decrease": [
                    r"(?:less formal|more casual|more relaxed|too formal|too stiff)",
                    r"(?:be more casual|relax|speak casually|loosen up)"
                ]
            },
            "proactivity": {
                "increase": [
                    r"(?:more proactive|more suggestions|more ideas|take initiative)",
                    r"(?:be more proactive|suggest more|offer ideas)"
                ],
                "decrease": [
                    r"(?:less proactive|fewer suggestions|too many suggestions)",
                    r"(?:be less proactive|wait for me to ask|don't suggest)"
                ]
            }
        }
        
        # Recent interactions for pattern detection
        self.recent_interactions = []
        self.max_recent_interactions = 20
        
        logger.info("Initialized behavioral conditioner")
    
    def _load_behavior_profile(self) -> Dict[str, Any]:
        """
        Load behavior profile from memory manager or create default.
        
        Returns:
            Behavior profile dictionary
        """
        if self.memory_manager and hasattr(self.memory_manager, 'get_user_summary'):
            profile = self.memory_manager.get_user_summary("behavior_profile")
            if profile:
                logger.info(f"Loaded behavior profile from memory")
                return profile
        
        # Create default profile
        default_profile = {
            "verbosity": 0.5,
            "assertiveness": 0.5,
            "humor": 0.3,
            "formality": 0.5,
            "proactivity": 0.4,
            "confidence": 0.1,  # Low initial confidence
            "last_updated": datetime.now().isoformat(),
            "observation_count": 0
        }
        
        logger.info("Created default behavior profile")
        return default_profile
    
    def _save_behavior_profile(self) -> None:
        """Save behavior profile to memory manager."""
        if self.memory_manager and hasattr(self.memory_manager, 'update_user_summary'):
            self.memory_manager.update_user_summary("behavior_profile", self.behavior_profile)
            logger.info("Saved behavior profile to memory")
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input for behavioral patterns.
        
        Args:
            user_input: User input text
            
        Returns:
            Dictionary of detected preferences
        """
        # Add to recent interactions
        self.recent_interactions.append({
            "text": user_input,
            "timestamp": datetime.now().isoformat(),
            "type": "user_input"
        })
        
        # Trim if needed
        if len(self.recent_interactions) > self.max_recent_interactions:
            self.recent_interactions = self.recent_interactions[-self.max_recent_interactions:]
        
        # Detect explicit preferences
        preferences = self._detect_explicit_preferences(user_input)
        
        # Apply detected preferences
        if preferences:
            self._apply_preferences(preferences, confidence=0.8)  # High confidence for explicit preferences
        
        return preferences
    
    def process_user_feedback(self, user_feedback: str) -> Dict[str, Any]:
        """
        Process user feedback for behavioral patterns.
        
        Args:
            user_feedback: User feedback text
            
        Returns:
            Dictionary of detected preferences
        """
        # Add to recent interactions
        self.recent_interactions.append({
            "text": user_feedback,
            "timestamp": datetime.now().isoformat(),
            "type": "user_feedback"
        })
        
        # Detect explicit preferences
        preferences = self._detect_explicit_preferences(user_feedback)
        
        # Apply detected preferences with high confidence
        if preferences:
            self._apply_preferences(preferences, confidence=0.9)  # Very high confidence for explicit feedback
        
        return preferences
    
    def _detect_explicit_preferences(self, text: str) -> Dict[str, float]:
        """
        Detect explicit preferences in text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary of parameter names and adjustment values
        """
        preferences = {}
        
        # Check each parameter for preference patterns
        for param_name, patterns in self.preference_patterns.items():
            # Check for increase patterns
            for pattern in patterns["increase"]:
                if re.search(pattern, text, re.IGNORECASE):
                    preferences[param_name] = 0.1  # Small increase
                    logger.info(f"Detected preference to increase {param_name}")
                    break
            
            # Check for decrease patterns
            for pattern in patterns["decrease"]:
                if re.search(pattern, text, re.IGNORECASE):
                    preferences[param_name] = -0.1  # Small decrease
                    logger.info(f"Detected preference to decrease {param_name}")
                    break
        
        return preferences
    
    def _apply_preferences(self, preferences: Dict[str, float], confidence: float = 0.5) -> None:
        """
        Apply detected preferences to behavior profile and parameters.
        
        Args:
            preferences: Dictionary of parameter names and adjustment values
            confidence: Confidence in the preferences (0.0 to 1.0)
        """
        if not preferences:
            return
        
        # Update behavior profile
        for param_name, adjustment in preferences.items():
            current_value = self.behavior_profile.get(param_name, 0.5)
            
            # Apply adjustment with confidence weighting
            weighted_adjustment = adjustment * confidence
            new_value = max(0.0, min(current_value + weighted_adjustment, 1.0))
            
            # Update profile
            self.behavior_profile[param_name] = new_value
            logger.info(f"Updated behavior profile {param_name}: {current_value} -> {new_value}")
        
        # Update confidence and metadata
        self.behavior_profile["confidence"] = min(
            self.behavior_profile.get("confidence", 0.1) + 0.05,
            0.9  # Cap confidence at 0.9
        )
        self.behavior_profile["last_updated"] = datetime.now().isoformat()
        self.behavior_profile["observation_count"] = self.behavior_profile.get("observation_count", 0) + 1
        
        # Save updated profile
        self._save_behavior_profile()
        
        # Apply to personality parameters if confidence is high enough
        if self.behavior_profile.get("confidence", 0) >= 0.3:
            self._apply_to_parameters()
    
    def _apply_to_parameters(self) -> None:
        """Apply behavior profile to personality parameters."""
        for param_name, value in self.behavior_profile.items():
            if param_name in ["confidence", "last_updated", "observation_count"]:
                continue
                
            if param_name in self.parameters.get_all_parameters():
                current_value = self.parameters.get_parameter_value(param_name)
                
                # Only update if there's a significant difference
                if abs(current_value - value) >= 0.1:
                    self.parameters.set_parameter_value(
                        param_name, 
                        value, 
                        reason=f"behavior_profile (confidence: {self.behavior_profile.get('confidence', 0):.2f})"
                    )
    
    def analyze_interaction_patterns(self) -> Dict[str, Any]:
        """
        Analyze recent interactions for patterns.
        
        Returns:
            Dictionary of detected patterns
        """
        if len(self.recent_interactions) < 5:
            return {}  # Not enough data
        
        patterns = {}
        
        # Analyze message length preferences
        user_message_lengths = [
            len(interaction["text"])
            for interaction in self.recent_interactions
            if interaction["type"] == "user_input"
        ]
        
        if user_message_lengths:
            avg_length = sum(user_message_lengths) / len(user_message_lengths)
            
            # Infer verbosity preference
            if avg_length < 50:
                patterns["verbosity"] = -0.05  # User tends to be brief, might prefer brief responses
            elif avg_length > 150:
                patterns["verbosity"] = 0.05  # User tends to be verbose, might prefer detailed responses
        
        # Analyze question frequency
        question_count = sum(
            1 for interaction in self.recent_interactions
            if interaction["type"] == "user_input" and "?" in interaction["text"]
        )
        
        if len(self.recent_interactions) > 0:
            question_ratio = question_count / len(self.recent_interactions)
            
            # Infer proactivity preference
            if question_ratio > 0.7:
                patterns["proactivity"] = -0.05  # User asks many questions, might prefer reactive responses
            elif question_ratio < 0.3:
                patterns["proactivity"] = 0.05  # User asks few questions, might prefer proactive responses
        
        # Apply detected patterns with low confidence
        if patterns:
            self._apply_preferences(patterns, confidence=0.2)  # Low confidence for inferred patterns
        
        return patterns
    
    def get_behavior_profile(self) -> Dict[str, Any]:
        """
        Get the current behavior profile.
        
        Returns:
            Behavior profile dictionary
        """
        return self.behavior_profile
    
    def get_parameter_recommendations(self) -> Dict[str, float]:
        """
        Get recommended parameter values based on behavior profile.
        
        Returns:
            Dictionary of parameter names and recommended values
        """
        recommendations = {}
        
        for param_name, value in self.behavior_profile.items():
            if param_name in ["confidence", "last_updated", "observation_count"]:
                continue
                
            # Only recommend if confidence is high enough
            if self.behavior_profile.get("confidence", 0) >= 0.3:
                recommendations[param_name] = value
        
        return recommendations
    
    def reset(self) -> None:
        """Reset the behavioral conditioner."""
        # Create default profile
        self.behavior_profile = {
            "verbosity": 0.5,
            "assertiveness": 0.5,
            "humor": 0.3,
            "formality": 0.5,
            "proactivity": 0.4,
            "confidence": 0.1,
            "last_updated": datetime.now().isoformat(),
            "observation_count": 0
        }
        
        # Clear recent interactions
        self.recent_interactions = []
        
        # Save reset profile
        self._save_behavior_profile()
        
        logger.info("Reset behavioral conditioner")
