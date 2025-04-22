#!/usr/bin/env python3
"""
Test script for the advanced personality features.
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
logger = logging.getLogger("test.advanced_personality")

# Import the personality modules
from personality import (
    PersonalityParameters,
    BehavioralConditioner,
    TopicAwareness,
    SessionManager,
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

def test_personality_parameters():
    """Test the PersonalityParameters class."""
    print("\n" + "=" * 50)
    print("Testing PersonalityParameters")
    print("=" * 50)
    
    # Initialize personality parameters
    params = PersonalityParameters()
    
    # Get all parameters
    all_params = params.get_all_parameters()
    print(f"Loaded {len(all_params)} personality parameters:")
    for name, param in all_params.items():
        print(f"- {name}: {param.get('value')} (range: {param.get('range')})")
        print(f"  Description: {param.get('description')}")
        print(f"  Context adjustments: {param.get('context_adjustments')}")
    
    # Test parameter adjustment
    print("\nTesting parameter adjustment:")
    params.set_parameter_value("verbosity", 0.8, reason="test")
    params.set_parameter_value("humor", 0.2, reason="test")
    
    # Test context adjustment
    print("\nTesting context adjustment:")
    adjustments = params.adjust_for_context("technical_topic")
    print(f"Applied adjustments for 'technical_topic': {adjustments}")
    
    # Get adjustment history
    history = params.get_adjustment_history()
    print("\nAdjustment history:")
    for entry in history:
        print(f"- {entry.get('parameter')}: {entry.get('old_value')} -> {entry.get('new_value')} ({entry.get('reason')})")
    
    # Test parameter explanation
    explanation = params.explain_parameter("verbosity")
    print("\nParameter explanation:")
    print(json.dumps(explanation, indent=2))
    
    # Reset parameters
    params.reset_to_defaults()
    print("\nReset parameters to defaults")
    
    print("\nPersonalityParameters test completed")

def test_behavioral_conditioner():
    """Test the BehavioralConditioner class."""
    print("\n" + "=" * 50)
    print("Testing BehavioralConditioner")
    print("=" * 50)
    
    # Initialize personality parameters
    params = PersonalityParameters()
    
    # Initialize behavioral conditioner
    conditioner = BehavioralConditioner(personality_parameters=params)
    
    # Test processing user input
    print("\nTesting user input processing:")
    
    inputs = [
        "I prefer shorter, more concise responses.",
        "Can you be more direct and assertive in your answers?",
        "I'd like more detailed explanations with examples.",
        "Your responses are too formal, can you be more casual?",
        "I enjoy when you add a bit of humor to your responses."
    ]
    
    for user_input in inputs:
        print(f"\nUser input: \"{user_input}\"")
        preferences = conditioner.process_user_input(user_input)
        print(f"Detected preferences: {preferences}")
    
    # Get behavior profile
    profile = conditioner.get_behavior_profile()
    print("\nBehavior profile:")
    print(json.dumps(profile, indent=2))
    
    # Test pattern analysis
    print("\nTesting interaction pattern analysis:")
    patterns = conditioner.analyze_interaction_patterns()
    print(f"Detected patterns: {patterns}")
    
    # Get parameter recommendations
    recommendations = conditioner.get_parameter_recommendations()
    print("\nParameter recommendations:")
    print(json.dumps(recommendations, indent=2))
    
    print("\nBehavioralConditioner test completed")

def test_topic_awareness():
    """Test the TopicAwareness class."""
    print("\n" + "=" * 50)
    print("Testing TopicAwareness")
    print("=" * 50)
    
    # Initialize personality parameters
    params = PersonalityParameters()
    
    # Initialize topic awareness
    topic_awareness = TopicAwareness(personality_parameters=params)
    
    # Test topic detection
    print("\nTesting topic detection:")
    
    topics = [
        "Can you help me debug this Python code? I'm getting a syntax error.",
        "I'm working on a new design for my website and need some creative ideas.",
        "What's the best way to prepare for my business presentation tomorrow?",
        "I've been feeling stressed lately and need some advice on work-life balance.",
        "Have you seen the new sci-fi movie that just came out? It's amazing!"
    ]
    
    for text in topics:
        print(f"\nText: \"{text}\"")
        topic_info = topic_awareness.detect_topic(text)
        print(f"Detected topic: {topic_info.get('topic')}")
        print(f"Category: {topic_info.get('category')}")
        print(f"Confidence: {topic_info.get('confidence')}")
        print(f"Keywords: {topic_info.get('keywords')}")
    
    # Test processing user input
    print("\nTesting user input processing:")
    for text in topics:
        print(f"\nProcessing: \"{text}\"")
        topic_awareness.process_user_input(text)
    
    # Get current topic
    current_topic = topic_awareness.get_current_topic()
    print("\nCurrent topic:")
    print(json.dumps(current_topic, indent=2))
    
    # Get topic history
    history = topic_awareness.get_topic_history()
    print("\nTopic history:")
    for entry in history:
        print(f"- {entry.get('topic')} ({entry.get('category')}, confidence: {entry.get('confidence'):.2f})")
    
    print("\nTopicAwareness test completed")

def test_session_manager():
    """Test the SessionManager class."""
    print("\n" + "=" * 50)
    print("Testing SessionManager")
    print("=" * 50)
    
    # Initialize personality parameters
    params = PersonalityParameters()
    
    # Initialize session manager
    session_manager = SessionManager(personality_parameters=params)
    
    # Test initial state
    print("\nInitial session state:")
    state = session_manager.get_session_state()
    print(json.dumps(state, indent=2))
    
    # Simulate some interactions
    print("\nSimulating interactions:")
    for i in range(5):
        print(f"\nInteraction {i+1}")
        session_manager.process_interaction("user", f"User message {i+1}")
        session_manager.process_interaction("assistant", f"Assistant response {i+1}")
        state = session_manager.update()
        print(f"Session duration: {state.get('session_duration'):.1f}s")
        print(f"Turn count: {state.get('turn_count')}")
    
    # Generate session summary
    print("\nGenerating session summary:")
    summary = session_manager.generate_session_summary()
    print(json.dumps(summary, indent=2))
    
    # Test closure mode
    print("\nTesting closure mode:")
    # Hack the session duration to force closure mode
    session_manager.session_duration = 1801  # Just over 30 minutes
    session_manager.update()
    
    if session_manager.in_closure_mode:
        print("Entered closure mode")
        closure_message = session_manager.get_closure_message()
        print(f"Closure message: \"{closure_message}\"")
    
    # Reset session
    session_manager.reset()
    print("\nReset session manager")
    
    print("\nSessionManager test completed")

def test_advanced_personality_manager():
    """Test the AdvancedPersonalityManager class."""
    print("\n" + "=" * 50)
    print("Testing AdvancedPersonalityManager")
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
            "long_term_path": "data/memory/test_advanced",
            "vector_db": "in_memory"
        }
    }
    
    memory_manager = EnhancedMemoryManager(memory_config)
    
    # Initialize advanced personality manager
    personality_manager = AdvancedPersonalityManager(
        memory_manager=memory_manager,
        config=config
    )
    
    # Test processing user input
    print("\nTesting user input processing:")
    
    inputs = [
        "Can you help me debug this Python code? I'm getting a syntax error.",
        "I prefer shorter, more concise responses.",
        "What's the best way to prepare for my business presentation tomorrow?",
        "I'd like more detailed explanations with examples.",
        "Have you seen the new sci-fi movie that just came out? It's amazing!"
    ]
    
    for user_input in inputs:
        print(f"\nUser input: \"{user_input}\"")
        memory_manager.add_turn("user", user_input)
        results = personality_manager.process_user_input(user_input)
        
        # Process a simulated response
        response = f"Here's my response to: {user_input}"
        memory_manager.add_turn("assistant", response)
        personality_manager.process_assistant_response(response)
    
    # Get current context
    context = personality_manager.get_current_context()
    print("\nCurrent context:")
    print(json.dumps(context, indent=2))
    
    # Generate system prompt
    print("\nGenerating system prompt:")
    prompt = personality_manager.generate_system_prompt()
    print(prompt)
    
    # Test response formatting
    print("\nTesting response formatting:")
    original_response = "This is a test response that should be formatted according to the current personality parameters. It might be adjusted for verbosity, formality, and other factors based on the user's preferences and the current conversation context."
    formatted = personality_manager.format_response(original_response)
    print(f"Original: \"{original_response}\"")
    print(f"Formatted: \"{formatted}\"")
    
    # Get behavior profile
    profile = personality_manager.get_behavior_profile()
    print("\nBehavior profile:")
    print(json.dumps(profile, indent=2))
    
    # Get current topic
    topic = personality_manager.get_current_topic()
    print("\nCurrent topic:")
    print(json.dumps(topic, indent=2))
    
    # Get session state
    session = personality_manager.get_session_state()
    print("\nSession state:")
    print(json.dumps(session, indent=2))
    
    # Get personality parameters
    parameters = personality_manager.get_personality_parameters()
    print("\nPersonality parameters:")
    for name, param in parameters.items():
        print(f"- {name}: {param.get('value')}")
    
    # Reset personality manager
    personality_manager.reset()
    print("\nReset personality manager")
    
    print("\nAdvancedPersonalityManager test completed")

def main():
    """Run all tests."""
    try:
        test_personality_parameters()
        test_behavioral_conditioner()
        test_topic_awareness()
        test_session_manager()
        test_advanced_personality_manager()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
