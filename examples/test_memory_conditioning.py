#!/usr/bin/env python3
"""
Test script for memory-based personality conditioning.
"""

import os
import sys
import logging
from datetime import datetime, timedelta
import random

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
logger = logging.getLogger("test.memory_conditioning")

# Import the necessary modules
from memory import EnhancedMemoryManager
from personality import AdvancedPersonalityManager
from feedback import FeedbackManager, FeedbackType
from personality.memory_conditioning import MemoryConditioner, FeedbackPattern

def load_config():
    """Load configuration from file."""
    import yaml
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def create_test_feedback(feedback_type, sentiment, response_text):
    """Create a test feedback item."""
    feedback_id = f"feedback_{datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    return {
        "id": feedback_id,
        "type": feedback_type,
        "prompt": f"Test prompt for {feedback_type.name}",
        "response": response_text,
        "sentiment": sentiment,
        "intent_type": "TEST_INTENT",
        "intent_result": {"intent_type": "TEST_INTENT", "action": "test"},
        "timestamp": datetime.now().isoformat(),
        "turn": random.randint(1, 100)
    }

def test_memory_conditioner_initialization():
    """Test the initialization of the memory conditioner."""
    print("\n" + "=" * 50)
    print("Testing Memory Conditioner Initialization")
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
            "long_term_path": "data/memory/test_conditioning",
            "vector_db": "in_memory"
        }
    }
    
    memory_manager = EnhancedMemoryManager(memory_config)
    
    # Create a test personality manager
    personality_manager = AdvancedPersonalityManager(
        memory_manager=memory_manager,
        config=config
    )
    
    # Create a test memory conditioner
    memory_conditioner = MemoryConditioner(
        memory_manager=memory_manager,
        personality_manager=personality_manager,
        behavioral_conditioner=personality_manager.behavioral_conditioner,
        config=config
    )
    
    print(f"Memory conditioner initialized: {memory_conditioner is not None}")
    print(f"Memory manager connected: {memory_conditioner.memory_manager is not None}")
    print(f"Personality manager connected: {memory_conditioner.personality_manager is not None}")
    print(f"Behavioral conditioner connected: {memory_conditioner.behavioral_conditioner is not None}")
    
    print("Memory conditioner initialization test completed")
    
    return memory_manager, personality_manager, memory_conditioner

def test_feedback_storage():
    """Test the storage of feedback in memory."""
    print("\n" + "=" * 50)
    print("Testing Feedback Storage")
    print("=" * 50)
    
    # Create test components
    memory_manager, personality_manager, memory_conditioner = test_memory_conditioner_initialization()
    
    # Create test feedback items
    feedback_items = [
        create_test_feedback(FeedbackType.TONE, "positive", "I like your formal tone"),
        create_test_feedback(FeedbackType.VERBOSITY, "negative", "Too verbose, please be more concise"),
        create_test_feedback(FeedbackType.HELPFULNESS, "positive", "That was very helpful, thanks"),
        create_test_feedback(FeedbackType.ACCURACY, "neutral", "Seems mostly correct"),
        create_test_feedback(FeedbackType.MEMORY, "positive", "Yes, please remember that"),
        create_test_feedback(FeedbackType.TONE, "negative", "Too formal, please be more casual")
    ]
    
    # Store feedback items
    print("\nStoring feedback items:")
    for i, feedback in enumerate(feedback_items):
        success = memory_manager.add_feedback(feedback)
        print(f"Feedback {i+1} ({feedback['type'].name}, {feedback['sentiment']}): {'Stored' if success else 'Failed'}")
    
    # Retrieve feedback memories
    print("\nRetrieving feedback memories:")
    memories = memory_manager.get_feedback_memories(limit=10)
    print(f"Retrieved {len(memories)} feedback memories")
    
    for i, memory in enumerate(memories):
        print(f"Memory {i+1}: {memory.get('content', '')} (Type: {memory.get('type', 'unknown')}, Sentiment: {memory.get('sentiment', 'unknown')})")
    
    # Retrieve feedback by type
    print("\nRetrieving feedback by type:")
    for feedback_type in [ft.name for ft in FeedbackType]:
        type_memories = memory_manager.get_feedback_memories(feedback_type=feedback_type, limit=5)
        print(f"Type {feedback_type}: {len(type_memories)} memories")
    
    print("Feedback storage test completed")
    
    return memory_manager, personality_manager, memory_conditioner

