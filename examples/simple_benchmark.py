#!/usr/bin/env python3
"""
Simple benchmark script to measure the performance improvements from threading.
"""

import os
import sys
import time
import logging
import threading
from pathlib import Path
from queue import Queue

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("simple_benchmark")

# Import modules
from tts import create_tts

def test_sequential(iterations=3):
    """Test sequential TTS processing."""
    print("\nTesting Sequential Processing")
    print("----------------------------")
    
    # Initialize TTS
    tts = create_tts(
        engine="csm",
        language="EN",
        voice="EN-US",
        device="cuda"
    )
    
    # Test text
    test_texts = [
        "Hello, I am Coda, your voice assistant. How can I help you today?",
        "The weather in New York City is currently 72 degrees and sunny with a light breeze.",
        "I'm sorry, I don't have access to real-time information or the internet."
    ]
    
    total_time = 0
    
    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}")
        
        text = test_texts[i % len(test_texts)]
        print(f"Text: {text}")
        
        # Measure time
        start_time = time.time()
        tts.speak(text)
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        
        print(f"Time: {elapsed_time:.2f} seconds")
    
    avg_time = total_time / iterations
    print(f"\nAverage Time: {avg_time:.2f} seconds")
    
    return avg_time

def test_concurrent(iterations=3):
    """Test concurrent TTS processing with threading."""
    print("\nTesting Concurrent Processing")
    print("----------------------------")
    
    # Initialize TTS
    tts = create_tts(
        engine="csm",
        language="EN",
        voice="EN-US",
        device="cuda"
    )
    
    # Test text
    test_texts = [
        "Hello, I am Coda, your voice assistant. How can I help you today?",
        "The weather in New York City is currently 72 degrees and sunny with a light breeze.",
        "I'm sorry, I don't have access to real-time information or the internet."
    ]
    
    # Create response queue
    response_queue = Queue()
    
    # TTS worker thread
    def tts_worker():
        while not response_queue.empty():
            try:
                text = response_queue.get()
                tts.speak(text)
                response_queue.task_done()
            except Exception as e:
                logger.error(f"Error in TTS worker: {e}")
    
    total_time = 0
    
    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}")
        
        text = test_texts[i % len(test_texts)]
        print(f"Text: {text}")
        
        # Add text to queue
        response_queue.put(text)
        
        # Measure time
        start_time = time.time()
        
        # Start TTS worker thread
        tts_thread = threading.Thread(target=tts_worker)
        tts_thread.start()
        
        # Wait for TTS to complete
        response_queue.join()
        
        end_time = time.time()
        
        elapsed_time = end_time - start_time
        total_time += elapsed_time
        
        print(f"Time: {elapsed_time:.2f} seconds")
    
    avg_time = total_time / iterations
    print(f"\nAverage Time: {avg_time:.2f} seconds")
    
    return avg_time

def main():
    """Main benchmark function."""
    try:
        print("=" * 50)
        print("Coda Lite Simple Performance Benchmark")
        print("=" * 50)
        
        # Test sequential processing
        seq_time = test_sequential()
        
        # Test concurrent processing
        con_time = test_concurrent()
        
        # Calculate improvement
        time_improvement = seq_time - con_time
        percentage_improvement = (time_improvement / seq_time) * 100 if seq_time > 0 else 0
        
        print("\n" + "=" * 50)
        print("Benchmark Results")
        print("=" * 50)
        print(f"Sequential Processing: {seq_time:.2f} seconds")
        print(f"Concurrent Processing: {con_time:.2f} seconds")
        print(f"Time Improvement: {time_improvement:.2f} seconds ({percentage_improvement:.2f}%)")
        
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
