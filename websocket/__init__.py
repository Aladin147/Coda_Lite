"""
WebSocket package for Coda.

This package provides WebSocket functionality for Coda, allowing clients to
connect and receive real-time events about Coda's operation.
"""

from .server_fixed import CodaWebSocketServer
from .events import (
    EventType,
    BaseEvent,
    create_event,
    validate_event,
)
from .integration_fixed import CodaWebSocketIntegration, PerfTracker

__all__ = [
    "CodaWebSocketServer",
    "EventType",
    "BaseEvent",
    "create_event",
    "validate_event",
    "CodaWebSocketIntegration",
    "PerfTracker",
]
