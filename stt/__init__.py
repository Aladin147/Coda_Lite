"""
Speech-to-Text (STT) module for Coda Lite.
Uses faster-whisper for local speech recognition.
"""

from stt.whisper_stt import WhisperSTT
from stt.websocket_stt import WebSocketWhisperSTT

__all__ = ["WhisperSTT", "WebSocketWhisperSTT"]
