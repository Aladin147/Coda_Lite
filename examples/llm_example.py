#!/usr/bin/env python3
"""
Example script demonstrating the use of the OllamaLLM class.
"""

import os
import sys
import time
import json
import logging
from pathlib import Path

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

from llm import OllamaLLM

def simple_response_example():
    """Example of generating a simple response."""
    print("\n=== Generating a simple response ===")
    
    # Initialize the OllamaLLM module
    llm = OllamaLLM(
        model_name="llama3",  # Use your preferred model
        host="http://localhost:11434"
    )
    
    # Define a prompt and system prompt
    prompt = "What are three interesting facts about the moon?"
    system_prompt = "You are a helpful, concise assistant. Keep your answers brief and to the point."
    
    # Generate a response
    start_time = time.time()
    response = llm.generate_response(
        prompt=prompt,
        system_prompt=system_prompt,
        temperature=0.7
    )
    end_time = time.time()
    
    print(f"Prompt: {prompt}")
    print(f"Response (generated in {end_time - start_time:.2f} seconds):")
    print(response)

def structured_output_example():
    """Example of generating structured output."""
    print("\n=== Generating structured output ===")
    
    # Initialize the OllamaLLM module
    llm = OllamaLLM(
        model_name="llama3",  # Use your preferred model
        host="http://localhost:11434"
    )
    
    # Define a prompt and output schema
    prompt = "What's the weather like in Paris today?"
    
    # Define the schema for the structured output
    output_schema = {
        "type": "object",
        "properties": {
            "action": {
                "type": "string",
                "enum": ["get_weather", "unknown_location", "need_more_info"]
            },
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {"type": "string"},
                    "date": {"type": "string"}
                },
                "required": ["location"]
            }
        },
        "required": ["action", "parameters"]
    }
    
    # Generate structured output
    start_time = time.time()
    response = llm.generate_structured_output(
        prompt=prompt,
        output_schema=output_schema,
        temperature=0.2  # Lower temperature for more deterministic outputs
    )
    end_time = time.time()
    
    print(f"Prompt: {prompt}")
    print(f"Structured Response (generated in {end_time - start_time:.2f} seconds):")
    print(json.dumps(response, indent=2))

def conversation_example():
    """Example of having a conversation."""
    print("\n=== Having a conversation ===")
    
    # Initialize the OllamaLLM module
    llm = OllamaLLM(
        model_name="llama3",  # Use your preferred model
        host="http://localhost:11434"
    )
    
    # Create a conversation history
    messages = [
        {"role": "system", "content": "You are a helpful, concise assistant named Coda."},
        {"role": "user", "content": "Hello, who are you?"}
    ]
    
    # Generate a response
    start_time = time.time()
    response = llm.chat(
        messages=messages,
        temperature=0.7
    )
    end_time = time.time()
    
    print("User: Hello, who are you?")
    print(f"Assistant (generated in {end_time - start_time:.2f} seconds): {response}")
    
    # Add the assistant's response to the conversation
    messages.append({"role": "assistant", "content": response})
    
    # Continue the conversation
    messages.append({"role": "user", "content": "What can you help me with?"})
    
    # Generate another response
    start_time = time.time()
    response = llm.chat(
        messages=messages,
        temperature=0.7
    )
    end_time = time.time()
    
    print("User: What can you help me with?")
    print(f"Assistant (generated in {end_time - start_time:.2f} seconds): {response}")

if __name__ == "__main__":
    # Check if Ollama is running
    try:
        # Run the examples
        simple_response_example()
        structured_output_example()
        conversation_example()
    except ConnectionError as e:
        print(f"Error: {e}")
        print("Make sure Ollama is running and accessible at http://localhost:11434")
        print("You can start Ollama by running 'ollama serve' in a terminal")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)
