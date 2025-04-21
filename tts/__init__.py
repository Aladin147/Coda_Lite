"""
Text-to-Speech (TTS) module for Coda Lite.
Provides a common interface for different TTS implementations.
"""

from tts.speak import BaseTTS, create_tts
from tts.coqui_tts import CoquiTTS

# For backward compatibility
from tts.coqui_tts import CoquiTTS as CSMTTS

__all__ = ["BaseTTS", "CoquiTTS", "CSMTTS", "create_tts"]
