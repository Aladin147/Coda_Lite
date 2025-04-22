#!/usr/bin/env python3
"""
Test script for the Enhanced Personality System.
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
logger = logging.getLogger("test.enhanced_personality")

# Import the necessary modules
from personality import EnhancedPersonalityLoader

def test_basic_functionality():
    """Test basic functionality of the enhanced personality loader."""
    logger.info("Testing basic functionality...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test basic getters
    logger.info(f"Name: {personality.get_name()}")
    logger.info(f"Role: {personality.get_role()}")
    
    # Test getting traits for different contexts
    logger.info("\nTraits for default context:")
    default_traits = personality.get_traits_for_context("default")
    for trait in default_traits:
        logger.info(f"- {trait.get('trait')} (strength: {trait.get('strength')})")
    
    logger.info("\nTraits for tool_call context:")
    tool_traits = personality.get_traits_for_context("tool_call")
    for trait in tool_traits:
        logger.info(f"- {trait.get('trait')} (strength: {trait.get('strength')})")
    
    logger.info("\nTraits for casual context:")
    casual_traits = personality.get_traits_for_context("casual")
    for trait in casual_traits:
        logger.info(f"- {trait.get('trait')} (strength: {trait.get('strength')})")
    
    logger.info("Basic functionality tests completed successfully")

def test_tone_switching():
    """Test adaptive tone switching."""
    logger.info("\nTesting adaptive tone switching...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test getting tones for different contexts
    contexts = ["default", "tool_call", "information", "casual", "entertainment", "error", "formal", "emergency"]
    for context in contexts:
        tone = personality.get_tone(context)
        logger.info(f"Tone for {context} context: {tone}")
    
    logger.info("Tone switching tests completed successfully")

def test_quirks():
    """Test personality quirks."""
    logger.info("\nTesting personality quirks...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test getting quirks for different triggers
    triggers = ["time", "number", "waiting", "identity", "developer"]
    for trigger in triggers:
        quirk = personality.get_quirk_for_trigger(trigger)
        if quirk:
            logger.info(f"Quirk for {trigger}: {quirk.get('quirk')}")
            logger.info(f"  Frequency: {quirk.get('frequency')}")
            logger.info(f"  Examples: {quirk.get('examples')}")
        else:
            logger.info(f"No quirk found for trigger: {trigger}")
    
    # Test applying quirks
    responses = [
        "It's 3:45 PM.",
        "The answer is 42.",
        "I'm thinking about your question.",
        "I'm an AI assistant designed to help you.",
        "Let me help you with that code."
    ]
    
    for response in responses:
        quirky_response = personality.apply_quirk(response)
        logger.info(f"Original: {response}")
        logger.info(f"With quirk: {quirky_response}")
        logger.info("")
    
    logger.info("Quirk tests completed successfully")

def test_prompt_generation():
    """Test system prompt generation."""
    logger.info("\nTesting system prompt generation...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test generating prompts for different contexts
    contexts = ["default", "tool_detection", "summarization"]
    for context in contexts:
        logger.info(f"\nPrompt for {context} context:")
        prompt = personality.generate_system_prompt(context)
        print(f"\n{prompt}\n")
    
    logger.info("Prompt generation tests completed successfully")

def test_context_detection():
    """Test context detection from user input."""
    logger.info("\nTesting context detection...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Test detecting context from different user inputs
    inputs = [
        "What time is it?",
        "Tell me a joke",
        "Help! There's an emergency!",
        "Hi, how are you today?",
        "Can you tell me a fun story?",
        "What's the capital of France?",
        "Thanks for your help"
    ]
    
    for user_input in inputs:
        context = personality.detect_context(user_input)
        logger.info(f"Input: '{user_input}' → Context: {context}")
    
    logger.info("Context detection tests completed successfully")

def test_live_reloading():
    """Test live reloading of personality."""
    logger.info("\nTesting live reloading...")
    
    # Create an instance of the enhanced personality loader
    personality = EnhancedPersonalityLoader()
    
    # Get initial traits
    logger.info("Initial traits:")
    initial_traits = personality.get_traits_for_context("default")
    for trait in initial_traits:
        logger.info(f"- {trait.get('trait')}")
    
    # Reload the personality
    logger.info("\nReloading personality...")
    result = personality.reload()
    logger.info(result)
    
    # Get traits after reload
    logger.info("\nTraits after reload:")
    reloaded_traits = personality.get_traits_for_context("default")
    for trait in reloaded_traits:
        logger.info(f"- {trait.get('trait')}")
    
    logger.info("Live reloading tests completed successfully")

def main():
    """Run all tests."""
    logger.info("Starting Enhanced Personality System tests...")
    
    # Run the tests
    test_basic_functionality()
    test_tone_switching()
    test_quirks()
    test_prompt_generation()
    test_context_detection()
    test_live_reloading()
    
    logger.info("All tests completed successfully")

if __name__ == "__main__":
    main()
