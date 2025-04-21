"""Tests for the OllamaLLM class."""

import json
import pytest
from unittest.mock import patch, MagicMock

from llm.ollama_llm import OllamaLLM

def test_ollama_llm_init():
    """Test OllamaLLM initialization."""
    with patch('requests.get') as mock_get:
        # Mock the version response
        mock_response = MagicMock()
        mock_response.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_response

        # Initialize the OllamaLLM
        llm = OllamaLLM(model_name="llama3")

        # Check that the model name is set correctly
        assert llm.model_name == "llama3"
        assert llm.host == "http://localhost:11434"

        # Verify that the version endpoint was called
        mock_get.assert_called_once_with(
            "http://localhost:11434/api/version",
            timeout=5
        )

def test_generate_response():
    """Test generating a response."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        # Mock the version response
        mock_version = MagicMock()
        mock_version.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_version

        # Mock the chat response
        mock_chat = MagicMock()
        mock_chat.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "This is a test response"
            }
        }
        mock_post.return_value = mock_chat

        # Initialize the OllamaLLM and generate a response
        llm = OllamaLLM(model_name="llama3")
        response = llm.generate_response(
            prompt="Hello, world!",
            system_prompt="You are a helpful assistant.",
            temperature=0.5
        )

        # Check the response
        assert response == "This is a test response"

        # Verify that the chat endpoint was called with the correct payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['url'] == "http://localhost:11434/api/chat"

        # Check the payload
        payload = json.loads(call_args['json'])
        assert payload['model'] == "llama3"
        assert payload['messages'] == [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ]
        assert payload['options']['temperature'] == 0.5

def test_generate_structured_output():
    """Test generating structured output."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        # Mock the version response
        mock_version = MagicMock()
        mock_version.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_version

        # Mock the chat response
        mock_chat = MagicMock()
        mock_chat.json.return_value = {
            "message": {
                "role": "assistant",
                "content": '{"action": "get_weather", "parameters": {"location": "New York"}}'
            }
        }
        mock_post.return_value = mock_chat

        # Define the output schema
        output_schema = {
            "type": "object",
            "properties": {
                "action": {"type": "string"},
                "parameters": {"type": "object"}
            }
        }

        # Initialize the OllamaLLM and generate structured output
        llm = OllamaLLM(model_name="llama3")
        response = llm.generate_structured_output(
            prompt="What's the weather in New York?",
            output_schema=output_schema,
            system_prompt="You are a helpful assistant.",
            temperature=0.2
        )

        # Check the response
        assert response == {"action": "get_weather", "parameters": {"location": "New York"}}

        # Verify that the chat endpoint was called with the correct payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['url'] == "http://localhost:11434/api/chat"

        # Check the payload
        payload = json.loads(call_args['json'])
        assert payload['model'] == "llama3"
        assert payload['format'] == output_schema
        assert payload['options']['temperature'] <= 0.5  # Should be adjusted down

def test_chat():
    """Test chat with conversation history."""
    with patch('requests.get') as mock_get, \
         patch('requests.post') as mock_post:
        # Mock the version response
        mock_version = MagicMock()
        mock_version.json.return_value = {"version": "0.1.0"}
        mock_get.return_value = mock_version

        # Mock the chat response
        mock_chat = MagicMock()
        mock_chat.json.return_value = {
            "message": {
                "role": "assistant",
                "content": "I'm doing well, thank you for asking!"
            }
        }
        mock_post.return_value = mock_chat

        # Initialize the OllamaLLM
        llm = OllamaLLM(model_name="llama3")

        # Create a conversation history
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, how are you?"},
        ]

        # Generate a response
        response = llm.chat(messages=messages, temperature=0.7)

        # Check the response
        assert response == "I'm doing well, thank you for asking!"

        # Verify that the chat endpoint was called with the correct payload
        mock_post.assert_called_once()
        call_args = mock_post.call_args[1]
        assert call_args['url'] == "http://localhost:11434/api/chat"

        # Check the payload
        payload = json.loads(call_args['json'])
        assert payload['model'] == "llama3"
        assert payload['messages'] == messages
        assert payload['options']['temperature'] == 0.7
