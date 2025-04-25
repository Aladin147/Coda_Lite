#!/usr/bin/env python3
"""
Test script for the WebSocket authentication system.

This script tests the authentication implementation.
"""

import logging
import sys
import time
import unittest
from pathlib import Path

# Add the parent directory to the path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from websocket.authentication import (
    WebSocketAuthenticator,
    get_authenticator,
    generate_token,
    validate_token,
    revoke_token
)

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("test_authentication")


class TestAuthentication(unittest.TestCase):
    """Test cases for the authentication system."""

    def test_generate_token(self):
        """Test generating an authentication token."""
        # Generate a token
        token = generate_token("test_client")

        # Check that it's a valid token
        self.assertIsInstance(token, str)
        self.assertTrue(len(token) > 0)

        # Check that it contains the client ID
        self.assertIn("test_client", token)

    def test_validate_token(self):
        """Test validating an authentication token."""
        # Generate a token
        token = generate_token("test_client")

        # Validate the token
        is_valid, client_id = validate_token(token)

        # Check that it's valid
        self.assertTrue(is_valid)
        self.assertEqual(client_id, "test_client")

        # Validate an invalid token
        is_valid, client_id = validate_token("invalid_token")

        # Check that it's invalid
        self.assertFalse(is_valid)
        self.assertIsNone(client_id)

    def test_revoke_token(self):
        """Test revoking an authentication token."""
        # Create a custom authenticator for this test
        authenticator = WebSocketAuthenticator()

        # Generate a token
        token = authenticator.generate_token("test_client")

        # Validate the token
        is_valid, client_id = authenticator.validate_token(token)

        # Check that it's valid
        self.assertTrue(is_valid)

        # Revoke the token
        result = authenticator.revoke_token(token)

        # Check that it was revoked
        self.assertTrue(result)

        # Validate the token again
        is_valid, client_id = authenticator.validate_token(token)

        # Check that it's invalid
        self.assertFalse(is_valid)
        self.assertIsNone(client_id)

        # Try to revoke an invalid token
        result = authenticator.revoke_token("invalid_token")

        # Check that it wasn't revoked
        self.assertFalse(result)

    def test_token_expiration(self):
        """Test token expiration."""
        # Create an authenticator with a short expiration time
        authenticator = WebSocketAuthenticator(token_expiration_seconds=1)

        # Generate a token
        token = authenticator.generate_token("test_client")

        # Validate the token
        is_valid, client_id = authenticator.validate_token(token)

        # Check that it's valid
        self.assertTrue(is_valid)
        self.assertEqual(client_id, "test_client")

        # Wait for the token to expire
        time.sleep(1.1)

        # Validate the token again
        is_valid, client_id = authenticator.validate_token(token)

        # Check that it's invalid
        self.assertFalse(is_valid)
        self.assertIsNone(client_id)

    def test_get_authenticator(self):
        """Test the get_authenticator function."""
        # Get the authenticator
        authenticator = get_authenticator()

        # Check that it's a valid authenticator
        self.assertIsInstance(authenticator, WebSocketAuthenticator)

        # Get it again
        authenticator2 = get_authenticator()

        # Check that it's the same instance
        self.assertIs(authenticator, authenticator2)

    def test_multiple_tokens(self):
        """Test generating and validating multiple tokens."""
        # Create a custom authenticator for this test
        authenticator = WebSocketAuthenticator()

        # Generate tokens for different clients
        token1 = authenticator.generate_token("client1")
        token2 = authenticator.generate_token("client2")
        token3 = authenticator.generate_token("client3")

        # Validate the tokens
        is_valid1, client_id1 = authenticator.validate_token(token1)
        is_valid2, client_id2 = authenticator.validate_token(token2)
        is_valid3, client_id3 = authenticator.validate_token(token3)

        # Check that they're all valid
        self.assertTrue(is_valid1)
        self.assertEqual(client_id1, "client1")

        self.assertTrue(is_valid2)
        self.assertEqual(client_id2, "client2")

        self.assertTrue(is_valid3)
        self.assertEqual(client_id3, "client3")

        # Revoke one token
        result = authenticator.revoke_token(token2)

        # Check that it was revoked
        self.assertTrue(result)

        # Validate the tokens again
        is_valid1, client_id1 = authenticator.validate_token(token1)
        is_valid2, client_id2 = authenticator.validate_token(token2)
        is_valid3, client_id3 = authenticator.validate_token(token3)

        # Check that token1 and token3 are still valid
        self.assertTrue(is_valid1)
        self.assertEqual(client_id1, "client1")

        self.assertTrue(is_valid3)
        self.assertEqual(client_id3, "client3")

        # Check that token2 is invalid
        self.assertFalse(is_valid2)
        self.assertIsNone(client_id2)


if __name__ == "__main__":
    unittest.main()
