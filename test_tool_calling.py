#!/usr/bin/env python3
"""
Test script for tool calling in Coda Lite.
This script manually tests the tool calling pipeline to ensure it's working correctly.
"""

import logging
import json
from datetime import datetime
import re

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S"
)
logger = logging.getLogger(__name__)

# Import the LLM module
from llm.ollama_llm import OllamaLLM

def extract_clean_response(response: str) -> str:
    """Remove any JSON blocks and clean up the response."""
    # Remove any JSON blocks (more aggressive pattern)
    response = re.sub(r'\{.*?"tool_call".*?\}', '', response, flags=re.DOTALL)
    response = re.sub(r'\{.*?\}', '', response, flags=re.DOTALL)  # Remove any remaining JSON

    # Remove any trailing/leading whitespace and normalize spacing
    response = response.strip()
    response = re.sub(r'\s+', ' ', response)

    # Remove any tool-related mentions
    response = re.sub(r'tool_call', '', response)
    response = re.sub(r'tool result', '', response, flags=re.IGNORECASE)
    response = re.sub(r'according to the tool', '', response, flags=re.IGNORECASE)
    response = re.sub(r'the tool says', '', response, flags=re.IGNORECASE)

    # Remove phrases like "Let me check" or "I found that"
    response = re.sub(r'let me check', '', response, flags=re.IGNORECASE)
    response = re.sub(r'i found that', '', response, flags=re.IGNORECASE)
    response = re.sub(r'i can tell you that', '', response, flags=re.IGNORECASE)

    # Clean up any double spaces or punctuation issues from the removals
    response = re.sub(r'\s+', ' ', response)  # Normalize spaces again
    response = re.sub(r'\s+\.', '.', response)  # Fix spaces before periods
    response = re.sub(r'^[,\.\s]+', '', response)  # Remove leading punctuation
    response = re.sub(r'\s+$', '', response)  # Remove trailing spaces

    # If the response is too short after cleaning, return a generic message
    if len(response) < 5:
        return "I'm sorry, I couldn't process that properly."

    return response

def test_tool_detection():
    """Test the tool detection phase."""
    logger.info("Testing tool detection phase...")

    # Initialize the LLM
    llm = OllamaLLM(
        model_name="llama3",
        host="http://localhost:11434",
        timeout=120
    )

    # Create a system prompt for tool detection
    system_prompt = """You are Coda, a helpful voice assistant.

You can use tools to help answer user questions.
Available tools:
- get_time: Get the current time.
- get_date: Get the current date.
- tell_joke: Tell a random joke.

If you decide a tool is needed, respond ONLY with JSON in this format:
{ "tool_call": { "name": "tool_name", "args": { ... } } }

Do NOT include explanations, just the JSON. The system will execute the tool and provide the result.
If no tool is needed, respond naturally without JSON.
"""

    # Test with a query that should trigger a tool call
    user_query = "What time is it right now?"

    # Create the context
    context = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_query}
    ]

    # Generate a response
    logger.info("Generating tool detection response...")
    response = ""
    for chunk in llm.chat(
        messages=context,
        temperature=0.7,
        max_tokens=256,
        stream=True
    ):
        response += chunk

    logger.info(f"Tool detection response: {response}")

    # Check if the response contains a tool call
    if "{" in response and "tool_call" in response:
        logger.info("✅ Tool call detected successfully!")

        # Try to extract the tool call
        try:
            # Find the JSON object in the response
            json_start = response.find("{")
            json_end = response.rfind("}") + 1
            json_str = response[json_start:json_end]

            # Parse the JSON
            tool_call = json.loads(json_str)

            # Extract the tool name and args
            tool_name = tool_call.get("tool_call", {}).get("name")
            tool_args = tool_call.get("tool_call", {}).get("args", {})

            logger.info(f"Tool name: {tool_name}")
            logger.info(f"Tool args: {tool_args}")

            # Execute the tool (simulate)
            if tool_name == "get_time":
                tool_result = datetime.now().strftime("It's %H:%M.")
            elif tool_name == "get_date":
                tool_result = datetime.now().strftime("Today is %A, %B %d, %Y.")
            elif tool_name == "tell_joke":
                tool_result = "Why don't scientists trust atoms? Because they make up everything!"
            else:
                tool_result = f"Unknown tool: {tool_name}"

            logger.info(f"Tool result: {tool_result}")

            # Test the summarization phase
            test_summarization(user_query, tool_result)
        except Exception as e:
            logger.error(f"Error extracting tool call: {e}")
    else:
        logger.warning("❌ No tool call detected in the response.")

def test_summarization(user_query, tool_result):
    """Test the summarization phase."""
    logger.info("Testing summarization phase...")

    # Initialize the LLM
    llm = OllamaLLM(
        model_name="llama3",
        host="http://localhost:11434",
        timeout=120
    )

    # Create a system prompt for summarization
    summarization_prompt = """You are Coda, a helpful and natural-sounding voice assistant.

You have received the result of a tool call. DO NOT output any JSON.
DO NOT repeat the tool call. DO NOT re-call the tool.
DO NOT include any curly braces {} in your response.
DO NOT mention tools, functions, or APIs.
DO NOT use phrases like "according to the tool" or "the tool says".

Respond clearly and casually with just the final answer. Do not say things like "Let me check" or "I found that". Just deliver the result naturally.

Examples:
- [TOOL RESULT] The current time is 2:45 PM → It's 2:45 PM.
- [TOOL RESULT] Today's date is April 22, 2025 → Today is April 22nd, 2025.
- [TOOL RESULT] Here's a joke: Why don't scientists trust atoms? Because they make up everything! → Why don't scientists trust atoms? Because they make up everything!

Keep your response brief, conversational, and completely free of any JSON formatting.
"""

    # Create the context for summarization
    messages = [
        {"role": "system", "content": summarization_prompt},
        {"role": "system", "content": f"[TOOL RESULT] {tool_result}"},
        {"role": "user", "content": user_query}
    ]

    # Log the messages for debugging
    logger.info("Summarization messages:")
    for i, msg in enumerate(messages):
        logger.info(f"  Message {i}: role={msg['role']}, content={msg['content']}")

    # Generate a natural language summary
    logger.info("Generating summarization response...")
    raw_summary = ""
    for chunk in llm.chat(
        messages=messages,
        temperature=0.7,
        max_tokens=256,
        stream=True
    ):
        raw_summary += chunk

    logger.info(f"Raw summary: {raw_summary}")

    # Clean the response to remove any JSON or tool call patterns
    final_response = extract_clean_response(raw_summary)

    logger.info(f"Final cleaned response: {final_response}")

    # Check if the final response still contains JSON
    if "{" in final_response or "}" in final_response or "tool_call" in final_response.lower():
        logger.warning("❌ JSON still detected in the final response.")
    else:
        logger.info("✅ Final response is clean and natural!")

if __name__ == "__main__":
    logger.info("Starting tool calling test...")
    test_tool_detection()
    logger.info("Tool calling test complete.")
