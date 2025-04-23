"""
WebSocket-integrated LLM implementation for Coda Lite.
Extends OllamaLLM to emit events via WebSocket.
"""

import json
import time
import logging
from typing import Dict, List, Optional, Union, Any, Generator

import requests

from llm.ollama_llm import OllamaLLM
from websocket.integration import CodaWebSocketIntegration

logger = logging.getLogger("coda.llm.websocket")

# Define message types for type hints
Message = Dict[str, str]
MessageList = List[Message]

class WebSocketOllamaLLM(OllamaLLM):
    """LLM implementation using Ollama with WebSocket integration."""

    def __init__(self,
                 websocket_integration: CodaWebSocketIntegration,
                 model_name: str = "llama3",
                 host: str = "http://localhost:11434",
                 timeout: int = 120,
                 keep_alive: str = "5m"):
        """
        Initialize the WebSocketOllamaLLM module.

        Args:
            websocket_integration: The WebSocket integration instance
            model_name (str): Name of the Ollama model to use.
                Default: "llama3"
            host (str): Host URL for Ollama API.
                Default: "http://localhost:11434"
            timeout (int): Request timeout in seconds.
                Default: 120
            keep_alive (str): Duration to keep model loaded in memory.
                Default: "5m"
        """
        super().__init__(
            model_name=model_name,
            host=host,
            timeout=timeout,
            keep_alive=keep_alive
        )
        
        self.ws = websocket_integration
        logger.info("WebSocketOllamaLLM initialized with WebSocket integration")

    def generate_response(self,
                         prompt: str,
                         system_prompt: Optional[str] = None,
                         temperature: float = 0.7,
                         max_tokens: Optional[int] = None,
                         stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        Generate a response from the LLM with WebSocket events.

        Args:
            prompt (str): User prompt/query
            system_prompt (str, optional): System prompt to guide the model
            temperature (float): Sampling temperature (0.0 to 1.0)
            max_tokens (int, optional): Maximum number of tokens to generate
            stream (bool): Whether to stream the response

        Returns:
            str or Generator: Generated response or stream of response chunks
        """
        logger.info(f"Generating response for prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

        messages = self._format_messages(prompt, system_prompt)
        
        # Estimate prompt tokens (rough approximation)
        prompt_tokens = sum(len(msg["content"]) for msg in messages) // 4
        
        # Signal start of LLM processing
        self.ws.llm_start(
            model=self.model_name,
            prompt_tokens=prompt_tokens,
            system_prompt_preview=system_prompt[:100] + "..." if system_prompt and len(system_prompt) > 100 else system_prompt
        )

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
                token_index = 0
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        
                        if content:
                            # Send token event
                            self.ws.llm_token(content, token_index)
                            token_index += 1
                            
                            full_response += content
                            yield content  # Yield each chunk for streaming
                
                # Send LLM result event
                self.ws.llm_result(
                    text=full_response,
                    total_tokens=token_index + prompt_tokens,
                    has_tool_calls=False
                )
                
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                content = result.get("message", {}).get("content", "")

                end_time = time.time()
                logger.info(f"Response generated in {end_time - start_time:.2f} seconds")
                
                # Send LLM result event
                self.ws.llm_result(
                    text=content,
                    total_tokens=prompt_tokens + (len(content) // 4),  # Rough approximation
                    has_tool_calls=False
                )

                return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            
            # Send LLM error event
            self.ws.llm_error(str(e))
            
            raise

    def generate_structured_output(self,
                                  prompt: str,
                                  output_schema: Dict[str, Any],
                                  system_prompt: Optional[str] = None,
                                  temperature: float = 0.7) -> Dict[str, Any]:
        """
        Generate a structured response (for tool calling) from the LLM with WebSocket events.

        Args:
            prompt (str): User prompt/query
            output_schema (dict): JSON schema for the structured output
            system_prompt (str, optional): System prompt to guide the model
            temperature (float): Sampling temperature (0.0 to 1.0)

        Returns:
            dict: Structured output according to the schema
        """
        logger.info(f"Generating structured output for prompt: {prompt[:50]}{'...' if len(prompt) > 50 else ''}")

        # Create a prompt that includes the schema
        schema_str = json.dumps(output_schema, indent=2)
        structured_prompt = f"{prompt}\n\nRespond with a JSON object that follows this schema:\n{schema_str}"
        
        # Estimate prompt tokens (rough approximation)
        prompt_tokens = (len(structured_prompt) + (len(system_prompt) if system_prompt else 0)) // 4
        
        # Signal start of LLM processing
        self.ws.llm_start(
            model=self.model_name,
            prompt_tokens=prompt_tokens,
            system_prompt_preview=system_prompt[:100] + "..." if system_prompt and len(system_prompt) > 100 else system_prompt
        )

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
                
                # Send LLM result event
                self.ws.llm_result(
                    text=content,
                    total_tokens=prompt_tokens + (len(content) // 4),  # Rough approximation
                    has_tool_calls=True
                )
                
                return structured_output
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON response: {content}")
                
                # Send LLM error event
                self.ws.llm_error(f"Failed to parse JSON response: {content[:100]}...")
                
                return {"action": "none", "parameters": {}, "error": "Failed to parse response"}

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            
            # Send LLM error event
            self.ws.llm_error(str(e))
            
            return {"action": "none", "parameters": {}, "error": str(e)}

    def chat(self,
             messages: MessageList,
             temperature: float = 0.7,
             max_tokens: Optional[int] = None,
             stream: bool = False) -> Union[str, Generator[str, None, None]]:
        """
        Generate a response based on a conversation history with WebSocket events.

        Args:
            messages (list): List of message dictionaries with 'role' and 'content'
            temperature (float): Sampling temperature (0.0 to 1.0)
            max_tokens (int, optional): Maximum number of tokens to generate
            stream (bool): Whether to stream the response

        Returns:
            str or Generator: Generated response or stream of response chunks
        """
        logger.info(f"Generating chat response for {len(messages)} messages")
        
        # Estimate prompt tokens (rough approximation)
        prompt_tokens = sum(len(msg["content"]) for msg in messages) // 4
        
        # Get system prompt for preview
        system_prompt = next((msg["content"] for msg in messages if msg["role"] == "system"), None)
        
        # Signal start of LLM processing
        self.ws.llm_start(
            model=self.model_name,
            prompt_tokens=prompt_tokens,
            system_prompt_preview=system_prompt[:100] + "..." if system_prompt and len(system_prompt) > 100 else system_prompt
        )

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
                token_index = 0
                
                for line in response.iter_lines():
                    if line:
                        chunk = json.loads(line)
                        content = chunk.get("message", {}).get("content", "")
                        
                        if content:
                            # Send token event
                            self.ws.llm_token(content, token_index)
                            token_index += 1
                            
                            full_response += content
                            yield content  # Yield each chunk for streaming
                
                # Send LLM result event
                self.ws.llm_result(
                    text=full_response,
                    total_tokens=token_index + prompt_tokens,
                    has_tool_calls="tool_call" in full_response.lower()
                )
                
                return full_response
            else:
                # Handle non-streaming response
                result = response.json()
                content = result.get("message", {}).get("content", "")

                end_time = time.time()
                logger.info(f"Response generated in {end_time - start_time:.2f} seconds")
                
                # Send LLM result event
                self.ws.llm_result(
                    text=content,
                    total_tokens=prompt_tokens + (len(content) // 4),  # Rough approximation
                    has_tool_calls="tool_call" in content.lower()
                )

                return content

        except requests.exceptions.RequestException as e:
            logger.error(f"Error calling Ollama API: {e}")
            
            # Send LLM error event
            self.ws.llm_error(str(e))
            
            raise
