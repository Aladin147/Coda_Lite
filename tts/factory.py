"""
TTS Factory module for Coda Lite.

This module provides a factory function for creating TTS instances with lazy loading.
Only the requested TTS implementation is imported and instantiated.
"""

import gc
import logging
from typing import Dict, Any, Optional, Type

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
            # Call unload if available
            if hasattr(_tts_instance, "unload"):
                _tts_instance.unload()
            
            # Delete the instance
            del _tts_instance
            
            # Force garbage collection
            gc.collect()
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
                api_key = config.get("tts.elevenlabs_api_key") if config else kwargs.get("api_key")
                voice_id = config.get("tts.elevenlabs_voice_id") if config else kwargs.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
                model_id = config.get("tts.elevenlabs_model") if config else kwargs.get("model_id", "eleven_multilingual_v2")
                
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
                api_key = config.get("tts.elevenlabs_api_key") if config else kwargs.get("api_key")
                voice_id = config.get("tts.elevenlabs_voice_id") if config else kwargs.get("voice_id", "21m00Tcm4TlvDq8ikWAM")
                model_id = config.get("tts.elevenlabs_model") if config else kwargs.get("model_id", "eleven_multilingual_v2")
                
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
    
    elif tts_type == "csm":
        try:
            # Only import CSM TTS when needed
            if websocket_integration:
                # WebSocket CSM TTS not implemented yet, fall back to regular CSM TTS
                logger.warning("WebSocket CSM TTS not implemented yet, falling back to regular CSM TTS")
                from tts.csm_tts import CSMTTS
                
                # Extract CSM-specific parameters from config
                language = config.get("tts.language") if config else kwargs.get("language", "EN")
                voice = config.get("tts.voice") if config else kwargs.get("voice", "EN-US")
                device = config.get("tts.device") if config else kwargs.get("device", "cuda")
                
                logger.info(f"Creating CSMTTS instance with language={language}, voice={voice}")
                _tts_instance = CSMTTS(
                    language=language,
                    voice=voice,
                    device=device,
                    **kwargs
                )
            else:
                from tts.csm_tts import CSMTTS
                
                # Extract CSM-specific parameters from config
                language = config.get("tts.language") if config else kwargs.get("language", "EN")
                voice = config.get("tts.voice") if config else kwargs.get("voice", "EN-US")
                device = config.get("tts.device") if config else kwargs.get("device", "cuda")
                
                logger.info(f"Creating CSMTTS instance with language={language}, voice={voice}")
                _tts_instance = CSMTTS(
                    language=language,
                    voice=voice,
                    device=device,
                    **kwargs
                )
            
            _current_tts_type = "csm"
        except ImportError as e:
            logger.error(f"Error importing CSM TTS: {e}")
            raise ImportError(f"CSM TTS is not available: {e}")
    
    elif tts_type == "dia":
        try:
            # Only import Dia TTS when needed
            if websocket_integration:
                # WebSocket Dia TTS not implemented yet, fall back to regular Dia TTS
                logger.warning("WebSocket Dia TTS not implemented yet, falling back to regular Dia TTS")
                from tts.dia_tts import DiaTTS
                
                # Extract Dia-specific parameters from config
                model_path = config.get("tts.dia_model_path") if config else kwargs.get("model_path")
                device = config.get("tts.device") if config else kwargs.get("device", "cuda")
                
                logger.info(f"Creating DiaTTS instance with device={device}")
                _tts_instance = DiaTTS(
                    model_path=model_path,
                    device=device,
                    **kwargs
                )
            else:
                from tts.dia_tts import DiaTTS
                
                # Extract Dia-specific parameters from config
                model_path = config.get("tts.dia_model_path") if config else kwargs.get("model_path")
                device = config.get("tts.device") if config else kwargs.get("device", "cuda")
                
                logger.info(f"Creating DiaTTS instance with device={device}")
                _tts_instance = DiaTTS(
                    model_path=model_path,
                    device=device,
                    **kwargs
                )
            
            _current_tts_type = "dia"
        except ImportError as e:
            logger.error(f"Error importing Dia TTS: {e}")
            raise ImportError(f"Dia TTS is not available: {e}")
    
    else:
        raise ValueError(f"Unsupported TTS type: {tts_type}")
    
    return _tts_instance


def get_available_tts_engines() -> Dict[str, bool]:
    """
    Get a dictionary of available TTS engines.
    
    This function checks which TTS engines are available without loading them.
    It only imports the minimum necessary to check availability.
    
    Returns:
        Dict[str, bool]: Dictionary of TTS engine names and their availability
    """
    engines = {
        "elevenlabs": False,
        "csm": False,
        "dia": False
    }
    
    # Check ElevenLabs availability
    try:
        import importlib.util
        if importlib.util.find_spec("elevenlabs") is not None:
            engines["elevenlabs"] = True
    except ImportError:
        pass
    
    # Check CSM availability
    try:
        import importlib.util
        if importlib.util.find_spec("melotts") is not None:
            engines["csm"] = True
    except ImportError:
        pass
    
    # Check Dia availability
    try:
        import importlib.util
        if importlib.util.find_spec("dia") is not None:
            engines["dia"] = True
    except ImportError:
        pass
    
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
            # Call unload if available
            if hasattr(_tts_instance, "unload"):
                _tts_instance.unload()
            
            # Delete the instance
            del _tts_instance
            
            # Force garbage collection
            gc.collect()
        except Exception as e:
            logger.warning(f"Error unloading TTS instance: {e}")
    
    # Reset instance variables
    _tts_instance = None
    _current_tts_type = None
