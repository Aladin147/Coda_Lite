#!/usr/bin/env python3
"""
Test script for the Enhanced Personality Features.
"""

import sys
import os
import logging
from datetime import datetime

# Add the parent directory to the path so we can import the modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("test.enhanced_personality_features")

# Import the necessary modules
from personality import EnhancedPersonalityLoader

# Mock memory manager for testing
class MockMemoryManager:
    def get_recent_topics(self, limit=3):
        return ["weather", "time", "jokes"]
        
    def get_last_tool_used(self):
        return "get_time"
        
    def get_user_preferences(self):
        return {"voice": "en-US", "response_length": "brief"}
        
    def get_conversation_summary(self):
        return "User asked about the time and weather, and requested a joke."
        
    def get_turn_count(self):
        return 5

def test_response_formatting():
    """Test response formatting with templates and styling."""
    logger.info("Testing response formatting...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test responses with different types
    responses = [
        ("Hello, how can I help you today?", "greeting"),
        ("I'll set an alarm for 7:00 AM tomorrow.", None),
        ("I've added that to your shopping list.", "confirmation"),
        ("I can't access your email account.", "refusal"),
        ("Is there anything else you'd like to know?", "farewell"),
        ("I encountered an error while processing that.", "error")
    ]
    
    for response, response_type in responses:
        logger.info(f"\nOriginal ({response_type}): {response}")
        formatted = personality.format_response(response, response_type)
        logger.info(f"Formatted: {formatted}")
    
    logger.info("Response formatting tests completed successfully")

def test_emotional_responses():
    """Test emotional response formatting."""
    logger.info("\nTesting emotional responses...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test with different emotion modes
    emotion_modes = ["off", "lite", "full"]
    emotions = ["positive", "negative", "surprise", "neutral"]
    
    for mode in emotion_modes:
        personality.set_emotion_mode(mode)
        logger.info(f"\nEmotion mode: {mode}")
        
        for emotion in emotions:
            logger.info(f"  User emotion: {emotion}")
            response = "I've found the information you requested."
            formatted = personality.format_response(response, user_emotion=emotion)
            logger.info(f"  Response: {formatted}")
    
    logger.info("Emotional response tests completed successfully")

def test_memory_hint_extraction():
    """Test memory hint extraction."""
    logger.info("\nTesting memory hint extraction...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Create a mock memory manager
    memory_manager = MockMemoryManager()
    
    # Test extracting memory hints
    hints = personality.extract_memory_hint(memory_manager, max_hints=3)
    
    logger.info("Extracted memory hints:")
    for hint in hints:
        logger.info(f"- {hint}")
    
    logger.info("Memory hint extraction tests completed successfully")

def test_prompt_with_memory_hints():
    """Test system prompt generation with memory hints."""
    logger.info("\nTesting system prompt generation with memory hints...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Create a mock memory manager
    memory_manager = MockMemoryManager()
    
    # Test generating prompts with memory hints
    contexts = ["default", "tool_detection", "summarization"]
    
    for context in contexts:
        logger.info(f"\nPrompt for {context} context with memory hints:")
        prompt = personality.generate_system_prompt(context, memory_manager)
        print(f"\n{prompt}\n")
    
    logger.info("Prompt with memory hints tests completed successfully")

def test_emotion_detection():
    """Test emotion detection from text."""
    logger.info("\nTesting emotion detection...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test detecting emotions from different inputs
    inputs = [
        "I'm really happy with the results!",
        "This is terrible, I hate it.",
        "Wow, that's amazing!",
        "Please tell me the time.",
        "Thanks for your help, I appreciate it.",
        "I'm having a problem with this feature.",
        "Oh my god, I can't believe it worked!"
    ]
    
    for user_input in inputs:
        emotion = personality.detect_emotion(user_input)
        logger.info(f"Input: '{user_input}' → Emotion: {emotion}")
    
    logger.info("Emotion detection tests completed successfully")

def test_mood_tracking():
    """Test mood tracking and personality drift."""
    logger.info("\nTesting mood tracking and personality drift...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Initial mood weights
    logger.info("Initial mood weights:")
    for mood, weight in personality.mood_weights.items():
        logger.info(f"- {mood}: {weight:.2f}")
    
    # Simulate a series of interactions
    interactions = [
        ("What time is it?", "tool_call"),
        ("Tell me a joke", "entertainment"),
        ("What's the weather like?", "information"),
        ("That's funny!", "casual"),
        ("Play some music", "entertainment"),
        ("How many turns in our conversation?", "tool_call"),
        ("Thanks, that's great!", "casual"),
        ("Tell me another joke", "entertainment")
    ]
    
    logger.info("\nSimulating interactions...")
    for i, (user_input, context) in enumerate(interactions):
        personality.update_mood(user_input, context)
        logger.info(f"Interaction {i+1}: '{user_input}' ({context})")
    
    # Final mood weights
    logger.info("\nFinal mood weights after interactions:")
    for mood, weight in personality.mood_weights.items():
        logger.info(f"- {mood}: {weight:.2f}")
    
    # Get traits before and after mood changes
    logger.info("\nTraits with mood influence:")
    traits = personality.get_traits_for_context("default")
    for trait in traits:
        logger.info(f"- {trait.get('trait')} (adjusted strength: {trait.get('adjusted_strength', 'N/A')})")
    
    logger.info("Mood tracking tests completed successfully")

def main():
    """Run all tests."""
    logger.info("Starting Enhanced Personality Features tests...")
    
    # Run the tests
    test_response_formatting()
    test_emotional_responses()
    test_memory_hint_extraction()
    test_prompt_with_memory_hints()
    test_emotion_detection()
    test_mood_tracking()
    
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    main()
