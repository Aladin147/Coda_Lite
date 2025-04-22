#!/usr/bin/env python3
"""
Test script for the feedback system.
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
logger = logging.getLogger("test.feedback")

# Import the feedback modules
from feedback import FeedbackManager, FeedbackType, FeedbackPrompt
from memory import EnhancedMemoryManager
from personality import AdvancedPersonalityManager
from intent import IntentType

def load_config():
    """Load configuration from file."""
    import yaml
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_feedback_manager():
    """Test the FeedbackManager class."""
    print("\n" + "=" * 50)
    print("Testing FeedbackManager")
    print("=" * 50)
    
    # Initialize feedback manager
    feedback_manager = FeedbackManager()
    
    # Test feedback types and prompts
    print("\nTesting feedback types and prompts:")
    
    for feedback_type in FeedbackType:
        print(f"Feedback type: {feedback_type.name}")
        
        # Get prompt options for this type
        prompt_options = getattr(FeedbackPrompt, feedback_type.name).value
        print(f"Prompt options:")
        for i, prompt in enumerate(prompt_options):
            print(f"  {i+1}. {prompt}")
        print()
    
    # Test sentiment analysis
    print("\nTesting sentiment analysis:")
    
    test_responses = [
        "Yes, that was helpful.",
        "No, that wasn't what I was looking for.",
        "That's correct, thanks!",
        "That's wrong, please try again.",
        "Maybe, I'm not sure.",
        "I like how you explained that.",
        "I don't like your tone.",
        "Perfect!",
        "Terrible response.",
        "OK"
    ]
    
    for response in test_responses:
        sentiment = feedback_manager._analyze_sentiment(response)
        print(f"Response: \"{response}\"")
        print(f"Sentiment: {sentiment}")
        print()
    
    print("FeedbackManager test completed")

def test_feedback_integration():
    """Test the FeedbackManager with integration."""
    print("\n" + "=" * 50)
    print("Testing FeedbackManager with Integration")
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
            "long_term_path": "data/memory/test_feedback",
            "vector_db": "in_memory"
        }
    }
    
    memory_manager = EnhancedMemoryManager(memory_config)
    
    # Create a test personality manager
    personality_manager = AdvancedPersonalityManager(
        memory_manager=memory_manager,
        config=config
    )
    
    # Initialize feedback manager
    feedback_manager = FeedbackManager(
        memory_manager=memory_manager,
        personality_manager=personality_manager,
        config=config
    )
    
    # Test the feedback request generation
    print("\nTesting feedback request generation:")
    
    # Create a mock intent result
    intent_results = [
        {
            "intent_type": IntentType.INFORMATION_REQUEST,
            "action": "llm_response",
            "message": "Paris is the capital of France."
        },
        {
            "intent_type": IntentType.MEMORY_RECALL,
            "action": "memory_recall",
            "message": "I found 2 memories about your job.",
            "memories": [
                {"content": "You work as a software developer."},
                {"content": "You enjoy coding in Python."}
            ]
        },
        {
            "intent_type": IntentType.MEMORY_STORE,
            "action": "memory_store",
            "message": "I'll remember that you prefer coffee over tea.",
            "store_content": "I prefer coffee over tea."
        },
        {
            "intent_type": IntentType.PERSONALITY_ADJUSTMENT,
            "action": "personality_adjustment",
            "message": "I'll try to be more concise.",
            "parameter": "verbosity",
            "adjustment": -0.2,
            "new_value": 0.3
        }
    ]
    
    for intent_result in intent_results:
        # Force feedback request
        feedback_manager.feedback_frequency = 1.0  # 100% chance
        feedback_manager.current_turn = 10  # Ensure we're past the cooldown
        
        print(f"\nIntent type: {intent_result['intent_type'].name if hasattr(intent_result['intent_type'], 'name') else intent_result['intent_type']}")
        print(f"Action: {intent_result['action']}")
        print(f"Message: {intent_result['message']}")
        
        should_request = feedback_manager.should_request_feedback(intent_result)
        print(f"Should request feedback: {should_request}")
        
        if should_request:
            feedback_request = feedback_manager.generate_feedback_prompt(intent_result)
            print(f"Feedback prompt: {feedback_request['prompt']}")
            print(f"Feedback type: {feedback_request['type'].name}")
            
            # Test processing a response
            response = "Yes, that was helpful."
            print(f"User response: {response}")
            
            is_feedback = feedback_manager.is_feedback_response(response)
            print(f"Is feedback response: {is_feedback}")
            
            if is_feedback:
                result = feedback_manager.process_feedback_response(response)
                print(f"Processed: {result['processed']}")
                print(f"Sentiment: {result['feedback']['sentiment']}")
    
    # Test getting feedback history and stats
    print("\nFeedback history:")
    history = feedback_manager.get_feedback_history()
    for i, item in enumerate(history):
        print(f"{i+1}. Type: {item['type'].name}, Sentiment: {item['sentiment']}, Response: \"{item['response']}\"")
    
    print("\nFeedback stats:")
    stats = feedback_manager.get_feedback_stats()
    print(f"Total: {stats['total']}")
    print(f"Positive: {stats['positive']}")
    print(f"Negative: {stats['negative']}")
    print(f"Neutral: {stats['neutral']}")
    
    # Test memory integration
    print("\nTesting memory integration:")
    
    # Get user summary
    feedback_stats = memory_manager.get_user_summary("feedback_stats")
    print(f"Feedback stats in memory: {feedback_stats}")
    
    # Clear history
    feedback_manager.clear_history()
    print("\nCleared feedback history")
    
    print("FeedbackManager integration test completed")

def main():
    """Run all tests."""
    try:
        test_feedback_manager()
        test_feedback_integration()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
