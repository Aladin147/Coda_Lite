#!/usr/bin/env python3
"""
Test script for the personal lore system.
"""

import os
import sys
import json
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
logger = logging.getLogger("test.personal_lore")

# Import the personality modules
from personality import (
    PersonalLoreManager,
    AdvancedPersonalityManager
)

# Import memory modules for integration testing
from memory import EnhancedMemoryManager

def load_config():
    """Load configuration from file."""
    import yaml
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_personal_lore_manager():
    """Test the PersonalLoreManager class."""
    print("\n" + "=" * 50)
    print("Testing PersonalLoreManager")
    print("=" * 50)
    
    # Initialize personal lore manager
    lore_manager = PersonalLoreManager()
    
    # Test getting backstory
    print("\nBackstory:")
    backstory = lore_manager.get_backstory()
    for key, value in backstory.items():
        print(f"- {key}: {value}")
    
    # Test getting preferences
    print("\nPreferences:")
    preferences = lore_manager.get_preferences()
    
    print("\nLikes:")
    for like in preferences.get("likes", [])[:2]:  # Show first 2 for brevity
        print(f"- {like.get('category')}: {like.get('description')}")
    
    print("\nDislikes:")
    for dislike in preferences.get("dislikes", [])[:2]:  # Show first 2 for brevity
        print(f"- {dislike.get('category')}: {dislike.get('description')}")
    
    # Test getting traits
    print("\nTraits:")
    traits = lore_manager.get_traits()
    
    print("\nPrimary Traits:")
    for trait in traits.get("primary", [])[:2]:  # Show first 2 for brevity
        print(f"- {trait.get('name')}: {trait.get('description')}")
    
    print("\nSecondary Traits:")
    for trait in traits.get("secondary", [])[:2]:  # Show first 2 for brevity
        print(f"- {trait.get('name')}: {trait.get('description')}")
    
    # Test getting anchors
    print("\nTesting anchors for different contexts:")
    contexts = ["technical_topic", "creative_task", "formal_context", "personal_context", "entertainment"]
    for context in contexts:
        anchor = lore_manager.get_anchor_for_context(context)
        print(f"- {context}: {anchor}")
    
    # Test getting quirks
    print("\nTesting quirks for different triggers:")
    trigger_sets = [
        ["efficiency", "workflow"],
        ["creative", "design"],
        ["technical", "code"]
    ]
    for triggers in trigger_sets:
        quirk = lore_manager.get_quirk_for_trigger(triggers)
        if quirk:
            expression = lore_manager.get_quirk_expression(quirk)
            print(f"- Triggers {triggers}: {quirk.get('name')} - \"{expression}\"")
        else:
            print(f"- Triggers {triggers}: No matching quirk")
    
    # Test getting random memory
    print("\nRandom memory:")
    memory = lore_manager.get_random_memory()
    if memory:
        print(f"- {memory.get('type')}: {memory.get('content')}")
    else:
        print("- No memory returned")
    
    # Test generating lore summary
    print("\nLore summary:")
    summary = lore_manager.generate_lore_summary()
    print(summary)
    
    # Test injecting lore into prompt
    print("\nTesting lore injection into prompt:")
    original_prompt = "You are Coda, a helpful assistant. Be concise and clear in your responses."
    enhanced_prompt = lore_manager.inject_lore_into_prompt(
        prompt=original_prompt,
        context_type="technical_topic",
        trigger_words=["efficiency", "code"]
    )
    print("\nOriginal prompt:")
    print(original_prompt)
    print("\nEnhanced prompt:")
    print(enhanced_prompt)
    
    # Test formatting response with lore
    print("\nTesting response formatting with lore:")
    original_response = "Here's how you can optimize your code for better performance."
    formatted_response = lore_manager.format_response_with_lore(
        response=original_response,
        context_type="technical_topic",
        trigger_words=["efficiency", "code"]
    )
    print("\nOriginal response:")
    print(original_response)
    print("\nFormatted response:")
    print(formatted_response)
    
    # Test usage statistics
    print("\nUsage statistics:")
    stats = lore_manager.get_usage_statistics()
    print(json.dumps(stats, indent=2))
    
    # Test resetting usage statistics
    lore_manager.reset_usage_statistics()
    print("\nReset usage statistics")
    
    print("\nPersonalLoreManager test completed")

def test_advanced_personality_manager_with_lore():
    """Test the AdvancedPersonalityManager with personal lore integration."""
    print("\n" + "=" * 50)
    print("Testing AdvancedPersonalityManager with Personal Lore")
    print("=" * 50)
    
    # Load config
    config = load_config()
    
    # Create a test memory manager
    memory_config = {
        "memory": {
            "max_turns": 20,
            "max_tokens": 800,
            "export_dir": "data/memory",
            "long_term_enabled": True,
            "long_term_path": "data/memory/test_lore",
            "vector_db": "in_memory"
        }
    }
    
    memory_manager = EnhancedMemoryManager(memory_config)
    
    # Initialize advanced personality manager
    personality_manager = AdvancedPersonalityManager(
        memory_manager=memory_manager,
        config=config
    )
    
    # Test processing user input with different topics
    print("\nTesting user input processing with different topics:")
    
    inputs = [
        "Can you help me optimize this code for better efficiency?",
        "I'm working on a creative design project and need some ideas.",
        "What's your opinion on workflow optimization?",
        "Tell me about your background and what you're designed to do."
    ]
    
    for user_input in inputs:
        print(f"\nUser input: \"{user_input}\"")
        memory_manager.add_turn("user", user_input)
        results = personality_manager.process_user_input(user_input)
        
        # Get current context
        context = personality_manager.get_current_context()
        print(f"Context type: {context.get('type')}")
        print(f"Trigger words: {context.get('trigger_words')}")
        
        # Process a simulated response
        response = f"Here's my response to: {user_input}"
        memory_manager.add_turn("assistant", response)
        personality_manager.process_assistant_response(response)
    
    # Generate system prompt with personal lore
    print("\nGenerating system prompt with personal lore:")
    prompt = personality_manager.generate_system_prompt()
    print("\nSystem prompt (truncated for readability):")
    lines = prompt.split("\n")
    if len(lines) > 20:
        print("\n".join(lines[:10]) + "\n...\n" + "\n".join(lines[-10:]))
    else:
        print(prompt)
    
    # Test response formatting with personal lore
    print("\nTesting response formatting with personal lore:")
    original_response = "I can help you optimize your code for better efficiency. Let's look at your current implementation and identify areas for improvement."
    formatted = personality_manager.format_response(original_response)
    print(f"Original: \"{original_response}\"")
    print(f"Formatted: \"{formatted}\"")
    
    # Get personal lore information
    print("\nPersonal lore information:")
    lore_info = personality_manager.get_personal_lore()
    print("Backstory:")
    for key, value in lore_info.get("backstory", {}).items():
        print(f"- {key}: {value[:50]}..." if len(value) > 50 else f"- {key}: {value}")
    
    print("\nUsage statistics:")
    stats = lore_info.get("usage_statistics", {})
    print(json.dumps(stats, indent=2))
    
    # Reset personality manager
    personality_manager.reset()
    print("\nReset personality manager")
    
    print("\nAdvancedPersonalityManager with Personal Lore test completed")

def main():
    """Run all tests."""
    try:
        test_personal_lore_manager()
        test_advanced_personality_manager_with_lore()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
