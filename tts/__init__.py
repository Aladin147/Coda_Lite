"""
Text-to-Speech (TTS) module for Coda Lite.
Provides a common interface for different TTS implementations.
"""

from tts.speak import BaseTTS

# Disable CSM TTS to avoid MeCab dependency issues
CSM_AVAILABLE = False

# Disable Dia TTS for now
DIA_AVAILABLE = False

# Import ElevenLabs TTS
try:
    from tts.elevenlabs_tts import ElevenLabsTTS
    from tts.websocket_elevenlabs_tts import WebSocketElevenLabsTTS
    ELEVENLABS_AVAILABLE = True
except ImportError as e:
    print(f"Error importing ElevenLabsTTS: {e}")
    ELEVENLABS_AVAILABLE = False

# Factory function to create TTS instances
def create_tts(engine="csm", **kwargs):
    """
    Create a TTS instance based on the specified engine.

    Args:
        engine (str): TTS engine to use ("csm", "dia", or "elevenlabs")
        **kwargs: Additional parameters to pass to the TTS constructor

    Returns:
        BaseTTS: TTS instance

    Raises:
        NotImplementedError: If the specified engine is not supported
    """
    if engine == "csm":
        if CSM_AVAILABLE:
            return CSMTTS(**kwargs)
        else:
            raise ImportError("CSM TTS is not available. Please install melotts package.")
    elif engine == "dia":
        if DIA_AVAILABLE:
            return DiaTTS(**kwargs)
        else:
            raise ImportError("Dia TTS is not available. Please install dia package.")
    elif engine == "elevenlabs":
        if ELEVENLABS_AVAILABLE:
            return ElevenLabsTTS(**kwargs)
        else:
            raise ImportError("ElevenLabs TTS is not available. Please install elevenlabs package.")
    else:
        raise NotImplementedError(f"Unknown TTS engine: {engine}. Currently supported engines: 'csm', 'dia', 'elevenlabs'")

__all__ = ["BaseTTS", "create_tts", "ElevenLabsTTS", "WebSocketElevenLabsTTS"]
