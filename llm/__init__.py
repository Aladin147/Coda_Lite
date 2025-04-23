"""
Language Model (LLM) module for Coda Lite.
Handles interaction with local LLMs via Ollama.
"""

from llm.ollama_llm import OllamaLLM
from llm.websocket_llm import WebSocketOllamaLLM

__all__ = ["OllamaLLM", "WebSocketOllamaLLM"]
