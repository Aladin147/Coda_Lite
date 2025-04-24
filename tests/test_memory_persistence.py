"""
Memory Persistence Test Script

This script tests the memory system's ability to persist and retrieve memories across sessions.
It adds known facts to long-term memory, restarts the memory system, and then queries for those facts.
"""

import os
import sys
import logging
import json
import time
import uuid
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from memory import EnhancedMemoryManager
from config.config_loader import ConfigLoader

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/logs/memory_test_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("memory_test")

def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/memory", exist_ok=True)
    os.makedirs("data/memory/long_term", exist_ok=True)
    os.makedirs("data/memory/test_results", exist_ok=True)

def get_config():
    """Get configuration for memory system."""
    config = ConfigLoader()
    
    # Ensure long-term memory is enabled
    config.set("memory.long_term_enabled", True)
    config.set("memory.long_term_path", "data/memory/long_term")
    config.set("memory.vector_db", "chroma")
    config.set("memory.embedding_model", "all-MiniLM-L6-v2")
    config.set("memory.device", "cpu")
    config.set("memory.auto_persist", True)
    config.set("memory.persist_interval", 2)  # Persist after 2 turns
    
    return config

def create_test_facts():
    """Create a set of test facts with unique identifiers."""
    test_id = uuid.uuid4().hex[:8]
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    
    return [
        {
            "content": f"My name is Aladin. This is test fact {test_id}_1 created at {timestamp}.",
            "metadata": {"test_id": test_id, "fact_number": 1, "category": "personal"}
        },
        {
            "content": f"I like programming in Python. This is test fact {test_id}_2 created at {timestamp}.",
            "metadata": {"test_id": test_id, "fact_number": 2, "category": "preference"}
        },
        {
            "content": f"My favorite color is blue. This is test fact {test_id}_3 created at {timestamp}.",
            "metadata": {"test_id": test_id, "fact_number": 3, "category": "preference"}
        },
        {
            "content": f"I am working on a project called Coda Lite. This is test fact {test_id}_4 created at {timestamp}.",
            "metadata": {"test_id": test_id, "fact_number": 4, "category": "project"}
        },
        {
            "content": f"The capital of France is Paris. This is test fact {test_id}_5 created at {timestamp}.",
            "metadata": {"test_id": test_id, "fact_number": 5, "category": "general"}
        }
    ]

def add_facts_to_memory(memory_manager, facts):
    """Add facts to memory and return their IDs."""
    fact_ids = []
    
    for fact in facts:
        # Add the fact
        fact_id = memory_manager.add_fact(
            fact=fact["content"],
            source="test",
            metadata=fact["metadata"]
        )
        fact_ids.append(fact_id)
        logger.info(f"Added fact: {fact['content']} with ID: {fact_id}")
    
    return fact_ids

def query_facts(memory_manager, facts, min_similarity=0.5):
    """Query for facts and return the results."""
    results = []
    
    for fact in facts:
        # Create a query from the fact
        query = fact["content"].split(". ")[0]  # Use the first sentence as the query
        
        # Query for the fact
        memories = memory_manager.retrieve_relevant_memories(
            query=query,
            limit=5,
            min_similarity=min_similarity
        )
        
        # Check if the fact was found
        found = False
        for memory in memories:
            if fact["content"] in memory.get("content", ""):
                found = True
                break
        
        results.append({
            "query": query,
            "found": found,
            "memories_count": len(memories),
            "memories": memories
        })
        
        logger.info(f"Query: {query}")
        logger.info(f"Found: {found}")
        logger.info(f"Retrieved {len(memories)} memories")
    
    return results

