"""
Text-to-Speech (TTS) module for Coda Lite.
Provides a common interface for different TTS implementations.
"""

from tts.speak import BaseTTS

# Import CSM TTS (MeloTTS)
try:
    from tts.csm_tts import CSMTTS
    CSM_AVAILABLE = True
except ImportError:
    CSM_AVAILABLE = False

# Import Dia TTS
try:
    from tts.dia_tts import DiaTTS
    DIA_AVAILABLE = True
except ImportError:
    DIA_AVAILABLE = False

# Factory function to create TTS instances
def create_tts(engine="csm", **kwargs):
    """
    Create a TTS instance based on the specified engine.

    Args:
        engine (str): TTS engine to use ("csm" or "dia")
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
    else:
        raise NotImplementedError(f"Unknown TTS engine: {engine}. Currently supported engines: 'csm', 'dia'")

__all__ = ["BaseTTS", "create_tts", "CSMTTS", "DiaTTS"]
