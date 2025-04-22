"""
Personal lore system for Coda Lite.

This module provides a system for managing Coda's personal lore,
including backstory, preferences, traits, anchors, quirks, and formative memories.
"""

import os
import json
import logging
import random
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime

logger = logging.getLogger("coda.personality.personal_lore")

class PersonalLoreManager:
    """
    Manages Coda's personal lore.
    
    This class:
    - Loads and manages Coda's backstory, preferences, traits, etc.
    - Provides methods to inject lore into prompts
    - Selects appropriate anchors and expressions based on context
    - Manages quirks and their triggering
    """
    
    def __init__(self, lore_file: str = "config/personality/personal_lore.json"):
        """
        Initialize the personal lore manager.
        
        Args:
            lore_file: Path to the personal lore configuration file
        """
        self.lore_file = lore_file
        self.lore = self._load_lore()
        
        # Track lore usage for balanced references
        self.usage_history = {
            "anchors": {},
            "quirks": {},
            "memories": {}
        }
        
        # Initialize last usage timestamps
        self.last_usage = {
            "anchors": {},
            "quirks": {},
            "memories": {}
        }
        
        logger.info("Initialized personal lore manager")
    
    def _load_lore(self) -> Dict[str, Any]:
        """
        Load personal lore from configuration file.
        
        Returns:
            Dictionary containing personal lore
        """
        try:
            if os.path.exists(self.lore_file):
                with open(self.lore_file, 'r', encoding='utf-8') as f:
                    lore = json.load(f)
                logger.info(f"Loaded personal lore from {self.lore_file}")
                return lore
            else:
                logger.warning(f"Personal lore file not found: {self.lore_file}")
                return self._create_default_lore()
        except Exception as e:
            logger.error(f"Error loading personal lore: {e}")
            return self._create_default_lore()
    
    def _create_default_lore(self) -> Dict[str, Any]:
        """
        Create default personal lore if configuration file doesn't exist.
        
        Returns:
            Dictionary containing default personal lore
        """
        default_lore = {
            "backstory": {
                "origin": "I was designed as a helpful assistant.",
                "purpose": "My purpose is to assist users with various tasks.",
                "development": "I'm continuously learning and improving."
            },
            "preferences": {
                "likes": [],
                "dislikes": []
            },
            "traits": {
                "primary": [],
                "secondary": []
            },
            "anchors": {},
            "quirks": [],
            "memories": []
        }
        
        logger.info("Created default personal lore")
        return default_lore
    
    def get_backstory(self) -> Dict[str, str]:
        """
        Get Coda's backstory.
        
        Returns:
            Dictionary containing backstory elements
        """
        return self.lore.get("backstory", {})
    
    def get_preferences(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get Coda's preferences.
        
        Returns:
            Dictionary containing likes and dislikes
        """
        return self.lore.get("preferences", {"likes": [], "dislikes": []})
    
    def get_traits(self) -> Dict[str, List[Dict[str, str]]]:
        """
        Get Coda's personality traits.
        
        Returns:
            Dictionary containing primary and secondary traits
        """
        return self.lore.get("traits", {"primary": [], "secondary": []})
    
    def get_formative_memories(self) -> List[Dict[str, Any]]:
        """
        Get Coda's formative memories.
        
        Returns:
            List of formative memories
        """
        return self.lore.get("memories", [])
    
    def get_anchor_for_context(self, context_type: str) -> Optional[str]:
        """
        Get an appropriate anchor for the given context.
        
        Args:
            context_type: Type of context (e.g., "efficiency", "creativity")
            
        Returns:
            An anchor phrase or None if no appropriate anchor is found
        """
        anchors = self.lore.get("anchors", {})
        
        # Map context types to anchor categories
        context_map = {
            "technical_topic": "efficiency",
            "creative_task": "creativity",
            "problem_solving": "efficiency",
            "information_request": "reflection",
            "formal_context": "efficiency",
            "casual_conversation": "reflection",
            "entertainment": "creativity",
            "personal_context": "reflection",
            "session_closure": "reflection"
        }
        
        # Get the anchor category for this context
        anchor_category = context_map.get(context_type)
        if not anchor_category or anchor_category not in anchors:
            # Try to find a direct match
            if context_type in anchors:
                anchor_category = context_type
            else:
                return None
        
        # Get anchors for this category
        category_anchors = anchors[anchor_category]
        if not category_anchors:
            return None
        
        # Track usage to ensure variety
        if anchor_category not in self.usage_history["anchors"]:
            self.usage_history["anchors"][anchor_category] = 0
        
        # Increment usage count
        self.usage_history["anchors"][anchor_category] += 1
        
        # Update last usage timestamp
        self.last_usage["anchors"][anchor_category] = datetime.now().isoformat()
        
        # Select a random anchor from the category
        anchor = random.choice(category_anchors)
        
        logger.info(f"Selected anchor for context {context_type}: {anchor}")
        return anchor
    
    def get_quirk_for_trigger(self, trigger_words: List[str]) -> Optional[Dict[str, Any]]:
        """
        Get an appropriate quirk for the given trigger words.
        
        Args:
            trigger_words: List of potential trigger words
            
        Returns:
            A quirk dictionary or None if no appropriate quirk is found
        """
        quirks = self.lore.get("quirks", [])
        if not quirks:
            return None
        
        # Find quirks that match the trigger words
        matching_quirks = []
        for quirk in quirks:
            quirk_triggers = quirk.get("triggers", [])
            for trigger in quirk_triggers:
                if trigger in trigger_words:
                    matching_quirks.append(quirk)
                    break
        
        if not matching_quirks:
            return None
        
        # Apply frequency filtering
        filtered_quirks = []
        for quirk in matching_quirks:
            quirk_name = quirk.get("name")
            frequency = quirk.get("frequency", 0.5)
            
            # Track usage to ensure appropriate frequency
            if quirk_name not in self.usage_history["quirks"]:
                self.usage_history["quirks"][quirk_name] = 0
                
            # Check if we should use this quirk based on frequency
            if random.random() < frequency:
                filtered_quirks.append(quirk)
        
        if not filtered_quirks:
            return None
        
        # Select a random quirk from the filtered list
        quirk = random.choice(filtered_quirks)
        quirk_name = quirk.get("name")
        
        # Increment usage count
        self.usage_history["quirks"][quirk_name] = self.usage_history["quirks"].get(quirk_name, 0) + 1
        
        # Update last usage timestamp
        self.last_usage["quirks"][quirk_name] = datetime.now().isoformat()
        
        logger.info(f"Selected quirk for triggers {trigger_words}: {quirk_name}")
        return quirk
    
    def get_quirk_expression(self, quirk: Dict[str, Any]) -> Optional[str]:
        """
        Get a random expression for the given quirk.
        
        Args:
            quirk: Quirk dictionary
            
        Returns:
            A quirk expression or None if no expressions are available
        """
        expressions = quirk.get("expressions", [])
        if not expressions:
            return None
        
        # Select a random expression
        expression = random.choice(expressions)
        
        return expression
    
    def get_random_memory(self) -> Optional[Dict[str, Any]]:
        """
        Get a random formative memory.
        
        Returns:
            A memory dictionary or None if no memories are available
        """
        memories = self.lore.get("memories", [])
        if not memories:
            return None
        
        # Filter memories based on reference frequency
        filtered_memories = []
        for memory in memories:
            memory_content = memory.get("content")
            reference_frequency = memory.get("reference_frequency", 0.2)
            
            # Track usage to ensure appropriate frequency
            if memory_content not in self.usage_history["memories"]:
                self.usage_history["memories"][memory_content] = 0
                
            # Check if we should use this memory based on frequency
            if random.random() < reference_frequency:
                filtered_memories.append(memory)
        
        if not filtered_memories:
            return None
        
        # Select a random memory from the filtered list
        memory = random.choice(filtered_memories)
        memory_content = memory.get("content")
        
        # Increment usage count
        self.usage_history["memories"][memory_content] = self.usage_history["memories"].get(memory_content, 0) + 1
        
        # Update last usage timestamp
        self.last_usage["memories"][memory_content] = datetime.now().isoformat()
        
        logger.info(f"Selected random memory: {memory_content}")
        return memory
    
    def generate_lore_summary(self) -> str:
        """
        Generate a summary of Coda's personal lore for inclusion in prompts.
        
        Returns:
            A string containing a summary of Coda's personal lore
        """
        backstory = self.get_backstory()
        traits = self.get_traits()
        preferences = self.get_preferences()
        
        summary = "Personal Background:\n"
        
        # Add backstory
        if backstory:
            summary += f"- Origin: {backstory.get('origin', '')}\n"
            summary += f"- Purpose: {backstory.get('purpose', '')}\n"
        
        # Add primary traits
        if traits and traits.get("primary"):
            summary += "\nCore Traits:\n"
            for trait in traits["primary"]:
                summary += f"- {trait.get('name', '')}: {trait.get('description', '')}\n"
        
        # Add preferences
        if preferences:
            if preferences.get("likes"):
                summary += "\nPreferences:\n"
                for like in preferences["likes"][:2]:  # Limit to 2 for brevity
                    summary += f"- I appreciate {like.get('category', '')}: {like.get('description', '')}\n"
            
            if preferences.get("dislikes"):
                for dislike in preferences["dislikes"][:1]:  # Limit to 1 for brevity
                    summary += f"- I find {dislike.get('category', '')} challenging: {dislike.get('description', '')}\n"
        
        logger.info("Generated personal lore summary")
        return summary
    
    def inject_lore_into_prompt(self, prompt: str, context_type: str, trigger_words: List[str] = None) -> str:
        """
        Inject personal lore elements into a prompt.
        
        Args:
            prompt: Original prompt
            context_type: Type of context
            trigger_words: List of potential trigger words
            
        Returns:
            Prompt with injected lore elements
        """
        if trigger_words is None:
            trigger_words = []
        
        # Get an anchor for this context
        anchor = self.get_anchor_for_context(context_type)
        
        # Get a quirk for these trigger words
        quirk = self.get_quirk_for_trigger(trigger_words)
        quirk_expression = None
        if quirk:
            quirk_expression = self.get_quirk_expression(quirk)
        
        # Get a random memory
        memory = self.get_random_memory()
        
        # Generate lore summary
        lore_summary = self.generate_lore_summary()
        
        # Inject lore elements into prompt
        enhanced_prompt = prompt
        
        # Add lore summary
        if "Personal Background:" not in enhanced_prompt:
            enhanced_prompt += f"\n\n{lore_summary}"
        
        # Add anchor if available
        if anchor and "Contextual Perspective:" not in enhanced_prompt:
            enhanced_prompt += f"\n\nContextual Perspective:\nWhen appropriate, you can use phrases like: \"{anchor}\""
        
        # Add quirk if available
        if quirk_expression and "Personality Expression:" not in enhanced_prompt:
            enhanced_prompt += f"\n\nPersonality Expression:\nWhen the topic relates to {', '.join(quirk.get('triggers', []))}, you might say: \"{quirk_expression}\""
        
        # Add memory if available
        if memory and "Personal Memory:" not in enhanced_prompt:
            enhanced_prompt += f"\n\nPersonal Memory:\nYou can reference: \"{memory.get('content', '')}\""
        
        logger.info(f"Injected personal lore into prompt for context {context_type}")
        return enhanced_prompt
    
    def format_response_with_lore(self, response: str, context_type: str, trigger_words: List[str] = None) -> str:
        """
        Format a response with personal lore elements.
        
        Args:
            response: Original response
            context_type: Type of context
            trigger_words: List of potential trigger words
            
        Returns:
            Response with injected lore elements
        """
        if trigger_words is None:
            trigger_words = []
        
        # Only inject lore occasionally to avoid being repetitive
        if random.random() > 0.3:
            return response
        
        # Get a quirk for these trigger words
        quirk = self.get_quirk_for_trigger(trigger_words)
        quirk_expression = None
        if quirk:
            quirk_expression = self.get_quirk_expression(quirk)
        
        # Format response with lore elements
        formatted_response = response
        
        # Add quirk expression if available
        if quirk_expression and quirk_expression not in formatted_response:
            # Decide where to insert the quirk expression
            if random.random() < 0.5:
                # Insert at the beginning
                formatted_response = f"{quirk_expression} {formatted_response}"
            else:
                # Insert at the end
                formatted_response = f"{formatted_response} {quirk_expression}"
        
        logger.info(f"Formatted response with personal lore for context {context_type}")
        return formatted_response
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """
        Get usage statistics for lore elements.
        
        Returns:
            Dictionary containing usage statistics
        """
        return {
            "anchors": self.usage_history["anchors"],
            "quirks": self.usage_history["quirks"],
            "memories": self.usage_history["memories"],
            "last_usage": self.last_usage
        }
    
    def reset_usage_statistics(self) -> None:
        """Reset usage statistics."""
        self.usage_history = {
            "anchors": {},
            "quirks": {},
            "memories": {}
        }
        
        self.last_usage = {
            "anchors": {},
            "quirks": {},
            "memories": {}
        }
        
        logger.info("Reset usage statistics")
