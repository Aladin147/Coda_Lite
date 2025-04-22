"""
Topic awareness system for Coda Lite.

This module provides a system for detecting and tracking conversation topics,
allowing Coda to adjust its personality based on the current topic.
"""

import os
import json
import logging
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, Union, Tuple
from collections import Counter

from .parameters import PersonalityParameters

logger = logging.getLogger("coda.personality.topic_awareness")

class TopicAwareness:
    """
    Detects and tracks conversation topics.
    
    This class:
    - Analyzes conversations to identify topics
    - Categorizes topics into domains
    - Tracks topic shifts during conversations
    - Provides topic-based personality adjustments
    """
    
    def __init__(self, 
                 memory_manager=None, 
                 personality_parameters: Optional[PersonalityParameters] = None):
        """
        Initialize the topic awareness system.
        
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
        
        # Load topic categories
        self.topic_categories = self._load_topic_categories()
        
        # Initialize topic tracking
        self.current_topic = None
        self.current_category = None
        self.topic_history = []
        self.max_topic_history = 10
        
        # Topic keywords for detection
        self.topic_keywords = self._build_topic_keywords()
        
        logger.info("Initialized topic awareness system")
    
    def _load_topic_categories(self) -> Dict[str, Dict[str, Any]]:
        """
        Load topic categories from configuration.
        
        Returns:
            Dictionary of topic categories
        """
        categories = {
            "technical": {
                "keywords": ["code", "programming", "software", "hardware", "computer", "technology", 
                            "algorithm", "data", "system", "network", "database", "api", "function",
                            "development", "engineering", "science", "math", "technical", "analysis"],
                "personality_adjustments": {
                    "verbosity": 0.2,
                    "humor": -0.2,
                    "formality": 0.2
                }
            },
            "creative": {
                "keywords": ["art", "design", "music", "writing", "creative", "story", "film", "video",
                            "photography", "drawing", "painting", "compose", "create", "imagination",
                            "inspiration", "aesthetic", "artistic", "visual", "audio", "sound"],
                "personality_adjustments": {
                    "humor": 0.2,
                    "formality": -0.2,
                    "assertiveness": -0.1
                }
            },
            "business": {
                "keywords": ["business", "finance", "marketing", "management", "strategy", "company",
                            "corporate", "market", "product", "service", "client", "customer", "revenue",
                            "profit", "investment", "budget", "project", "meeting", "presentation"],
                "personality_adjustments": {
                    "formality": 0.3,
                    "assertiveness": 0.2,
                    "proactivity": 0.1
                }
            },
            "personal": {
                "keywords": ["family", "friend", "relationship", "personal", "feeling", "emotion",
                            "health", "fitness", "diet", "exercise", "hobby", "interest", "home",
                            "life", "lifestyle", "self", "improvement", "goal", "achievement"],
                "personality_adjustments": {
                    "humor": 0.1,
                    "formality": -0.3,
                    "assertiveness": -0.1
                }
            },
            "entertainment": {
                "keywords": ["game", "movie", "show", "book", "entertainment", "fun", "play", "watch",
                            "listen", "read", "sport", "hobby", "leisure", "relax", "enjoy", "amuse",
                            "comedy", "drama", "action", "adventure", "fantasy", "sci-fi"],
                "personality_adjustments": {
                    "humor": 0.3,
                    "formality": -0.3,
                    "verbosity": -0.1
                }
            },
            "informational": {
                "keywords": ["information", "fact", "news", "report", "article", "research", "study",
                            "learn", "education", "knowledge", "understand", "explain", "describe",
                            "define", "clarify", "detail", "specifics", "data", "statistics"],
                "personality_adjustments": {
                    "verbosity": 0.2,
                    "assertiveness": 0.1,
                    "proactivity": -0.1
                }
            }
        }
        
        return categories
    
    def _build_topic_keywords(self) -> Dict[str, List[str]]:
        """
        Build keyword lists for topic detection.
        
        Returns:
            Dictionary of keywords by topic
        """
        keywords = {}
        
        for category, data in self.topic_categories.items():
            for keyword in data.get("keywords", []):
                if keyword not in keywords:
                    keywords[keyword] = []
                keywords[keyword].append(category)
        
        return keywords
    
    def detect_topic(self, text: str) -> Dict[str, Any]:
        """
        Detect the topic of a text.
        
        Args:
            text: Text to analyze
            
        Returns:
            Dictionary with detected topic information
        """
        # Tokenize and normalize text
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Count category matches
        category_counts = Counter()
        
        for word in words:
            if word in self.topic_keywords:
                for category in self.topic_keywords[word]:
                    category_counts[category] += 1
        
        # Determine primary category
        if not category_counts:
            return {
                "topic": None,
                "category": None,
                "confidence": 0.0,
                "keywords": []
            }
        
        total_matches = sum(category_counts.values())
        primary_category = category_counts.most_common(1)[0][0]
        confidence = category_counts[primary_category] / total_matches
        
        # Extract potential topic keywords
        topic_keywords = [
            word for word in words
            if word in self.topic_keywords and primary_category in self.topic_keywords[word]
        ]
        
        # Determine most likely specific topic
        topic = None
        if topic_keywords:
            # Use the most frequent keyword as the topic
            topic_counter = Counter(topic_keywords)
            topic = topic_counter.most_common(1)[0][0]
        
        result = {
            "topic": topic,
            "category": primary_category,
            "confidence": confidence,
            "keywords": topic_keywords
        }
        
        logger.info(f"Detected topic: {result}")
        
        return result
    
    def process_user_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input for topic detection.
        
        Args:
            user_input: User input text
            
        Returns:
            Dictionary with topic information and adjustments
        """
        # Detect topic
        topic_info = self.detect_topic(user_input)
        
        # Update topic history
        if topic_info["category"]:
            self.topic_history.append({
                "topic": topic_info["topic"],
                "category": topic_info["category"],
                "confidence": topic_info["confidence"],
                "timestamp": datetime.now().isoformat()
            })
            
            # Trim if needed
            if len(self.topic_history) > self.max_topic_history:
                self.topic_history = self.topic_history[-self.max_topic_history:]
            
            # Update current topic if confidence is high enough
            if topic_info["confidence"] >= 0.5:
                self.current_topic = topic_info["topic"]
                self.current_category = topic_info["category"]
                
                # Apply personality adjustments
                self._apply_topic_adjustments(topic_info["category"])
        
        return topic_info
    
    def _apply_topic_adjustments(self, category: str) -> Dict[str, float]:
        """
        Apply personality adjustments based on topic category.
        
        Args:
            category: Topic category
            
        Returns:
            Dictionary of applied adjustments
        """
        if category not in self.topic_categories:
            return {}
        
        adjustments = self.topic_categories[category].get("personality_adjustments", {})
        
        # Apply adjustments to personality parameters
        applied_adjustments = {}
        for param_name, adjustment in adjustments.items():
            if param_name in self.parameters.get_all_parameters():
                current_value = self.parameters.get_parameter_value(param_name)
                
                # Apply adjustment
                self.parameters.set_parameter_value(
                    param_name,
                    current_value + adjustment,
                    reason=f"topic:{category}"
                )
                
                applied_adjustments[param_name] = adjustment
                logger.info(f"Applied topic adjustment to {param_name}: {adjustment} for category {category}")
        
        return applied_adjustments
    
    def get_current_topic(self) -> Dict[str, Any]:
        """
        Get the current conversation topic.
        
        Returns:
            Dictionary with current topic information
        """
        if not self.current_topic:
            return {
                "topic": None,
                "category": None,
                "history": self.topic_history[-3:] if self.topic_history else []
            }
        
        return {
            "topic": self.current_topic,
            "category": self.current_category,
            "history": self.topic_history[-3:] if self.topic_history else []
        }
    
    def get_topic_history(self, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Get recent topic history.
        
        Args:
            limit: Maximum number of history items to return
            
        Returns:
            List of recent topics
        """
        return self.topic_history[-limit:]
    
    def reset(self) -> None:
        """Reset the topic awareness system."""
        self.current_topic = None
        self.current_category = None
        self.topic_history = []
        logger.info("Reset topic awareness system")