def test_feedback_pattern_analysis():
    """Test the analysis of feedback patterns."""
    print("\n" + "=" * 50)
    print("Testing Feedback Pattern Analysis")
    print("=" * 50)
    
    # Create test components with feedback
    memory_manager, personality_manager, memory_conditioner = test_feedback_storage()
    
    # Analyze feedback patterns
    print("\nAnalyzing feedback patterns:")
    analysis = memory_conditioner.analyze_feedback_patterns(force_refresh=True)
    
    print(f"Overall pattern: {analysis.get('pattern', 'unknown')}")
    print(f"Feedback count: {analysis.get('feedback_count', 0)}")
    
    print("\nType patterns:")
    for type_name, pattern in analysis.get('type_patterns', {}).items():
        print(f"- {type_name}: {pattern}")
    
    print("\nInsights:")
    for type_name, insights in analysis.get('insights', {}).items():
        print(f"- {type_name}:")
        print(f"  Pattern: {insights.get('pattern', 'unknown')}")
        print(f"  Count: {insights.get('count', 0)}")
        print(f"  Sentiment distribution: {insights.get('sentiment_distribution', {})}")
        
        if insights.get('recommendations'):
            print(f"  Recommendations:")
            for rec in insights.get('recommendations', []):
                print(f"    - {rec.get('action', 'unknown')} (confidence: {rec.get('confidence', 0)})")
    
    print("Feedback pattern analysis test completed")
    
    return memory_manager, personality_manager, memory_conditioner

def test_feedback_pattern_application():
    """Test the application of feedback patterns."""
    print("\n" + "=" * 50)
    print("Testing Feedback Pattern Application")
    print("=" * 50)
    
    # Create test components with feedback and analysis
    memory_manager, personality_manager, memory_conditioner = test_feedback_pattern_analysis()
    
    # Get current behavior profile
    print("\nCurrent behavior profile:")
    behavior_profile = personality_manager.behavioral_conditioner.get_behavior_profile()
    for param, value in behavior_profile.items():
        if param not in ["last_updated", "observation_count"]:
            print(f"- {param}: {value}")
    
    # Apply feedback patterns
    print("\nApplying feedback patterns:")
    result = memory_conditioner.apply_feedback_patterns()
    
    if result.get("applied", False):
        print("Changes applied:")
        for change in result.get("changes", []):
            param = change.get("parameter", "unknown")
            old_val = change.get("old_value", 0)
            new_val = change.get("new_value", 0)
            reason = change.get("reason", "unknown")
            print(f"- {param}: {old_val:.2f} → {new_val:.2f} ({reason})")
    else:
        print(f"No changes applied: {result.get('reason', 'unknown')}")
    
    # Get updated behavior profile
    print("\nUpdated behavior profile:")
    behavior_profile = personality_manager.behavioral_conditioner.get_behavior_profile()
    for param, value in behavior_profile.items():
        if param not in ["last_updated", "observation_count"]:
            print(f"- {param}: {value}")
    
    print("Feedback pattern application test completed")
    
    return memory_manager, personality_manager, memory_conditioner

def test_user_preference_insights():
    """Test the generation of user preference insights."""
    print("\n" + "=" * 50)
    print("Testing User Preference Insights")
    print("=" * 50)
    
    # Create test components with feedback and applied patterns
    memory_manager, personality_manager, memory_conditioner = test_feedback_pattern_application()
    
    # Get user preference insights
    print("\nGetting user preference insights:")
    insights = memory_conditioner.get_user_preference_insights()
    
    if insights.get("available", False):
        print(f"Overall pattern: {insights.get('overall_pattern', 'unknown')}")
        print(f"Feedback count: {insights.get('feedback_count', 0)}")
        
        print("\nPreferences:")
        for param, prefs in insights.get("preferences", {}).items():
            print(f"- {param}:")
            for pref in prefs:
                preference = pref.get("preference", "unknown")
                confidence = pref.get("confidence", 0)
                source = pref.get("source", "unknown")
                print(f"  - {preference} (confidence: {confidence:.2f}, source: {source})")
        
        print("\nRecommendations:")
        for rec in insights.get("recommendations", []):
            print(f"- {rec.get('action', 'unknown')} (confidence: {rec.get('confidence', 0)})")
    else:
        print(f"No insights available: {insights.get('reason', 'unknown')}")
    
    print("User preference insights test completed")

def main():
    """Run all tests."""
    try:
        test_memory_conditioner_initialization()
        test_feedback_storage()
        test_feedback_pattern_analysis()
        test_feedback_pattern_application()
        test_user_preference_insights()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
