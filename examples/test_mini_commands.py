#!/usr/bin/env python3
"""
Test script for the mini-command language.
"""

import os
import sys
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
logger = logging.getLogger("test.mini_commands")

# Import the intent modules
from intent import IntentRouter, IntentType, IntentHandlers
from feedback import FeedbackManager, FeedbackType
from memory import EnhancedMemoryManager
from personality import AdvancedPersonalityManager

def load_config():
    """Load configuration from file."""
    import yaml
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_command_detection():
    """Test the detection of mini-commands."""
    print("\n" + "=" * 50)
    print("Testing Mini-Command Detection")
    print("=" * 50)
    
    # Initialize intent router
    router = IntentRouter()
    
    # Test command detection
    print("\nTesting command detection:")
    
    test_commands = [
        "#reset_tone casual",
        "#mood_reset",
        "#personality_insight",
        "#show_memory",
        "#summarize_session",
        "#summarize_day",
        "#view_feedback",
        "#view_feedback tone",
        "#feedback",
        "#feedback tone",
        "#debug_on",
        "#debug_off",
        "#help",
        "This is not a command",
        "#unknown_command"
    ]
    
    for command in test_commands:
        intent_type, metadata = router.detect_intent(command)
        print(f"Command: \"{command}\"")
        print(f"Detected intent: {intent_type.name}")
        print(f"Metadata: {metadata}")
        print()
    
    print("Command detection test completed")

def test_command_handling():
    """Test the handling of mini-commands."""
    print("\n" + "=" * 50)
    print("Testing Mini-Command Handling")
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
            "long_term_path": "data/memory/test_commands",
            "vector_db": "in_memory"
        }
    }
    
    memory_manager = EnhancedMemoryManager(memory_config)
    
    # Create a test personality manager
    personality_manager = AdvancedPersonalityManager(
        memory_manager=memory_manager,
        config=config
    )
    
    # Create a test feedback manager
    feedback_manager = FeedbackManager(
        memory_manager=memory_manager,
        personality_manager=personality_manager,
        config=config
    )
    
    # Connect feedback manager to personality manager
    personality_manager.feedback_manager = feedback_manager
    
    # Initialize intent handlers
    handlers = IntentHandlers(
        memory_manager=memory_manager,
        personality_manager=personality_manager
    )
    
    # Enable debug mode for testing
    handlers.debug_mode = True
    
    # Test command handling
    print("\nTesting command handling:")
    
    test_commands = [
        ("#reset_tone casual", "Reset personality tone to casual"),
        ("#mood_reset", "Reset personality to default state"),
        ("#personality_insight", "Show current personality settings"),
        ("#show_memory", "Show memory statistics"),
        ("#summarize_session", "Generate a summary of the current session"),
        ("#summarize_day", "Generate a summary of today's interactions"),
        ("#view_feedback", "View feedback statistics"),
        ("#feedback tone", "Request tone feedback"),
        ("#help", "Show available commands")
    ]
    
    for command, description in test_commands:
        print(f"\nCommand: \"{command}\" - {description}")
        
        # Detect intent
        intent_type, metadata = IntentRouter().detect_intent(command)
        print(f"Detected intent: {intent_type.name}")
        
        # Extract entities
        entities = IntentRouter().extract_entities(command, intent_type)
        print(f"Extracted entities: {entities}")
        
        # Handle command
        if intent_type == IntentType.SYSTEM_COMMAND:
            result = handlers.handle_system_command(command, entities, metadata)
            print(f"Action: {result.get('action')}")
            print(f"Message: {result.get('message')}")
            
            # Print additional information based on command
            if command == "#personality_insight":
                if "parameters" in result:
                    print(f"Parameters: {result.get('parameters')}")
            elif command == "#show_memory":
                if "stats" in result:
                    print(f"Memory stats: {result.get('stats')}")
            elif command == "#view_feedback":
                if "stats" in result:
                    print(f"Feedback stats: {result.get('stats')}")
            elif command == "#help":
                if "commands" in result:
                    print(f"Available commands: {len(result.get('commands'))} commands")
        else:
            print(f"Not a system command")
    
    print("\nCommand handling test completed")

def main():
    """Run all tests."""
    try:
        test_command_detection()
        test_command_handling()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
