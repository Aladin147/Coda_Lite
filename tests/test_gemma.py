"""
Test script for Gemma 2B LLM integration.
"""

import time
import logging
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.insert(0, str(Path(__file__).parent.parent))

from llm import OllamaLLM
from config.config_loader import ConfigLoader

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger("gemma_test")

def test_simple_response():
    """Test generating a simple response with Gemma 2B."""
    logger.info("=== Testing simple response generation with Gemma 2B ===")

    # Load configuration
    config = ConfigLoader()

    # Initialize the OllamaLLM module with Gemma 2B
    llm = OllamaLLM(
        model_name="gemma:2b",
        host="http://localhost:11434"
    )

    # Load system prompt
    system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Define a prompt
    prompt = "What are three interesting facts about the moon?"

    # Generate a response
    logger.info(f"Prompt: {prompt}")
    logger.info("Generating response...")

    start_time = time.time()
    response_generator = llm.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )

    # Collect the response
    response_chunks = []
    for chunk in response_generator:
        response_chunks.append(chunk)
    response = "".join(response_chunks)

    end_time = time.time()

    # Log the response and timing
    logger.info(f"Response (generated in {end_time - start_time:.2f} seconds):")
    logger.info(response)

    return end_time - start_time

def test_tool_usage():
    """Test tool usage with Gemma 2B."""
    logger.info("=== Testing tool usage with Gemma 2B ===")

    # Load configuration
    config = ConfigLoader()

    # Initialize the OllamaLLM module with Gemma 2B
    llm = OllamaLLM(
        model_name="gemma:2b",
        host="http://localhost:11434"
    )

    # Load system prompt
    system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Load tool prompt
    tool_prompt_file = config.get("llm.tool_prompt_file", "config/prompts/tools.txt")
    with open(tool_prompt_file, "r", encoding="utf-8") as f:
        tool_prompt = f.read()

    # Combine prompts
    combined_prompt = f"{system_prompt}\n\n{tool_prompt}"

    # Define a prompt that should trigger tool usage
    prompt = "What's the weather like in New York right now?"

    # Generate a response
    logger.info(f"Prompt: {prompt}")
    logger.info("Generating response...")

    start_time = time.time()
    response_generator = llm.generate_response(
        prompt=prompt,
        system_prompt=combined_prompt,
        temperature=0.7
    )

    # Collect the response
    response_chunks = []
    for chunk in response_generator:
        response_chunks.append(chunk)
    response = "".join(response_chunks)

    end_time = time.time()

    # Log the response and timing
    logger.info(f"Response (generated in {end_time - start_time:.2f} seconds):")
    logger.info(response)

    return end_time - start_time

def test_structured_output():
    """Test structured output generation with Gemma 2B."""
    logger.info("=== Testing structured output generation with Gemma 2B ===")

    # Initialize the OllamaLLM module with Gemma 2B
    llm = OllamaLLM(
        model_name="gemma:2b",
        host="http://localhost:11434"
    )

    # Define a prompt and output schema
    prompt = "Extract the person, location, and date from this text: 'John Smith visited Paris on May 15, 2023.'"

    # Define the schema for the structured output
    output_schema = {
        "type": "object",
        "properties": {
            "person": {"type": "string"},
            "location": {"type": "string"},
            "date": {"type": "string"}
        },
        "required": ["person", "location", "date"]
    }

    # Generate structured output
    logger.info(f"Prompt: {prompt}")
    logger.info("Generating structured output...")

    start_time = time.time()
    try:
        response = llm.generate_structured_output(
            prompt=prompt,
            output_schema=output_schema,
            temperature=0.3
        )
        end_time = time.time()

        # Log the response and timing
        logger.info(f"Response (generated in {end_time - start_time:.2f} seconds):")
        logger.info(response)
    except Exception as e:
        logger.error(f"Error generating structured output: {e}")
        end_time = time.time()

    return end_time - start_time

def compare_with_llama():
    """Compare Gemma 2B with LLaMA 3."""
    logger.info("=== Comparing Gemma 2B with LLaMA 3 ===")

    # Load configuration
    config = ConfigLoader()

    # Load system prompt
    system_prompt_file = config.get("llm.system_prompt_file", "config/prompts/system.txt")
    with open(system_prompt_file, "r", encoding="utf-8") as f:
        system_prompt = f.read()

    # Define a prompt
    prompt = "Explain quantum computing in simple terms."

    # Test with Gemma 2B
    logger.info("Testing with Gemma 2B...")
    gemma_llm = OllamaLLM(
        model_name="gemma:2b",
        host="http://localhost:11434"
    )

    start_time = time.time()
    gemma_response_generator = gemma_llm.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )

    # Collect the response
    gemma_response_chunks = []
    for chunk in gemma_response_generator:
        gemma_response_chunks.append(chunk)
    gemma_response = "".join(gemma_response_chunks)

    gemma_time = time.time() - start_time

    # Test with LLaMA 3
    logger.info("Testing with LLaMA 3...")
    llama_llm = OllamaLLM(
        model_name="llama3",
        host="http://localhost:11434"
    )

    start_time = time.time()
    llama_response_generator = llama_llm.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )

    # Collect the response
    llama_response_chunks = []
    for chunk in llama_response_generator:
        llama_response_chunks.append(chunk)
    llama_response = "".join(llama_response_chunks)

    llama_time = time.time() - start_time

    # Log results
    logger.info(f"Gemma 2B response (generated in {gemma_time:.2f} seconds):")
    logger.info(gemma_response)

    logger.info(f"LLaMA 3 response (generated in {llama_time:.2f} seconds):")
    logger.info(llama_response)

    # Compare times
    logger.info(f"Time comparison: Gemma 2B: {gemma_time:.2f}s, LLaMA 3: {llama_time:.2f}s")

    # Avoid division by zero
    if gemma_time < 0.001:
        gemma_time = 0.001
    if llama_time < 0.001:
        llama_time = 0.001

    if gemma_time < llama_time:
        logger.info(f"Gemma 2B is {(llama_time / gemma_time):.2f}x faster than LLaMA 3")
    else:
        logger.info(f"LLaMA 3 is {(gemma_time / llama_time):.2f}x faster than Gemma 2B")

    return {
        "gemma_time": gemma_time,
        "llama_time": llama_time,
        "gemma_response": gemma_response,
        "llama_response": llama_response
    }

if __name__ == "__main__":
    logger.info("Starting Gemma 2B tests...")

    # Run tests
    simple_time = test_simple_response()
    logger.info("\n")

    tool_time = test_tool_usage()
    logger.info("\n")

    structured_time = test_structured_output()
    logger.info("\n")

    comparison = compare_with_llama()

    # Summarize results
    logger.info("\n=== Test Summary ===")
    logger.info(f"Simple response generation: {simple_time:.2f} seconds")
    logger.info(f"Tool usage: {tool_time:.2f} seconds")
    logger.info(f"Structured output generation: {structured_time:.2f} seconds")
    logger.info(f"Comparison - Gemma 2B: {comparison['gemma_time']:.2f}s, LLaMA 3: {comparison['llama_time']:.2f}s")

    if comparison['gemma_time'] < comparison['llama_time']:
        speedup = comparison['llama_time'] / comparison['gemma_time']
        logger.info(f"Gemma 2B is {speedup:.2f}x faster than LLaMA 3")
    else:
        speedup = comparison['gemma_time'] / comparison['llama_time']
        logger.info(f"LLaMA 3 is {speedup:.2f}x faster than Gemma 2B")
