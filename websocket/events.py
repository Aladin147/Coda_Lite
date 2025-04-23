"""
Event schema for Coda WebSocket server.

This module defines the schema for events sent over the WebSocket connection.
"""

import time
from enum import Enum
from typing import Dict, List, Any, Optional, Union
from pydantic import BaseModel, Field

class EventType(str, Enum):
    """Event types for Coda WebSocket events."""

    # System events
    SYSTEM_INFO = "system_info"
    SYSTEM_ERROR = "system_error"
    SYSTEM_METRICS = "system_metrics"

    # STT events
    STT_START = "stt_start"
    STT_INTERIM = "stt_interim"
    STT_RESULT = "stt_result"
    STT_ERROR = "stt_error"

    # LLM events
    LLM_START = "llm_start"
    LLM_TOKEN = "llm_token"
    LLM_RESULT = "llm_result"
    LLM_ERROR = "llm_error"

    # TTS events
    TTS_START = "tts_start"
    TTS_PROGRESS = "tts_progress"
    TTS_RESULT = "tts_result"
    TTS_ERROR = "tts_error"

    # Memory events
    MEMORY_STORE = "memory_store"
    MEMORY_RETRIEVE = "memory_retrieve"
    MEMORY_UPDATE = "memory_update"

    # Tool events
    TOOL_CALL = "tool_call"
    TOOL_RESULT = "tool_result"
    TOOL_ERROR = "tool_error"

    # Conversation events
    CONVERSATION_START = "conversation_start"
    CONVERSATION_TURN = "conversation_turn"
    CONVERSATION_END = "conversation_end"

    # Performance events
    LATENCY_TRACE = "latency_trace"
    COMPONENT_TIMING = "component_timing"
    COMPONENT_STATS = "component_stats"

    # Replay events
    REPLAY = "replay"

class BaseEvent(BaseModel):
    """Base model for all events."""

    version: str = "1.0"
    seq: int
    timestamp: float = Field(default_factory=time.time)
    type: EventType
    session_id: Optional[str] = None

class SystemInfoEvent(BaseEvent):
    """System information event."""

    type: EventType = EventType.SYSTEM_INFO
    data: Dict[str, Any] = Field(default_factory=dict)

class SystemErrorEvent(BaseEvent):
    """System error event."""

    type: EventType = EventType.SYSTEM_ERROR
    level: str  # "warning", "error", "critical"
    message: str
    details: Optional[Dict[str, Any]] = None

class SystemMetricsEvent(BaseEvent):
    """System metrics event."""

    type: EventType = EventType.SYSTEM_METRICS
    memory_mb: float
    cpu_percent: float
    gpu_vram_mb: Optional[float] = None
    uptime_seconds: float

class STTStartEvent(BaseEvent):
    """STT start event."""

    type: EventType = EventType.STT_START
    mode: str  # "push_to_talk", "continuous", "file"

class STTInterimEvent(BaseEvent):
    """STT interim result event."""

    type: EventType = EventType.STT_INTERIM
    text: str
    confidence: float

class STTResultEvent(BaseEvent):
    """STT final result event."""

    type: EventType = EventType.STT_RESULT
    text: str
    confidence: float
    duration_seconds: float
    language: Optional[str] = None

class STTErrorEvent(BaseEvent):
    """STT error event."""

    type: EventType = EventType.STT_ERROR
    message: str
    details: Optional[Dict[str, Any]] = None

class LLMStartEvent(BaseEvent):
    """LLM start event."""

    type: EventType = EventType.LLM_START
    model: str
    prompt_tokens: int
    system_prompt_preview: Optional[str] = None

class LLMTokenEvent(BaseEvent):
    """LLM token event."""

    type: EventType = EventType.LLM_TOKEN
    token: str
    token_index: int

class LLMResultEvent(BaseEvent):
    """LLM result event."""

    type: EventType = EventType.LLM_RESULT
    text: str
    total_tokens: int
    duration_seconds: float
    has_tool_calls: bool = False

class LLMErrorEvent(BaseEvent):
    """LLM error event."""

    type: EventType = EventType.LLM_ERROR
    message: str
    details: Optional[Dict[str, Any]] = None

class TTSStartEvent(BaseEvent):
    """TTS start event."""

    type: EventType = EventType.TTS_START
    text: str
    voice: str
    provider: str  # "elevenlabs", "dia", "csm1b", etc.

class TTSProgressEvent(BaseEvent):
    """TTS progress event."""

    type: EventType = EventType.TTS_PROGRESS
    percent_complete: float

class TTSResultEvent(BaseEvent):
    """TTS result event."""

    type: EventType = EventType.TTS_RESULT
    duration_seconds: float
    audio_duration_seconds: float
    char_count: int

class TTSErrorEvent(BaseEvent):
    """TTS error event."""

    type: EventType = EventType.TTS_ERROR
    message: str
    details: Optional[Dict[str, Any]] = None

class MemoryStoreEvent(BaseEvent):
    """Memory store event."""

    type: EventType = EventType.MEMORY_STORE
    content_preview: str
    memory_type: str  # "conversation", "fact", "preference"
    importance: float
    memory_id: str

class MemoryRetrieveEvent(BaseEvent):
    """Memory retrieve event."""

    type: EventType = EventType.MEMORY_RETRIEVE
    query: str
    results_count: int
    top_result_preview: Optional[str] = None

