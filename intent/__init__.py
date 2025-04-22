"""
Intent module for Coda Lite.

This module provides intent detection and routing capabilities for Coda Lite, including:
- Lightweight intent detection based on pattern matching
- Intent routing to appropriate handlers
- Entity extraction from user input
- System command processing
"""

from .intent_router import IntentRouter, IntentType
from .handlers import IntentHandlers
from .manager import IntentManager

__all__ = ["IntentRouter", "IntentType", "IntentHandlers", "IntentManager"]
