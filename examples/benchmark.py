#!/usr/bin/env python3
"""
Benchmark script to measure the performance of the voice loop.
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

logger = logging.getLogger("benchmark")

# Import modules
from config.config_loader import ConfigLoader
from stt import WhisperSTT
from llm import OllamaLLM
from tts import create_tts

def benchmark_sequential(config, test_text, iterations=3):
    """Benchmark sequential processing (STT -> LLM -> TTS)."""
    print("\nBenchmarking Sequential Processing")
    print("----------------------------------")

    # Initialize components
    stt = WhisperSTT(
        model_size=config.get("stt.model_size", "base"),
        device=config.get("stt.device", "cuda"),
        compute_type=config.get("stt.compute_type", "float16"),
        language=config.get("stt.language", "en"),
        vad_filter=True
    )

    llm = OllamaLLM(
        model_name=config.get("llm.model_name", "llama3"),
        host="http://localhost:11434",
        timeout=120
    )

    tts = create_tts(
        engine="csm",
        language=config.get("tts.language", "EN"),
        voice=config.get("tts.voice", "EN-US"),
        device=config.get("tts.device", "cuda")
    )

    # Load system prompt
    system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
    try:
        with open(system_prompt_file, 'r') as f:
            system_prompt = f.read().strip()
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        system_prompt = "You are Coda, a helpful voice assistant running locally on the user's computer."

    # Initialize conversation history
    conversation_history = [{"role": "system", "content": system_prompt}]

    total_time = 0
    llm_times = []
    tts_times = []

    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}")

        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": test_text})

        # Measure LLM time
        llm_start = time.time()
        response = llm.chat(
            messages=conversation_history,
            temperature=config.get("llm.temperature", 0.7),
            max_tokens=config.get("llm.max_tokens", 256),
            stream=False
        )
        llm_end = time.time()
        llm_time = llm_end - llm_start
        llm_times.append(llm_time)

        print(f"LLM Response: {response}")
        print(f"LLM Time: {llm_time:.2f} seconds")

        # Add assistant message to conversation history
        conversation_history.append({"role": "assistant", "content": response})

        # Measure TTS time
        tts_start = time.time()
        tts.speak(response)
        tts_end = time.time()
        tts_time = tts_end - tts_start
        tts_times.append(tts_time)

        print(f"TTS Time: {tts_time:.2f} seconds")

        # Calculate total time
        iteration_time = llm_time + tts_time
        total_time += iteration_time
        print(f"Total Time: {iteration_time:.2f} seconds")

    # Calculate averages
    avg_llm_time = sum(llm_times) / len(llm_times)
    avg_tts_time = sum(tts_times) / len(tts_times)
    avg_total_time = total_time / iterations

    print("\nSequential Processing Results:")
    print(f"Average LLM Time: {avg_llm_time:.2f} seconds")
    print(f"Average TTS Time: {avg_tts_time:.2f} seconds")
    print(f"Average Total Time: {avg_total_time:.2f} seconds")

    # Clean up
    stt.close()

    return avg_llm_time, avg_tts_time, avg_total_time

def benchmark_concurrent(config, test_text, iterations=3):
    """Benchmark concurrent processing (LLM and TTS in separate threads)."""
    print("\nBenchmarking Concurrent Processing")
    print("----------------------------------")

    # Initialize components
    stt = WhisperSTT(
        model_size=config.get("stt.model_size", "base"),
        device=config.get("stt.device", "cuda"),
        compute_type=config.get("stt.compute_type", "float16"),
        language=config.get("stt.language", "en"),
        vad_filter=True
    )

    llm = OllamaLLM(
        model_name=config.get("llm.model_name", "llama3"),
        host="http://localhost:11434",
        timeout=120
    )

    tts = create_tts(
        engine="csm",
        language=config.get("tts.language", "EN"),
        voice=config.get("tts.voice", "EN-US"),
        device=config.get("tts.device", "cuda")
    )

    # Load system prompt
    system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
    try:
        with open(system_prompt_file, 'r') as f:
            system_prompt = f.read().strip()
    except Exception as e:
        logger.error(f"Error loading system prompt: {e}")
        system_prompt = "You are Coda, a helpful voice assistant running locally on the user's computer."

    # Initialize conversation history
    conversation_history = [{"role": "system", "content": system_prompt}]

    # Initialize response queue
    response_queue = Queue()

    # TTS worker thread
    def tts_worker():
        while not response_queue.empty():
            try:
                response = response_queue.get()
                tts.speak(response)
                response_queue.task_done()
            except Exception as e:
                logger.error(f"Error in TTS worker: {e}")

    total_time = 0
    llm_times = []
    tts_times = []
    concurrent_times = []

    for i in range(iterations):
        print(f"\nIteration {i+1}/{iterations}")

        # Add user message to conversation history
        conversation_history.append({"role": "user", "content": test_text})

        # Start timing
        start_time = time.time()

        # Measure LLM time
        llm_start = time.time()
        response = llm.chat(
            messages=conversation_history,
            temperature=config.get("llm.temperature", 0.7),
            max_tokens=config.get("llm.max_tokens", 256),
            stream=False
        )
        llm_end = time.time()
        llm_time = llm_end - llm_start
        llm_times.append(llm_time)

        print(f"LLM Response: {response}")
        print(f"LLM Time: {llm_time:.2f} seconds")

        # Add assistant message to conversation history
        conversation_history.append({"role": "assistant", "content": response})

        # Add response to queue
        response_queue.put(response)

        # Start TTS worker thread
        tts_start = time.time()
        tts_thread = threading.Thread(target=tts_worker)
        tts_thread.start()

        # Wait for TTS to complete
        response_queue.join()
        tts_end = time.time()
        tts_time = tts_end - tts_start
        tts_times.append(tts_time)

        print(f"TTS Time: {tts_time:.2f} seconds")

        # Calculate total time
        end_time = time.time()
        concurrent_time = end_time - start_time
        concurrent_times.append(concurrent_time)
        total_time += concurrent_time
        print(f"Concurrent Time: {concurrent_time:.2f} seconds")

    # Calculate averages
    avg_llm_time = sum(llm_times) / len(llm_times)
    avg_tts_time = sum(tts_times) / len(tts_times)
    avg_concurrent_time = sum(concurrent_times) / len(concurrent_times)

    print("\nConcurrent Processing Results:")
    print(f"Average LLM Time: {avg_llm_time:.2f} seconds")
    print(f"Average TTS Time: {avg_tts_time:.2f} seconds")
    print(f"Average Concurrent Time: {avg_concurrent_time:.2f} seconds")

    # Clean up
    stt.close()

    return avg_llm_time, avg_tts_time, avg_concurrent_time

def main():
    """Main benchmark function."""
    try:
        # Load configuration
        config = ConfigLoader()

        # Test text
        test_text = "What's the weather like today in New York City?"

        print("=" * 50)
        print("Coda Lite Performance Benchmark")
        print("=" * 50)

        # Benchmark sequential processing
        seq_llm_time, seq_tts_time, seq_total_time = benchmark_sequential(config, test_text)

        # Benchmark concurrent processing
        con_llm_time, con_tts_time, con_total_time = benchmark_concurrent(config, test_text)

        # Calculate improvement
        time_improvement = seq_total_time - con_total_time
        percentage_improvement = (time_improvement / seq_total_time) * 100

        print("\n" + "=" * 50)
        print("Benchmark Results")
        print("=" * 50)
        print(f"Sequential Processing: {seq_total_time:.2f} seconds")
        print(f"Concurrent Processing: {con_total_time:.2f} seconds")
        print(f"Time Improvement: {time_improvement:.2f} seconds ({percentage_improvement:.2f}%)")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
