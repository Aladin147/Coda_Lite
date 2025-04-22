#!/usr/bin/env python3
"""
Test script for the intent routing system.
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
logger = logging.getLogger("test.intent_routing")

# Import the intent modules
from intent import IntentRouter, IntentType, IntentHandlers, IntentManager

# Import memory and personality modules for integration testing
from memory import EnhancedMemoryManager
from personality import AdvancedPersonalityManager

def load_config():
    """Load configuration from file."""
    import yaml
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_intent_router():
    """Test the IntentRouter class."""
    print("\n" + "=" * 50)
    print("Testing IntentRouter")
    print("=" * 50)
    
    # Initialize intent router
    router = IntentRouter()
    
    # Test intent detection
    print("\nTesting intent detection:")
    
    test_inputs = [
        "What is the capital of France?",
        "Do you remember what I told you about my job?",
        "Remember that I prefer coffee over tea.",
        "Look up the weather forecast for tomorrow.",
        "Calculate 15% of 85.",
        "Remind me to call my mom tomorrow.",
        "I like science fiction movies.",
        "Let's talk about something else.",
        "Be more concise in your responses.",
        "#reset_tone casual",
        "Hello, how are you today?",
        "Goodbye, talk to you later.",
        "Thank you for your help.",
        "That's not correct information."
    ]
    
    for user_input in test_inputs:
        intent_type, metadata = router.detect_intent(user_input)
        print(f"Input: \"{user_input}\"")
        print(f"Detected intent: {intent_type.name}")
        print(f"Metadata: {metadata}")
        print()
    
    # Test entity extraction
    print("\nTesting entity extraction:")
    
    entity_test_inputs = [
        ("Do you remember what I told you about my vacation?", IntentType.MEMORY_RECALL),
        ("Remember that I have a meeting at 3pm tomorrow.", IntentType.MEMORY_STORE),
        ("Look up the recipe for chocolate chip cookies.", IntentType.EXTERNAL_ACTION),
        ("Remind me to take my medication at 8pm.", IntentType.FUTURE_PLANNING),
        ("Be more formal in your responses.", IntentType.PERSONALITY_ADJUSTMENT),
        ("#reset_tone formal", IntentType.SYSTEM_COMMAND)
    ]
    
    for user_input, intent_type in entity_test_inputs:
        entities = router.extract_entities(user_input, intent_type)
        print(f"Input: \"{user_input}\"")
        print(f"Intent: {intent_type.name}")
        print(f"Extracted entities: {entities}")
        print()
    
    print("IntentRouter test completed")

def test_intent_handlers():
    """Test the IntentHandlers class."""
    print("\n" + "=" * 50)
    print("Testing IntentHandlers")
    print("=" * 50)
    
    # Initialize intent handlers
    handlers = IntentHandlers()
    
    # Enable debug mode for testing
    handlers.debug_mode = True
    
    # Test handlers for different intent types
    print("\nTesting handlers for different intent types:")
    
    test_cases = [
        (IntentType.INFORMATION_REQUEST, "What is the capital of France?", {}),
        (IntentType.MEMORY_RECALL, "Do you remember what I told you about my job?", {"recall_subject": "my job"}),
        (IntentType.MEMORY_STORE, "Remember that I prefer coffee over tea.", {"store_content": "I prefer coffee over tea"}),
        (IntentType.EXTERNAL_ACTION, "Look up the weather forecast for tomorrow.", {"lookup_query": "weather forecast for tomorrow"}),
        (IntentType.TOOL_USE, "Calculate 15% of 85.", {}),
        (IntentType.FUTURE_PLANNING, "Remind me to call my mom tomorrow.", {"reminder_content": "call my mom", "reminder_time": "tomorrow"}),
        (IntentType.USER_PREFERENCE, "I like science fiction movies.", {}),
        (IntentType.CONVERSATION_CONTROL, "Let's talk about something else.", {}),
        (IntentType.PERSONALITY_ADJUSTMENT, "Be more concise in your responses.", {"adjustment_trait": "concise", "adjustment_direction": "more"}),
        (IntentType.SYSTEM_COMMAND, "#reset_tone casual", {"command": "reset_tone", "args": ["casual"]}),
        (IntentType.GREETING, "Hello, how are you today?", {}),
        (IntentType.FAREWELL, "Goodbye, talk to you later.", {}),
        (IntentType.GRATITUDE, "Thank you for your help.", {}),
        (IntentType.FEEDBACK, "That's not correct information.", {}),
        (IntentType.UNKNOWN, "xyzzy plugh", {})
    ]
    
    for intent_type, user_input, entities in test_cases:
        # Get the appropriate handler method
        handler_methods = {
            IntentType.INFORMATION_REQUEST: handlers.handle_information_request,
            IntentType.MEMORY_RECALL: handlers.handle_memory_recall,
            IntentType.MEMORY_STORE: handlers.handle_memory_store,
            IntentType.EXTERNAL_ACTION: handlers.handle_external_action,
            IntentType.TOOL_USE: handlers.handle_tool_use,
            IntentType.FUTURE_PLANNING: handlers.handle_future_planning,
            IntentType.USER_PREFERENCE: handlers.handle_user_preference,
            IntentType.CONVERSATION_CONTROL: handlers.handle_conversation_control,
            IntentType.PERSONALITY_ADJUSTMENT: handlers.handle_personality_adjustment,
            IntentType.SYSTEM_COMMAND: handlers.handle_system_command,
            IntentType.GREETING: handlers.handle_greeting,
            IntentType.FAREWELL: handlers.handle_farewell,
            IntentType.GRATITUDE: handlers.handle_gratitude,
            IntentType.FEEDBACK: handlers.handle_feedback,
            IntentType.UNKNOWN: handlers.handle_unknown
        }
        
        handler = handler_methods[intent_type]
        
        # Call the handler
        metadata = {"raw_input": user_input}
        result = handler(user_input, entities, metadata)
        
        print(f"Intent: {intent_type.name}")
        print(f"Input: \"{user_input}\"")
        print(f"Entities: {entities}")
        print(f"Result action: {result.get('action')}")
        print(f"Result message: {result.get('message')}")
        print()
    
    print("IntentHandlers test completed")

def test_intent_manager():
    """Test the IntentManager class with integration."""
    print("\n" + "=" * 50)
    print("Testing IntentManager with Integration")
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
            "long_term_path": "data/memory/test_intent",
            "vector_db": "in_memory"
        }
    }
    
    memory_manager = EnhancedMemoryManager(memory_config)
    
    # Create a test personality manager
    personality_manager = AdvancedPersonalityManager(
        memory_manager=memory_manager,
        config=config
    )
    
    # Initialize intent manager
    intent_manager = IntentManager(
        memory_manager=memory_manager,
        tool_router=None,  # No tool router for this test
        personality_manager=personality_manager
    )
    
    # Enable debug mode for testing
    intent_manager.set_debug_mode(True)
    
    # Test processing different inputs
    print("\nTesting intent processing with integration:")
    
    test_inputs = [
        "What is the capital of France?",
        "Do you remember what I told you about my job?",
        "Remember that I prefer coffee over tea.",
        "Look up the weather forecast for tomorrow.",
        "Be more concise in your responses.",
        "#reset_tone casual",
        "#debug_off",
        "#help"
    ]
    
    for user_input in test_inputs:
        print(f"\nProcessing: \"{user_input}\"")
        result = intent_manager.process_input(user_input)
        
        print(f"Intent: {result.get('intent_type').name}")
        print(f"Action: {result.get('action')}")
        print(f"Message: {result.get('message')}")
        
        # Print additional information based on action
        if result.get('action') == 'memory_store':
            print(f"Stored content: {result.get('store_content')}")
        elif result.get('action') == 'memory_recall':
            print(f"Recall subject: {result.get('recall_subject')}")
            print(f"Found memories: {len(result.get('memories', []))}")
        elif result.get('action') == 'personality_adjustment':
            print(f"Adjusted parameter: {result.get('parameter')}")
            print(f"New value: {result.get('new_value')}")
        elif result.get('action') == 'system_command':
            print(f"Command: {result.get('command')}")
            print(f"Args: {result.get('args')}")
            
            if result.get('command') == 'help':
                print(f"Available commands: {result.get('commands')}")
    
    # Test getting intent history
    print("\nIntent history:")
    history = intent_manager.get_intent_history()
    for i, item in enumerate(history):
        print(f"{i+1}. {item.get('intent_type').name}: \"{item.get('user_input')}\"")
    
    # Test getting intent distribution
    print("\nIntent distribution:")
    distribution = intent_manager.get_intent_distribution()
    for intent_type, count in distribution.items():
        print(f"{intent_type.name}: {count}")
    
    # Clear history
    intent_manager.clear_history()
    print("\nCleared intent history")
    
    print("IntentManager test completed")

def main():
    """Run all tests."""
    try:
        test_intent_router()
        test_intent_handlers()
        test_intent_manager()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
