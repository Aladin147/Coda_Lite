"""
Verify Memory Fixes

This script verifies that the memory system fixes have resolved the issues.
It runs the same tests as test_memory_persistence.py but with the patched memory system.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional

# Add parent directory to path to import modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the test script
from tests.test_memory_persistence import (
    ensure_directories, get_config, create_test_facts,
    add_facts_to_memory, query_facts, test_memory_persistence,
    test_memory_retrieval_format, test_memory_encoding,
    test_vector_database, run_all_tests
)

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/logs/verify_fixes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("verify_fixes")

def compare_test_results(before_results, after_results):
    """Compare test results before and after fixes."""
    comparison = {}
    
    # Compare persistence test results
    if "persistence_test" in before_results and "persistence_test" in after_results:
        before_rate = before_results["persistence_test"]["success_rate"]
        after_rate = after_results["persistence_test"]["success_rate"]
        improvement = after_rate - before_rate
        
        comparison["persistence_test"] = {
            "before_rate": before_rate,
            "after_rate": after_rate,
            "improvement": improvement,
            "percent_improvement": improvement / before_rate * 100 if before_rate > 0 else float('inf')
        }
    
    # Compare vector DB test results
    if "vector_db_test" in before_results and "vector_db_test" in after_results:
        before_rate = before_results["vector_db_test"]["success_rate"]
        after_rate = after_results["vector_db_test"]["success_rate"]
        improvement = after_rate - before_rate
        
        comparison["vector_db_test"] = {
            "before_rate": before_rate,
            "after_rate": after_rate,
            "improvement": improvement,
            "percent_improvement": improvement / before_rate * 100 if before_rate > 0 else float('inf')
        }
    
    # Compare encoding test results
    if "encoding_test" in before_results and "encoding_test" in after_results:
        before_chunks = before_results["encoding_test"]["chunks_count"]
        after_chunks = after_results["encoding_test"]["chunks_count"]
        
        comparison["encoding_test"] = {
            "before_chunks": before_chunks,
            "after_chunks": after_chunks,
            "difference": after_chunks - before_chunks
        }
    
    # Compare retrieval format test results
    if "retrieval_format_test" in before_results and "retrieval_format_test" in after_results:
        before_length = len(before_results["retrieval_format_test"]["context"])
        after_length = len(after_results["retrieval_format_test"]["context"])
        
        comparison["retrieval_format_test"] = {
            "before_length": before_length,
            "after_length": after_length,
            "difference": after_length - before_length
        }
    
    return comparison

def run_verification():
    """Run verification tests and compare with previous results."""
    # Load previous test results if available
    previous_results = None
    results_dir = "data/memory/test_results"
    
    if os.path.exists(results_dir):
        # Find the most recent all_tests file
        all_tests_files = [f for f in os.listdir(results_dir) if f.startswith("all_tests_")]
        if all_tests_files:
            latest_file = max(all_tests_files)
            with open(os.path.join(results_dir, latest_file), 'r') as f:
                previous_results = json.load(f)
    
    # Run verification tests
    logger.info("Running verification tests")
    verification_results = run_all_tests()
    
    # Compare results
    if previous_results:
        comparison = compare_test_results(previous_results, verification_results)
        
        # Save comparison
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        comparison_path = f"data/memory/test_results/comparison_{timestamp}.json"
        
        with open(comparison_path, 'w') as f:
            json.dump({
                "timestamp": timestamp,
                "before": previous_results,
                "after": verification_results,
                "comparison": comparison
            }, f, indent=2)
        
        logger.info(f"Comparison saved to {comparison_path}")
        
        return {
            "previous_results": previous_results,
            "verification_results": verification_results,
            "comparison": comparison
        }
    else:
        logger.warning("No previous test results found for comparison")
        return {
            "verification_results": verification_results
        }

if __name__ == "__main__":
    try:
        logger.info("Starting memory fixes verification")
        results = run_verification()
        logger.info("Memory fixes verification completed successfully")
        
        # Print summary
        print("\n=== Memory Fixes Verification Summary ===")
        
        if "comparison" in results:
            comparison = results["comparison"]
            
            if "persistence_test" in comparison:
                persistence = comparison["persistence_test"]
                print(f"Persistence Test: {persistence['before_rate']:.2f}% -> {persistence['after_rate']:.2f}% ({persistence['percent_improvement']:.2f}% improvement)")
            
            if "vector_db_test" in comparison:
                vector_db = comparison["vector_db_test"]
                print(f"Vector DB Test: {vector_db['before_rate']:.2f}% -> {vector_db['after_rate']:.2f}% ({vector_db['percent_improvement']:.2f}% improvement)")
            
            if "encoding_test" in comparison:
                encoding = comparison["encoding_test"]
                print(f"Encoding Test: {encoding['before_chunks']} -> {encoding['after_chunks']} chunks ({encoding['difference']} difference)")
            
            if "retrieval_format_test" in comparison:
                retrieval = comparison["retrieval_format_test"]
                print(f"Retrieval Format Test: {retrieval['before_length']} -> {retrieval['after_length']} messages ({retrieval['difference']} difference)")
        else:
            verification = results["verification_results"]
            print(f"Persistence Test Success Rate: {verification['persistence_test']['success_rate']:.2f}%")
            print(f"Vector DB Test Success Rate: {verification['vector_db_test']['success_rate']:.2f}%")
            print(f"Encoding Test Chunks Count: {verification['encoding_test']['chunks_count']}")
            print(f"Retrieval Format Test Context Length: {len(verification['retrieval_format_test']['context'])}")
        
        sys.exit(0)
    except Exception as e:
        logger.error(f"Error in memory fixes verification: {e}", exc_info=True)
        sys.exit(1)
