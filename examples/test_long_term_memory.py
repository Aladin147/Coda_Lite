#!/usr/bin/env python3
"""
Test script for the long-term memory system.
"""

import os
import sys
import json
import logging
import yaml
from datetime import datetime, timedelta

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
logger = logging.getLogger("test.long_term_memory")

# Import the memory modules
from memory import LongTermMemory, MemoryEncoder, EnhancedMemoryManager, MemoryManager

def load_config():
    """Load configuration from file."""
    config_path = "config/config.yaml"
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    return config

def test_long_term_memory():
    """Test the LongTermMemory class."""
    print("\n" + "=" * 50)
    print("Testing LongTermMemory")
    print("=" * 50)
    
    # Create a test directory
    test_dir = "data/memory/test_long_term"
    os.makedirs(test_dir, exist_ok=True)
    
    # Initialize long-term memory
    memory = LongTermMemory(
        storage_path=test_dir,
        embedding_model="all-MiniLM-L6-v2",
        vector_db_type="in_memory",  # Use in-memory for testing
        max_memories=100,
        device="cpu"
    )
    
    # Add some test memories
    print("\nAdding test memories...")
    
    memory_ids = []
    
    # Add a conversation memory
    memory_id = memory.add_memory(
        content="I prefer to use Python for data science projects because it has great libraries like pandas and scikit-learn.",
        source_type="conversation",
        importance=0.8,
        metadata={
            "source_type": "conversation",
            "speakers": ["user"],
            "timestamp": datetime.now().isoformat(),
            "topics": ["python", "data science", "programming"]
        }
    )
    memory_ids.append(memory_id)
    
    # Add a fact memory
    memory_id = memory.add_memory(
        content="The user's favorite color is blue.",
        source_type="fact",
        importance=0.7,
        metadata={
            "source_type": "fact",
            "timestamp": datetime.now().isoformat(),
            "topics": ["preferences", "colors"]
        }
    )
    memory_ids.append(memory_id)
    
    # Add a preference memory
    memory_id = memory.add_memory(
        content="The user prefers concise responses without too much detail.",
        source_type="preference",
        importance=0.9,
        metadata={
            "source_type": "preference",
            "timestamp": datetime.now().isoformat(),
            "topics": ["communication", "preferences"]
        }
    )
    memory_ids.append(memory_id)
    
    # Add an older memory (30 days ago)
    old_timestamp = (datetime.now() - timedelta(days=30)).isoformat()
    memory_id = memory.add_memory(
        content="The user mentioned they were planning a trip to Japan next year.",
        source_type="conversation",
        importance=0.6,
        metadata={
            "source_type": "conversation",
            "speakers": ["user"],
            "timestamp": old_timestamp,
            "topics": ["travel", "japan", "plans"]
        }
    )
    memory_ids.append(memory_id)
    
    print(f"Added {len(memory_ids)} memories")
    
    # Test retrieving memories
    print("\nRetrieving memories...")
    
    # Test query about Python
    query = "What programming languages does the user like?"
    print(f"\nQuery: {query}")
    
    results = memory.retrieve_memories(query, limit=2)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. [Similarity: {result['similarity']:.2f}] {result['content']}")
        if 'adjusted_score' in result:
            print(f"   Adjusted score: {result['adjusted_score']:.2f}, Decay factor: {result['decay_factor']:.2f}")
    
    # Test query about preferences
    query = "How does the user prefer to communicate?"
    print(f"\nQuery: {query}")
    
    results = memory.retrieve_memories(query, limit=2)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. [Similarity: {result['similarity']:.2f}] {result['content']}")
        if 'adjusted_score' in result:
            print(f"   Adjusted score: {result['adjusted_score']:.2f}, Decay factor: {result['decay_factor']:.2f}")
    
    # Test query about travel
    query = "Has the user mentioned any travel plans?"
    print(f"\nQuery: {query}")
    
    results = memory.retrieve_memories(query, limit=2)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. [Similarity: {result['similarity']:.2f}] {result['content']}")
        if 'adjusted_score' in result:
            print(f"   Adjusted score: {result['adjusted_score']:.2f}, Decay factor: {result['decay_factor']:.2f}")
    
    # Test user summary
    print("\nTesting user summary...")
    
    memory.update_user_summary("preferred_topics", ["programming", "data science", "travel"])
    memory.update_user_summary("communication_style", "concise")
    memory.update_user_summary("favorite_color", "blue")
    
    summary = memory.get_user_summary()
    print(f"User summary: {json.dumps(summary, indent=2)}")
    
    # Test memory stats
    print("\nTesting memory stats...")
    
    stats = memory.get_memory_stats()
    print(f"Memory stats: {json.dumps(stats, indent=2)}")
    
    # Close memory
    memory.close()
    
    print("\nLongTermMemory test completed")

