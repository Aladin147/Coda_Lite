"""
TTS Factory module for Coda Lite.

This module provides a factory function for creating TTS instances with lazy loading.
Only the requested TTS implementation is imported and instantiated.
"""

import gc
import logging
from typing import Dict, Any, Optional

# Set up logging
logger = logging.getLogger("coda.tts.factory")

# Base TTS class (imported directly to avoid circular imports)
from tts.speak import BaseTTS

# Global TTS instance cache
_tts_instance = None
_current_tts_type = None


def get_tts_instance(
    tts_type: str,
    websocket_integration=None,
    config: Optional[Dict[str, Any]] = None,
    **kwargs
) -> BaseTTS:
    """
    Get a TTS instance of the specified type with lazy loading.

    This function will:
    1. Only import the requested TTS implementation
    2. Create a new instance if needed
    3. Clean up any previous instance if the type changes

    Args:
        tts_type: Type of TTS to create ("elevenlabs", "csm", "dia", etc.)
        websocket_integration: WebSocket integration instance (if available)
        config: Configuration dictionary
        **kwargs: Additional parameters to pass to the TTS constructor

    Returns:
        BaseTTS: TTS instance

    Raises:
        ImportError: If the requested TTS implementation is not available
        ValueError: If the TTS type is not supported
    """
    global _tts_instance, _current_tts_type

    # If we already have an instance of the requested type, return it
    if _tts_instance is not None and _current_tts_type == tts_type:
        logger.debug(f"Returning existing {tts_type} TTS instance")
        return _tts_instance

    # Clean up any existing instance
    if _tts_instance is not None:
        logger.info(f"Cleaning up existing {_current_tts_type} TTS instance")
        try:
            # Log memory usage before cleanup
            try:
                import psutil
                process = psutil.Process()
                memory_before = process.memory_info().rss / (1024 * 1024)
                logger.info(f"Memory usage before TTS cleanup: {memory_before:.2f} MB")
            except ImportError:
                memory_before = None

            # Call unload if available
            if hasattr(_tts_instance, "unload"):
                _tts_instance.unload()

            # Delete the instance
            del _tts_instance

            # Force garbage collection
            gc.collect()

            # Log memory usage after cleanup
            try:
                if memory_before is not None:
                    memory_after = process.memory_info().rss / (1024 * 1024)
                    memory_freed = memory_before - memory_after
                    logger.info(f"Memory usage after TTS cleanup: {memory_after:.2f} MB (freed {memory_freed:.2f} MB)")
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Error cleaning up TTS instance: {e}")

    # Reset instance variables
    _tts_instance = None
    _current_tts_type = None

    # Create a new instance based on the requested type
    if tts_type == "elevenlabs":
        try:
            # Only import ElevenLabs TTS when needed
            if websocket_integration:
                from tts.websocket_elevenlabs_tts import WebSocketElevenLabsTTS

                # Extract ElevenLabs-specific parameters from config
                api_key = config.get("tts.elevenlabs_api_key", "sk_7b576d29574b14a97150b864497d937c4e1fdd2d6b3a1e4d") if config else kwargs.get("api_key")
                voice_id = config.get("tts.elevenlabs_voice_id", "21m00Tcm4TlvDq8ikWAM") if config else kwargs.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
                model_id = config.get("tts.elevenlabs_model_id", "eleven_multilingual_v2") if config else kwargs.get("model_id", "eleven_multilingual_v2")

                logger.info(f"Creating WebSocketElevenLabsTTS instance with voice_id={voice_id}")
                _tts_instance = WebSocketElevenLabsTTS(
                    websocket_integration=websocket_integration,
                    api_key=api_key,
                    voice_id=voice_id,
                    model_id=model_id,
                    **kwargs
                )
            else:
                from tts.elevenlabs_tts import ElevenLabsTTS

                # Extract ElevenLabs-specific parameters from config
                api_key = config.get("tts.elevenlabs_api_key", "sk_7b576d29574b14a97150b864497d937c4e1fdd2d6b3a1e4d") if config else kwargs.get("api_key")
                voice_id = config.get("tts.elevenlabs_voice_id", "21m00Tcm4TlvDq8ikWAM") if config else kwargs.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
                model_id = config.get("tts.elevenlabs_model_id", "eleven_multilingual_v2") if config else kwargs.get("model_id", "eleven_multilingual_v2")

                logger.info(f"Creating ElevenLabsTTS instance with voice_id={voice_id}")
                _tts_instance = ElevenLabsTTS(
                    api_key=api_key,
                    voice_id=voice_id,
                    model_id=model_id,
                    **kwargs
                )

            _current_tts_type = "elevenlabs"
        except ImportError as e:
            logger.error(f"Error importing ElevenLabs TTS: {e}")
            raise ImportError(f"ElevenLabs TTS is not available: {e}")

    elif tts_type in ["csm", "dia"]:
        # CSM and Dia TTS are disabled until better versions are available
        logger.warning(f"{tts_type.upper()} TTS is currently disabled. Falling back to ElevenLabs TTS.")

        # Recursively call this function with ElevenLabs TTS
        return get_tts_instance("elevenlabs", websocket_integration, config, **kwargs)

    else:
        logger.warning(f"Unsupported TTS type: {tts_type}. Falling back to ElevenLabs TTS.")
        return get_tts_instance("elevenlabs", websocket_integration, config, **kwargs)

    return _tts_instance


def get_available_tts_engines() -> Dict[str, bool]:
    """
    Get a dictionary of available TTS engines.

    Currently, we're focusing exclusively on ElevenLabs TTS.
    Other engines (CSM, Dia) are disabled until better versions are available.

    Returns:
        Dict[str, bool]: Dictionary of TTS engine names and their availability
    """
    engines = {
        "elevenlabs": False,
        "csm": False,  # Disabled
        "dia": False   # Disabled
    }

    # Check ElevenLabs availability
    try:
        import importlib.util
        if importlib.util.find_spec("elevenlabs") is not None:
            engines["elevenlabs"] = True
    except ImportError:
        pass

    # Other engines are intentionally disabled
    # We're focusing exclusively on ElevenLabs TTS

    return engines


def unload_current_tts() -> None:
    """
    Unload the current TTS instance.

    This function cleans up the current TTS instance to free resources.
    """
    global _tts_instance, _current_tts_type

    if _tts_instance is not None:
        logger.info(f"Unloading {_current_tts_type} TTS instance")
        try:
            # Log memory usage before unload
            try:
                import psutil
                process = psutil.Process()
                memory_before = process.memory_info().rss / (1024 * 1024)
                logger.info(f"Memory usage before TTS unload: {memory_before:.2f} MB")
            except ImportError:
                memory_before = None

            # Call unload if available
            if hasattr(_tts_instance, "unload"):
                _tts_instance.unload()

            # Delete the instance
            del _tts_instance

            # Force garbage collection
            gc.collect()

            # Log memory usage after unload
            try:
                if memory_before is not None:
                    memory_after = process.memory_info().rss / (1024 * 1024)
                    memory_freed = memory_before - memory_after
                    logger.info(f"Memory usage after TTS unload: {memory_after:.2f} MB (freed {memory_freed:.2f} MB)")
            except Exception:
                pass

        except Exception as e:
            logger.warning(f"Error unloading TTS instance: {e}")

    # Reset instance variables
    _tts_instance = None
    _current_tts_type = None
