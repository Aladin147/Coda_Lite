/**
 * Types for WebSocket events
 */

// Base event interface
export interface BaseEvent {
  type: string;
  timestamp: string;
  data?: any;
}

// STT Events
export interface STTStartEvent extends BaseEvent {
  type: 'stt_start';
  data: {
    mode: 'push_to_talk' | 'wake_word' | 'continuous';
    continuous?: boolean;
  };
}

export interface STTResultEvent extends BaseEvent {
  type: 'stt_result';
  data: {
    text: string;
    language?: string;
    confidence?: number;
  };
}

export interface STTStopEvent extends BaseEvent {
  type: 'stt_stop';
}

// LLM Events
export interface LLMStartEvent extends BaseEvent {
  type: 'llm_start';
  data: {
    prompt?: string;
    model?: string;
  };
}

export interface LLMTokenEvent extends BaseEvent {
  type: 'llm_token';
  data: {
    token: string;
  };
}

export interface LLMResultEvent extends BaseEvent {
  type: 'llm_result';
  data: {
    text: string;
    model?: string;
    tokens?: number;
  };
}

// TTS Events
export interface TTSStartEvent extends BaseEvent {
  type: 'tts_start';
  data: {
    text: string;
    voice?: string;
  };
}

export interface TTSResultEvent extends BaseEvent {
  type: 'tts_result';
  data: {
    audio_path: string;
    duration_seconds?: number;
  };
}

export interface TTSStopEvent extends BaseEvent {
  type: 'tts_stop';
}

export interface TTSEndEvent extends BaseEvent {
  type: 'tts_end';
}

// Memory Events
export interface MemoryStoreEvent extends BaseEvent {
  type: 'memory_store';
  data: {
    memory_id: string;
    memory_type: string;
    content_preview: string;
    importance: number;
  };
}

export interface MemoryRetrieveEvent extends BaseEvent {
  type: 'memory_retrieve';
  data: {
    memory_id: string;
    memory_type: string;
    content_preview: string;
    importance: number;
    similarity?: number;
  };
}

// Tool Events
export interface ToolCallEvent extends BaseEvent {
  type: 'tool_call';
  data: {
    tool_name: string;
    parameters: Record<string, any>;
  };
}

export interface ToolResultEvent extends BaseEvent {
  type: 'tool_result';
  data: {
    tool_name: string;
    result: any;
    success: boolean;
    error?: string;
  };
}

// Performance Events
export interface LatencyTraceEvent extends BaseEvent {
  type: 'latency_trace';
  data: {
    stt_seconds: number;
    llm_seconds: number;
    tts_seconds: number;
    total_seconds: number;
    total_processing_seconds: number;
    stt_audio_duration?: number;
    tts_audio_duration?: number;
    total_interaction_seconds?: number;
    tool_seconds?: number;
    memory_seconds?: number;
  };
}

export interface SystemMetricsEvent extends BaseEvent {
  type: 'system_metrics';
  data: {
    memory_mb: number;
    cpu_percent: number;
    gpu_vram_mb?: number;
  };
}

export interface ComponentTimingEvent extends BaseEvent {
  type: 'component_timing';
  data: {
    component: string;
    operation: string;
    duration_seconds: number;
  };
}

// Emotion/State Events
export interface EmotionEvent extends BaseEvent {
  type: 'emotion';
  data: {
    emotion: string;
    intensity: number;
    trigger?: string;
  };
}

export interface StateChangeEvent extends BaseEvent {
  type: 'state_change';
  data: {
    previous_state: string;
    new_state: string;
    reason?: string;
  };
}

// Union type of all events
export type CodaEvent = 
  | STTStartEvent
  | STTResultEvent
  | STTStopEvent
  | LLMStartEvent
  | LLMTokenEvent
  | LLMResultEvent
  | TTSStartEvent
  | TTSResultEvent
  | TTSStopEvent
  | TTSEndEvent
  | MemoryStoreEvent
  | MemoryRetrieveEvent
  | ToolCallEvent
  | ToolResultEvent
  | LatencyTraceEvent
  | SystemMetricsEvent
  | ComponentTimingEvent
  | EmotionEvent
  | StateChangeEvent
  | BaseEvent; // Fallback for unknown events
