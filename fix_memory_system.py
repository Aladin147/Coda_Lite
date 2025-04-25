#!/usr/bin/env python3
"""
Memory System Fix Script

This script runs the memory system tests, applies the fixes, and verifies the results.
"""

import os
import sys
import logging
import json
import time
from datetime import datetime
import argparse

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f"data/logs/memory_fix_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("memory_fix")

def ensure_directories():
    """Ensure all required directories exist."""
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("data/memory", exist_ok=True)
    os.makedirs("data/memory/long_term", exist_ok=True)
    os.makedirs("data/memory/test_results", exist_ok=True)
    os.makedirs("data/memory/backups", exist_ok=True)

def run_tests():
    """Run the memory system tests."""
    logger.info("Running memory system tests...")
    
    try:
        from tests.test_memory_persistence import run_all_tests
        
        # Run the tests
        results = run_all_tests()
        
        # Print summary
        print("\n=== Memory System Test Summary ===")
        print(f"Persistence Test Success Rate: {results['persistence_test']['success_rate']:.2f}%")
        print(f"Vector DB Test Success Rate: {results['vector_db_test']['success_rate']:.2f}%")
        print(f"Encoding Test Chunks Count: {results['encoding_test']['chunks_count']}")
        print(f"Retrieval Format Test Context Length: {len(results['retrieval_format_test']['context'])}")
        
        return results
    except Exception as e:
        logger.error(f"Error running memory system tests: {e}", exc_info=True)
        return None

def apply_fixes():
    """Apply the memory system fixes."""
    logger.info("Applying memory system fixes...")
    
    try:
        from tests.memory_system_fixes import apply_all_fixes
        
        # Apply the fixes
        results = apply_all_fixes()
        
        # Print summary
        print("\n=== Memory System Fixes Summary ===")
        print(f"Backup Directory: {results['backup_dir']}")
        print(f"Persistence Fixes: {results['persistence_fixes']}")
        print(f"Retrieval Fixes: {results['retrieval_fixes']}")
        print(f"Encoding Fixes: {results['encoding_fixes']}")
        print(f"Integration Fixes: {results['integration_fixes']}")
        print(f"Vector DB Fixes: {results['vector_db_fixes']}")
        print(f"Configuration Fixes: {results['config_fixes']}")
        
        return results
    except Exception as e:
        logger.error(f"Error applying memory system fixes: {e}", exc_info=True)
        return None

def verify_fixes():
    """Verify the memory system fixes."""
    logger.info("Verifying memory system fixes...")
    
    try:
        from tests.verify_memory_fixes import run_verification
        
        # Run verification
        results = run_verification()
        
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
        
        return results
    except Exception as e:
        logger.error(f"Error verifying memory system fixes: {e}", exc_info=True)
        return None

def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Memory System Fix Script")
    parser.add_argument("--test", action="store_true", help="Run memory system tests")
    parser.add_argument("--fix", action="store_true", help="Apply memory system fixes")
    parser.add_argument("--verify", action="store_true", help="Verify memory system fixes")
    parser.add_argument("--all", action="store_true", help="Run all steps (test, fix, verify)")
    
    args = parser.parse_args()
    
    # If no arguments are provided, run all steps
    if not (args.test or args.fix or args.verify or args.all):
        args.all = True
    
    # Ensure all required directories exist
    ensure_directories()
    
    # Run the requested steps
    if args.test or args.all:
        run_tests()
    
    if args.fix or args.all:
        apply_fixes()
    
    if args.verify or args.all:
        verify_fixes()
    
    logger.info("Memory system fix script completed")

if __name__ == "__main__":
    main()
