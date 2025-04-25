"""
Message deduplication for Coda's WebSocket implementation.

This module provides utilities for detecting and handling duplicate messages.
"""

import time
import hashlib
import logging
import threading
from typing import Dict, Any, Optional, Tuple

logger = logging.getLogger("coda.websocket.deduplication")

class MessageDeduplicator:
    """
    Message deduplicator for WebSocket messages.
    
    This class provides methods to detect and handle duplicate messages
    based on content hashing and time-based expiration.
    """
    
    def __init__(self, expiration_seconds: float = 5.0, max_cache_size: int = 1000):
        """
        Initialize the message deduplicator.
        
        Args:
            expiration_seconds: Time in seconds after which a message is no longer considered a duplicate
            max_cache_size: Maximum number of messages to keep in the cache
        """
        self._messages: Dict[str, Tuple[float, int]] = {}  # hash -> (timestamp, count)
        self._lock = threading.RLock()
        self._expiration_seconds = expiration_seconds
        self._max_cache_size = max_cache_size
        
    def is_duplicate(self, message_type: str, message_data: Any) -> Tuple[bool, int]:
        """
        Check if a message is a duplicate.
        
        Args:
            message_type: The message type
            message_data: The message data
            
        Returns:
            A tuple of (is_duplicate, duplicate_count)
        """
        # Generate a hash of the message
        message_hash = self._generate_hash(message_type, message_data)
        
        with self._lock:
            current_time = time.time()
            
            # Clean up expired messages
            self._cleanup_expired(current_time)
            
            # Check if the message is a duplicate
            if message_hash in self._messages:
                timestamp, count = self._messages[message_hash]
                
                # Check if the message has expired
                if current_time - timestamp < self._expiration_seconds:
                    # Update the count and timestamp
                    self._messages[message_hash] = (current_time, count + 1)
                    logger.warning(f"Duplicate message detected: {message_type} (count: {count + 1})")
                    return True, count + 1
            
            # Not a duplicate or expired, add to cache
            self._messages[message_hash] = (current_time, 1)
            
            # Ensure cache doesn't grow too large
            if len(self._messages) > self._max_cache_size:
                self._trim_cache()
                
            return False, 1
    
    def _generate_hash(self, message_type: str, message_data: Any) -> str:
        """
        Generate a hash for a message.
        
        Args:
            message_type: The message type
            message_data: The message data
            
        Returns:
            A hash string
        """
        # Convert the message to a string
        message_str = f"{message_type}:{str(message_data)}"
        
        # Generate a hash
        return hashlib.md5(message_str.encode()).hexdigest()
    
    def _cleanup_expired(self, current_time: Optional[float] = None) -> None:
        """
        Clean up expired messages.
        
        Args:
            current_time: The current time (default: time.time())
        """
        if current_time is None:
            current_time = time.time()
            
        # Remove expired messages
        expired_hashes = [
            h for h, (timestamp, _) in self._messages.items()
            if current_time - timestamp >= self._expiration_seconds
        ]
        
        for h in expired_hashes:
            del self._messages[h]
            
        if expired_hashes:
            logger.debug(f"Cleaned up {len(expired_hashes)} expired messages")
    
    def _trim_cache(self) -> None:
        """Trim the cache to the maximum size."""
        # Sort messages by timestamp (oldest first)
        sorted_messages = sorted(
            self._messages.items(),
            key=lambda x: x[1][0]
        )
        
        # Keep only the newest messages
        to_keep = sorted_messages[-self._max_cache_size:]
        
        # Update the cache
        self._messages = dict(to_keep)
        
        logger.debug(f"Trimmed message cache to {len(self._messages)} entries")
    
    def clear(self) -> None:
        """Clear the message cache."""
        with self._lock:
            self._messages.clear()
            logger.debug("Cleared message cache")

# Global message deduplicator instance
_message_deduplicator = MessageDeduplicator()

def get_message_deduplicator() -> MessageDeduplicator:
    """
    Get the global message deduplicator instance.
    
    Returns:
        The global message deduplicator instance
    """
    return _message_deduplicator

def is_duplicate_message(message_type: str, message_data: Any) -> Tuple[bool, int]:
    """
    Check if a message is a duplicate.
    
    Args:
        message_type: The message type
        message_data: The message data
        
    Returns:
        A tuple of (is_duplicate, duplicate_count)
    """
    return _message_deduplicator.is_duplicate(message_type, message_data)
