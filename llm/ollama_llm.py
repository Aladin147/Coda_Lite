"""
Ollama-based LLM implementation for Coda Lite.
Handles interaction with local LLMs like LLaMA 3 and DeepSeek.
"""

import json
import time
from typing import Dict, List, Optional, Union, Any, Generator

import requests

import logging
logger = logging.getLogger("coda.llm")

# Define message types for type hints
Message = Dict[str, str]
MessageList = List[Message]

class OllamaLLM:
    """LLM implementation using Ollama."""

    def __init__(self,
                 model_name: str = "llama3",
                 host: str = "http://localhost:11434",
                 timeout: int = 120,
                 keep_alive: str = "5m"):
        """
        Initialize the OllamaLLM module.

        Args:
            model_name (str): Name of the Ollama model to use.
                Default: "llama3"
            host (str): Host URL for Ollama API.
                Default: "http://localhost:11434"
            timeout (int): Request timeout in seconds.
                Default: 120
            keep_alive (str): Duration to keep model loaded in memory.
                Default: "5m"
        """
        self.model_name = model_name
        self.host = host.rstrip('/')
        self.timeout = timeout
        self.keep_alive = keep_alive

        logger.info(f"Initializing OllamaLLM with model: {model_name} at {host}")

        # Check if Ollama is running
        try:
            self._check_ollama_status()
            logger.info("Successfully connected to Ollama")
        except Exception as e:
            logger.error(f"Failed to connect to Ollama: {e}")
            raise

    def _check_ollama_status(self) -> Dict[str, str]:
        """Check if Ollama is running and get version."""
        try:
            response = requests.get(f"{self.host}/api/version", timeout=5)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to Ollama: {e}")
            raise ConnectionError(f"Could not connect to Ollama at {self.host}. Is it running?") from e

    def _format_messages(self, prompt: str, system_prompt: Optional[str] = None) -> MessageList:
        """Format messages for the chat API."""
        messages = []

        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        messages.append({"role": "user", "content": prompt})

        return messages

    def generate_response(self,
                         prompt: str,
                         system_prompt: Optional[str] = None,
                         temperature: float = 0.7,
                         max_tokens: Optional[int] = None,
                         stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        Generate a response from the LLM.

        Args:
            prompt (str): User prompt/query
            system_prompt (str, optional): System prompt to guide the model
            temperature (float): Sampling temperature (0.0 to 1.0)
            max_tokens (int, optional): Maximum number of tokens to generate
            stream (bool): Whether to stream the response

        Returns:
            str: Generated response
        """
        logger.info(f"Generating response for prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

        messages = self._format_messages(prompt, system_prompt)

        try:
            start_time = time.time()

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                },
                "keep_alive": self.keep_alive
            }

            if max_tokens is not None:
                payload["options"]["num_predict"] = max_tokens

            # Make request to Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        full_response += content
                        yield content  # Yield each chunk for streaming
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                content = result.get("message", {}).get("content", "")

                end_time = time.time()
                logger.info(f"Response generated in {end_time - start_time:.2f} seconds")

                return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise

    def generate_structured_output(self,
                                  prompt: str,
                                  output_schema: Dict[str, Any],
                                  system_prompt: Optional[str] = None,
                                  temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate a structured response (for tool calling) from the LLM.

        Args:
            prompt (str): User prompt/query
            output_schema (dict): JSON schema for the structured output
            system_prompt (str, optional): System prompt to guide the model
            temperature (float): Sampling temperature (0.0 to 1.0)

        Returns:
            dict: Structured response for tool execution
        """
        logger.info(f"Generating structured output for prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

        # Add instructions to the prompt to return structured output
        structured_prompt = f"{prompt}\n\nRespond with a JSON object that matches the following schema: {json.dumps(output_schema)}"

        try:
            # Use a lower temperature for structured outputs to improve reliability
            adjusted_temp = min(temperature, 0.5)

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": self._format_messages(structured_prompt, system_prompt),
                "format": output_schema,  # Use the schema for formatting
                "options": {
                    "temperature": adjusted_temp,
                },
                "stream": False,
                "keep_alive": self.keep_alive
            }

            # Make request to Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout
            )
            response.raise_for_status()

            result = response.json()
            content = result.get("message", {}).get("content", "")

            # Parse the JSON response
            try:
                structured_output = json.loads(content)
                return structured_output
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {content}")
                return {"action": "none", "parameters": {}, "error": "Failed to parse response"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            return {"action": "none", "parameters": {}, "error": str(e)}

    def chat(self,
             messages: MessageList,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None,
             stream: bool = False) -> Union[str, Dict[str, Any], Generator[str, None, None]]:
        """
        Generate a response based on a conversation history.

        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            temperature (float): Sampling temperature (0.0 to 1.0)
            max_tokens (int, optional): Maximum number of tokens to generate
            stream (bool): Whether to stream the response

        Returns:
            str or dict: Generated response text or full response object
        """
        logger.info(f"Generating chat response for {len(messages)} messages")

        try:
            start_time = time.time()

            # Prepare request payload
            payload = {
                "model": self.model_name,
                "messages": messages,
                "stream": stream,
                "options": {
                    "temperature": temperature,
                },
                "keep_alive": self.keep_alive
            }

            if max_tokens is not None:
                payload["options"]["num_predict"] = max_tokens

            # Make request to Ollama API
            response = requests.post(
                f"{self.host}/api/chat",
                json=payload,
                timeout=self.timeout,
                stream=stream
            )
            response.raise_for_status()

            if stream:
                # Handle streaming response
                full_response = ""
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        full_response += content
                        yield content  # Yield each chunk for streaming
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                content = result.get("message", {}).get("content", "")

                end_time = time.time()
                logger.info(f"Chat response generated in {end_time - start_time:.2f} seconds")

                return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            raise