def test_memory_persistence():
    """Test memory persistence across sessions."""
    ensure_directories()
    config = get_config()
    
    # Create test facts
    test_facts = create_test_facts()
    
    # First session: Add facts to memory
    logger.info("=== Starting First Session ===")
    memory_manager_1 = EnhancedMemoryManager(config=config.get_all())
    
    # Add system and user turns to simulate a conversation
    memory_manager_1.add_turn("system", "You are Coda, a helpful assistant.")
    memory_manager_1.add_turn("user", "Hello, who are you?")
    memory_manager_1.add_turn("assistant", "I'm Coda, your voice assistant. How can I help you today?")
    
    # Add facts to memory
    fact_ids = add_facts_to_memory(memory_manager_1, test_facts)
    
    # Force persistence
    memory_manager_1.persist_short_term_memory()
    
    # Close the memory manager
    memory_manager_1.close()
    logger.info("First session completed and memory manager closed")
    
    # Wait a moment to ensure persistence
    time.sleep(2)
    
    # Second session: Query for facts
    logger.info("=== Starting Second Session ===")
    memory_manager_2 = EnhancedMemoryManager(config=config.get_all())
    
    # Add a new conversation turn to simulate a new session
    memory_manager_2.add_turn("system", "You are Coda, a helpful assistant.")
    memory_manager_2.add_turn("user", "Can you tell me what you know about me?")
    
    # Query for facts with different similarity thresholds
    thresholds = [0.7, 0.5, 0.3]
    all_results = {}
    
    for threshold in thresholds:
        logger.info(f"Querying with similarity threshold: {threshold}")
        results = query_facts(memory_manager_2, test_facts, min_similarity=threshold)
        all_results[str(threshold)] = results
    
    # Close the memory manager
    memory_manager_2.close()
    logger.info("Second session completed and memory manager closed")
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_path = f"data/memory/test_results/persistence_test_{timestamp}.json"
    
    with open(results_path, 'w') as f:
        json.dump({
            "test_facts": test_facts,
            "fact_ids": fact_ids,
            "results": all_results
        }, f, indent=2, default=str)
    
    logger.info(f"Results saved to {results_path}")
    
    # Analyze results
    success_count = 0
    total_facts = len(test_facts)
    
    for threshold, results in all_results.items():
        found_count = sum(1 for result in results if result["found"])
        success_rate = found_count / total_facts * 100
        logger.info(f"Threshold {threshold}: Found {found_count}/{total_facts} facts ({success_rate:.2f}%)")
        
        if threshold == "0.5":  # Use the middle threshold for overall success
            success_count = found_count
    
    overall_success_rate = success_count / total_facts * 100
    logger.info(f"Overall success rate: {overall_success_rate:.2f}%")
    
    return {
        "test_facts": test_facts,
        "fact_ids": fact_ids,
        "results": all_results,
        "success_rate": overall_success_rate
    }

def test_memory_retrieval_format():
    """Test how memories are formatted in the context."""
    ensure_directories()
    config = get_config()
    
    # Create memory manager
    memory_manager = EnhancedMemoryManager(config=config.get_all())
    
    # Add system and user turns
    memory_manager.add_turn("system", "You are Coda, a helpful assistant.")
    memory_manager.add_turn("user", "Hello, who are you?")
    memory_manager.add_turn("assistant", "I'm Coda, your voice assistant. How can I help you today?")
    
    # Add a test fact
    test_fact = "My name is Aladin and I am working on a project called Coda Lite."
    memory_manager.add_fact(test_fact, source="test")
    
    # Force persistence
    memory_manager.persist_short_term_memory()
    
    # Get enhanced context
    query = "What is my name and what am I working on?"
    context = memory_manager.get_enhanced_context(query)
    
    # Save context
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    context_path = f"data/memory/test_results/context_format_{timestamp}.json"
    
    with open(context_path, 'w') as f:
        json.dump({
            "query": query,
            "context": context
        }, f, indent=2, default=str)
    
    logger.info(f"Context saved to {context_path}")
    
    # Close the memory manager
    memory_manager.close()
    
    return {
        "query": query,
        "context": context
    }

def test_memory_encoding():
    """Test memory encoding and chunking."""
    ensure_directories()
    config = get_config()
    
    # Create memory manager
    memory_manager = EnhancedMemoryManager(config=config.get_all())
    
    # Create a conversation with multiple turns
    memory_manager.add_turn("system", "You are Coda, a helpful assistant.")
    memory_manager.add_turn("user", "Hello, who are you?")
    memory_manager.add_turn("assistant", "I'm Coda, your voice assistant. How can I help you today?")
    memory_manager.add_turn("user", "Can you tell me about yourself?")
    memory_manager.add_turn("assistant", "I'm an AI assistant designed to help with various tasks. I can answer questions, provide information, and assist with many different topics.")
    memory_manager.add_turn("user", "What can you do?")
    memory_manager.add_turn("assistant", "I can help with a wide range of tasks including answering questions, providing information, assisting with planning, and much more. Is there something specific you'd like help with?")
    
    # Force persistence
    chunks = memory_manager.persist_short_term_memory()
    
    # Get the encoded memories
    memories = memory_manager.long_term.get_all_memories()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    encoding_path = f"data/memory/test_results/encoding_test_{timestamp}.json"
    
    with open(encoding_path, 'w') as f:
        json.dump({
            "chunks_count": chunks,
            "memories": memories
        }, f, indent=2, default=str)
    
    logger.info(f"Encoding results saved to {encoding_path}")
    
    # Close the memory manager
    memory_manager.close()
    
    return {
        "chunks_count": chunks,
        "memories": memories
    }