class MemoryUpdateEvent(BaseEvent):
    """Memory update event."""

    type: EventType = EventType.MEMORY_UPDATE
    memory_id: str
    field: str
    old_value: Any
    new_value: Any

class ToolCallEvent(BaseEvent):
    """Tool call event."""

    type: EventType = EventType.TOOL_CALL
    tool_name: str
    parameters: Dict[str, Any]

class ToolResultEvent(BaseEvent):
    """Tool result event."""

    type: EventType = EventType.TOOL_RESULT
    tool_name: str
    result_preview: str
    duration_seconds: float

class ToolErrorEvent(BaseEvent):
    """Tool error event."""

    type: EventType = EventType.TOOL_ERROR
    tool_name: str
    message: str
    details: Optional[Dict[str, Any]] = None

class ConversationStartEvent(BaseEvent):
    """Conversation start event."""

    type: EventType = EventType.CONVERSATION_START
    session_id: str

class ConversationTurnEvent(BaseEvent):
    """Conversation turn event."""

    type: EventType = EventType.CONVERSATION_TURN
    role: str  # "user", "assistant", "system"
    content: str
    turn_id: int

class ConversationEndEvent(BaseEvent):
    """Conversation end event."""

    type: EventType = EventType.CONVERSATION_END
    session_id: str
    duration_seconds: float
    turns_count: int

class LatencyTraceEvent(BaseEvent):
    """Latency trace event."""

    type: EventType = EventType.LATENCY_TRACE
    stt_seconds: float
    llm_seconds: float
    tts_seconds: float
    total_seconds: float
    tool_seconds: Optional[float] = None
    memory_seconds: Optional[float] = None

class ComponentTimingEvent(BaseEvent):
    """Component timing event."""

    type: EventType = EventType.COMPONENT_TIMING
    component: str
    operation: str
    duration_seconds: float

class ComponentStatsEvent(BaseEvent):
    """Component statistics event."""

    type: EventType = EventType.COMPONENT_STATS
    components: Dict[str, Dict[str, Dict[str, Any]]]

class ReplayEvent(BaseEvent):
    """Replay event containing recent important events."""

    type: EventType = EventType.REPLAY
    events: List[Dict[str, Any]]

# Map of event types to event classes
EVENT_CLASS_MAP = {
    EventType.SYSTEM_INFO: SystemInfoEvent,
    EventType.SYSTEM_ERROR: SystemErrorEvent,
    EventType.SYSTEM_METRICS: SystemMetricsEvent,
    EventType.STT_START: STTStartEvent,
    EventType.STT_INTERIM: STTInterimEvent,
    EventType.STT_RESULT: STTResultEvent,
    EventType.STT_ERROR: STTErrorEvent,
    EventType.LLM_START: LLMStartEvent,
    EventType.LLM_TOKEN: LLMTokenEvent,
    EventType.LLM_RESULT: LLMResultEvent,
    EventType.LLM_ERROR: LLMErrorEvent,
    EventType.TTS_START: TTSStartEvent,
    EventType.TTS_PROGRESS: TTSProgressEvent,
    EventType.TTS_RESULT: TTSResultEvent,
    EventType.TTS_ERROR: TTSErrorEvent,
    EventType.MEMORY_STORE: MemoryStoreEvent,
    EventType.MEMORY_RETRIEVE: MemoryRetrieveEvent,
    EventType.MEMORY_UPDATE: MemoryUpdateEvent,
    EventType.TOOL_CALL: ToolCallEvent,
    EventType.TOOL_RESULT: ToolResultEvent,
    EventType.TOOL_ERROR: ToolErrorEvent,
    EventType.CONVERSATION_START: ConversationStartEvent,
    EventType.CONVERSATION_TURN: ConversationTurnEvent,
    EventType.CONVERSATION_END: ConversationEndEvent,
    EventType.LATENCY_TRACE: LatencyTraceEvent,
    EventType.COMPONENT_TIMING: ComponentTimingEvent,
    EventType.COMPONENT_STATS: ComponentStatsEvent,
    EventType.REPLAY: ReplayEvent,
}

def create_event(event_type: Union[str, EventType], **kwargs) -> BaseEvent:
    """
    Create an event of the specified type.

    Args:
        event_type: The type of event to create
        **kwargs: Additional event data

    Returns:
        The created event

    Raises:
        ValueError: If the event type is unknown
    """
    if isinstance(event_type, str):
        event_type = EventType(event_type)

    event_class = EVENT_CLASS_MAP.get(event_type)
    if not event_class:
        raise ValueError(f"Unknown event type: {event_type}")

    return event_class(**kwargs)

def validate_event(event_data: Dict[str, Any]) -> BaseEvent:
    """
    Validate an event dictionary against the schema.

    Args:
        event_data: The event data to validate

    Returns:
        The validated event

    Raises:
        ValueError: If the event is invalid
    """
    if "type" not in event_data:
        raise ValueError("Event missing 'type' field")

    event_type = event_data["type"]
    try:
        event_type = EventType(event_type)
    except ValueError:
        raise ValueError(f"Unknown event type: {event_type}")

    event_class = EVENT_CLASS_MAP.get(event_type)
    if not event_class:
        raise ValueError(f"No schema defined for event type: {event_type}")

    return event_class(**event_data)
