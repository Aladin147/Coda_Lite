"""
Authentication for Coda's WebSocket server.

This module provides utilities for authenticating WebSocket connections.
"""

import time
import hmac
import hashlib
import logging
import secrets
import threading
from typing import Dict, Optional, Tuple

logger = logging.getLogger("coda.websocket.auth")

class WebSocketAuthenticator:
    """
    Authenticator for WebSocket connections.
    
    This class provides methods to generate and validate authentication tokens
    for WebSocket connections.
    """
    
    def __init__(self, secret_key: Optional[str] = None, token_expiration_seconds: int = 3600):
        """
        Initialize the authenticator.
        
        Args:
            secret_key: The secret key to use for token generation (default: random)
            token_expiration_seconds: Time in seconds after which a token expires
        """
        self._secret_key = secret_key or secrets.token_hex(32)
        self._token_expiration_seconds = token_expiration_seconds
        self._tokens: Dict[str, Tuple[float, str]] = {}  # token -> (expiration_time, client_id)
        self._lock = threading.RLock()
        
        logger.info("WebSocket authenticator initialized")
        
    def generate_token(self, client_id: str) -> str:
        """
        Generate an authentication token.
        
        Args:
            client_id: The client ID
            
        Returns:
            An authentication token
        """
        with self._lock:
            # Generate a timestamp
            timestamp = int(time.time())
            expiration = timestamp + self._token_expiration_seconds
            
            # Generate a nonce
            nonce = secrets.token_hex(8)
            
            # Generate the token data
            token_data = f"{client_id}:{timestamp}:{nonce}"
            
            # Generate the signature
            signature = hmac.new(
                self._secret_key.encode(),
                token_data.encode(),
                hashlib.sha256
            ).hexdigest()
            
            # Combine into a token
            token = f"{token_data}:{signature}"
            
            # Store the token
            self._tokens[token] = (expiration, client_id)
            
            # Clean up expired tokens
            self._cleanup_expired_tokens()
            
            logger.debug(f"Generated token for client {client_id}")
            return token
    
    def validate_token(self, token: str) -> Tuple[bool, Optional[str]]:
        """
        Validate an authentication token.
        
        Args:
            token: The token to validate
            
        Returns:
            A tuple of (is_valid, client_id)
        """
        with self._lock:
            # Check if the token is in our cache
            if token in self._tokens:
                expiration, client_id = self._tokens[token]
                
                # Check if the token has expired
                if time.time() < expiration:
                    logger.debug(f"Validated token for client {client_id}")
                    return True, client_id
                
                # Token has expired, remove it
                del self._tokens[token]
                logger.warning(f"Expired token for client {client_id}")
                return False, None
            
            # Token not in cache, validate it manually
            try:
                # Split the token
                token_parts = token.split(":")
                if len(token_parts) != 4:
                    logger.warning("Invalid token format")
                    return False, None
                
                client_id, timestamp_str, nonce, signature = token_parts
                
                # Check if the token has expired
                timestamp = int(timestamp_str)
                if time.time() - timestamp > self._token_expiration_seconds:
                    logger.warning(f"Expired token for client {client_id}")
                    return False, None
                
                # Validate the signature
                token_data = f"{client_id}:{timestamp_str}:{nonce}"
                expected_signature = hmac.new(
                    self._secret_key.encode(),
                    token_data.encode(),
                    hashlib.sha256
                ).hexdigest()
                
                if signature != expected_signature:
                    logger.warning(f"Invalid signature for client {client_id}")
                    return False, None
                
                # Token is valid, add to cache
                expiration = timestamp + self._token_expiration_seconds
                self._tokens[token] = (expiration, client_id)
                
                logger.debug(f"Validated token for client {client_id}")
                return True, client_id
            except Exception as e:
                logger.error(f"Error validating token: {e}")
                return False, None
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke an authentication token.
        
        Args:
            token: The token to revoke
            
        Returns:
            True if the token was revoked, False otherwise
        """
        with self._lock:
            if token in self._tokens:
                del self._tokens[token]
                logger.debug("Revoked token")
                return True
            
            logger.warning("Token not found for revocation")
            return False
    
    def _cleanup_expired_tokens(self) -> None:
        """Clean up expired tokens."""
        current_time = time.time()
        expired_tokens = [
            token for token, (expiration, _) in self._tokens.items()
            if current_time > expiration
        ]
        
        for token in expired_tokens:
            del self._tokens[token]
            
        if expired_tokens:
            logger.debug(f"Cleaned up {len(expired_tokens)} expired tokens")

# Global authenticator instance
_authenticator = WebSocketAuthenticator()

def get_authenticator() -> WebSocketAuthenticator:
    """
    Get the global authenticator instance.
    
    Returns:
        The global authenticator instance
    """
    return _authenticator

def generate_token(client_id: str) -> str:
    """
    Generate an authentication token.
    
    Args:
        client_id: The client ID
        
    Returns:
        An authentication token
    """
    return _authenticator.generate_token(client_id)

def validate_token(token: str) -> Tuple[bool, Optional[str]]:
    """
    Validate an authentication token.
    
    Args:
        token: The token to validate
        
    Returns:
        A tuple of (is_valid, client_id)
    """
    return _authenticator.validate_token(token)

def revoke_token(token: str) -> bool:
    """
    Revoke an authentication token.
    
    Args:
        token: The token to revoke
        
    Returns:
        True if the token was revoked, False otherwise
    """
    return _authenticator.revoke_token(token)