def test_vector_database():
    """Test vector database persistence."""
    ensure_directories()
    config = get_config()
    
    # Create test facts
    test_facts = create_test_facts()
    
    # First session: Add facts to memory
    logger.info("=== Testing Vector Database Persistence ===")
    memory_manager_1 = EnhancedMemoryManager(config=config.get_all())
    
    # Add facts to memory
    fact_ids = add_facts_to_memory(memory_manager_1, test_facts)
    
    # Get vector database stats before closing
    db_stats_before = memory_manager_1.long_term.get_memory_stats()
    
    # Close the memory manager
    memory_manager_1.close()
    logger.info("First session completed and memory manager closed")
    
    # Wait a moment to ensure persistence
    time.sleep(2)
    
    # Second session: Check if facts are still in the database
    memory_manager_2 = EnhancedMemoryManager(config=config.get_all())
    
    # Get vector database stats after reopening
    db_stats_after = memory_manager_2.long_term.get_memory_stats()
    
    # Check if all facts are still in the database
    all_memories = memory_manager_2.long_term.get_all_memories()
    
    # Check if fact IDs are still in the database
    found_ids = []
    for fact_id in fact_ids:
        memory = memory_manager_2.long_term.get_memory_by_id(fact_id)
        if memory:
            found_ids.append(fact_id)
    
    # Close the memory manager
    memory_manager_2.close()
    
    # Save results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    db_path = f"data/memory/test_results/vector_db_test_{timestamp}.json"
    
    with open(db_path, 'w') as f:
        json.dump({
            "test_facts": test_facts,
            "fact_ids": fact_ids,
            "found_ids": found_ids,
            "db_stats_before": db_stats_before,
            "db_stats_after": db_stats_after,
            "all_memories_count": len(all_memories)
        }, f, indent=2, default=str)
    
    logger.info(f"Vector database test results saved to {db_path}")
    
    # Analyze results
    found_count = len(found_ids)
    total_facts = len(fact_ids)
    success_rate = found_count / total_facts * 100
    
    logger.info(f"Found {found_count}/{total_facts} facts in the database ({success_rate:.2f}%)")
    logger.info(f"DB stats before: {db_stats_before}")
    logger.info(f"DB stats after: {db_stats_after}")
    
    return {
        "test_facts": test_facts,
        "fact_ids": fact_ids,
        "found_ids": found_ids,
        "db_stats_before": db_stats_before,
        "db_stats_after": db_stats_after,
        "all_memories_count": len(all_memories),
        "success_rate": success_rate
    }

def run_all_tests():
    """Run all memory tests and save the results."""
    ensure_directories()
    
    # Run tests
    persistence_results = test_memory_persistence()
    retrieval_results = test_memory_retrieval_format()
    encoding_results = test_memory_encoding()
    vector_db_results = test_vector_database()
    
    # Save combined results
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_path = f"data/memory/test_results/all_tests_{timestamp}.json"
    
    with open(results_path, 'w') as f:
        json.dump({
            "persistence_test": {
                "success_rate": persistence_results["success_rate"]
            },
            "retrieval_format_test": {
                "context_length": len(retrieval_results["context"])
            },
            "encoding_test": {
                "chunks_count": encoding_results["chunks_count"],
                "memories_count": len(encoding_results["memories"])
            },
            "vector_db_test": {
                "success_rate": vector_db_results["success_rate"],
                "memories_count": vector_db_results["all_memories_count"]
            }
        }, f, indent=2)
    
    logger.info(f"All test results saved to {results_path}")
    
    return {
        "persistence_test": persistence_results,
        "retrieval_format_test": retrieval_results,
        "encoding_test": encoding_results,
        "vector_db_test": vector_db_results
    }

if __name__ == "__main__":
    try:
        logger.info("Starting memory system tests")
        results = run_all_tests()
        logger.info("Memory system tests completed successfully")
        
        # Print summary
        print("\n=== Memory System Test Summary ===")
        print(f"Persistence Test Success Rate: {results['persistence_test']['success_rate']:.2f}%")
        print(f"Vector DB Test Success Rate: {results['vector_db_test']['success_rate']:.2f}%")
        print(f"Encoding Test Chunks Count: {results['encoding_test']['chunks_count']}")
        print(f"Retrieval Format Test Context Length: {len(results['retrieval_format_test']['context'])}")
        
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in memory system tests: {e}", exc_info=True)
        sys.exit(1)