def test_memory_encoder():
    """Test the MemoryEncoder class."""
    print("\n" + "=" * 50)
    print("Testing MemoryEncoder")
    print("=" * 50)
    
    # Initialize memory encoder
    encoder = MemoryEncoder(
        chunk_size=200,
        overlap=50,
        min_chunk_length=50
    )
    
    # Create some test conversation turns
    turns = [
        {
            "role": "user",
            "content": "I've been learning Python for data science. What libraries would you recommend for machine learning?",
            "turn_id": 0,
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": "For machine learning in Python, I'd recommend scikit-learn for general ML algorithms, TensorFlow or PyTorch for deep learning, and pandas for data manipulation. What kind of projects are you working on?",
            "turn_id": 1,
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "user",
            "content": "I'm working on a project to analyze customer data and predict which customers are likely to churn. I'm not sure if I should use classification or regression for this.",
            "turn_id": 2,
            "timestamp": datetime.now().isoformat()
        },
        {
            "role": "assistant",
            "content": "For customer churn prediction, you'd want to use classification since you're predicting a binary outcome (churn or not churn). Random Forest or Gradient Boosting classifiers from scikit-learn would be good choices to start with.",
            "turn_id": 3,
            "timestamp": datetime.now().isoformat()
        }
    ]
    
    # Test encoding conversation
    print("\nEncoding conversation...")
    
    memories = encoder.encode_conversation(turns)
    
    print(f"Created {len(memories)} memory chunks:")
    for i, memory in enumerate(memories):
        print(f"{i+1}. [Importance: {memory['importance']:.2f}] {memory['content'][:100]}...")
        print(f"   Topics: {memory['metadata']['topics']}")
    
    # Test encoding a fact
    print("\nEncoding a fact...")
    
    fact = "The user is working on a customer churn prediction project using Python."
    fact_memory = encoder.encode_fact(fact)
    
    print(f"Fact: {fact}")
    print(f"Importance: {fact_memory['importance']:.2f}")
    print(f"Topics: {fact_memory['metadata']['topics']}")
    
    # Test encoding a preference
    print("\nEncoding a preference...")
    
    preference = "The user prefers detailed technical explanations with code examples."
    pref_memory = encoder.encode_preference(preference)
    
    print(f"Preference: {preference}")
    print(f"Importance: {pref_memory['importance']:.2f}")
    print(f"Topics: {pref_memory['metadata']['topics']}")
    
    print("\nMemoryEncoder test completed")

def test_enhanced_memory_manager():
    """Test the EnhancedMemoryManager class."""
    print("\n" + "=" * 50)
    print("Testing EnhancedMemoryManager")
    print("=" * 50)
    
    # Load config
    config = load_config()
    
    # Override some settings for testing
    config["memory"]["long_term_path"] = "data/memory/test_enhanced"
    config["memory"]["vector_db"] = "in_memory"
    
    # Initialize enhanced memory manager
    memory = EnhancedMemoryManager(config)
    
    # Add some conversation turns
    print("\nAdding conversation turns...")
    
    memory.add_turn("system", "You are Coda, a helpful assistant with a direct and efficient personality.")
    memory.add_turn("user", "I'm planning a trip to Japan next month. What are some must-visit places in Tokyo?")
    memory.add_turn("assistant", "Tokyo has many great attractions. Some must-visit places include the Tokyo Skytree, Senso-ji Temple in Asakusa, the Meiji Shrine, and the Shibuya Crossing. When are you planning to visit and how long will you stay?")
    memory.add_turn("user", "I'll be there for a week in cherry blossom season. I'm particularly interested in technology and food.")
    memory.add_turn("assistant", "Visiting during cherry blossom season is perfect! For technology, check out Akihabara Electric Town and the teamLab Borderless digital art museum. For food, visit Tsukiji Outer Market for fresh sushi, try ramen in Shinjuku, and don't miss the department store food halls called 'depachika'. The cherry blossoms in Ueno Park and along the Meguro River are spectacular.")
    
    # Test persisting to long-term memory
    print("\nPersisting to long-term memory...")
    
    count = memory.persist_short_term_memory()
    print(f"Persisted {count} memories")
    
    # Add a fact
    print("\nAdding a fact...")
    
    fact = "The user is planning a trip to Japan during cherry blossom season and is interested in technology and food."
    fact_id = memory.add_fact(fact)
    print(f"Added fact with ID: {fact_id}")
    
    # Add a preference
    print("\nAdding a preference...")
    
    preference = "The user enjoys traveling and experiencing different cultures, especially food and technology."
    pref_id = memory.add_preference(preference)
    print(f"Added preference with ID: {pref_id}")
    
    # Update user summary
    print("\nUpdating user summary...")
    
    memory.update_user_summary("interests", ["travel", "technology", "food"])
    memory.update_user_summary("upcoming_trips", ["Japan"])
    
    # Test retrieving memories
    print("\nRetrieving memories...")
    
    query = "What is the user interested in regarding Japan?"
    print(f"\nQuery: {query}")
    
    results = memory.retrieve_relevant_memories(query, limit=2)
    
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results):
        print(f"{i+1}. [Similarity: {result['similarity']:.2f}] {result['content']}")
    
    # Test getting enhanced context
    print("\nGetting enhanced context...")
    
    user_input = "Can you recommend some good Japanese restaurants in Tokyo?"
    context = memory.get_enhanced_context(user_input)
    
    print(f"Enhanced context has {len(context)} messages:")
    for i, msg in enumerate(context):
        print(f"{i+1}. [{msg['role']}]: {msg['content'][:100]}...")
    
    # Test getting user preferences
    print("\nGetting user preferences...")
    
    preferences = memory.get_user_preferences()
    print(f"User preferences: {json.dumps(preferences, indent=2)}")
    
    # Test getting memory stats
    print("\nGetting memory stats...")
    
    stats = memory.get_memory_stats()
    print(f"Memory stats: {json.dumps(stats, indent=2)}")
    
    # Close memory
    memory.close()
    
    print("\nEnhancedMemoryManager test completed")

def main():
    """Run all tests."""
    try:
        test_long_term_memory()
        test_memory_encoder()
        test_enhanced_memory_manager()
        
        print("\nAll tests completed successfully!")
        
    except Exception as e:
        logger.error(f"Error during testing: {e}", exc_info=True)
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
