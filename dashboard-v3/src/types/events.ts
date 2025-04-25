/**
 * Base interface for all Coda events
 */
export interface CodaEvent {
  version: string;
  seq: number;
  timestamp: string;
  type: string;
  data: any;
}

/**
 * Latency trace event
 */
export interface LatencyTraceEvent extends CodaEvent {
  type: 'latency_trace';
  data: {
    stt_seconds: number;
    llm_seconds: number;
    tts_seconds: number;
    total_seconds: number;
    total_processing_seconds: number;
    stt_audio_duration: number;
    tts_audio_duration: number;
    total_interaction_seconds: number;
    tool_seconds: number;
    memory_seconds: number;
  };
}

/**
 * System metrics event
 */
export interface SystemMetricsEvent extends CodaEvent {
  type: 'system_metrics';
  data: {
    memory_mb: number;
    cpu_percent: number;
    gpu_vram_mb: number;
  };
}

/**
 * Memory store event
 */
export interface MemoryStoreEvent extends CodaEvent {
  type: 'memory_store';
  data: {
    memory_id: string;
    memory_type: string;
    content_preview: string;
    importance: number;
  };
}

/**
 * STT start event
 */
export interface STTStartEvent extends CodaEvent {
  type: 'stt_start';
  data: {};
}

/**
 * STT end event
 */
export interface STTEndEvent extends CodaEvent {
  type: 'stt_end';
  data: {
    text: string;
    duration: number;
  };
}

/**
 * LLM start event
 */
export interface LLMStartEvent extends CodaEvent {
  type: 'llm_start';
  data: {
    prompt: string;
  };
}

/**
 * LLM end event
 */
export interface LLMEndEvent extends CodaEvent {
  type: 'llm_end';
  data: {
    response: string;
    duration: number;
  };
}

/**
 * TTS start event
 */
export interface TTSStartEvent extends CodaEvent {
  type: 'tts_start';
  data: {
    text: string;
  };
}

/**
 * TTS end event
 */
export interface TTSEndEvent extends CodaEvent {
  type: 'tts_end';
  data: {
    duration: number;
  };
}

/**
 * Mode change event
 */
export interface ModeChangeEvent extends CodaEvent {
  type: 'mode_change';
  data: {
    mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
    previous_mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  };
}

/**
 * Emotion change event
 */
export interface EmotionChangeEvent extends CodaEvent {
  type: 'emotion_change';
  data: {
    emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';
    previous_emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';
  };
}

/**
 * Conversation message event
 */
export interface ConversationMessageEvent extends CodaEvent {
  type: 'conversation_message';
  data: {
    message_id: string;
    role: 'user' | 'assistant';
    content: string;
  };
}

/**
 * Type guard for LatencyTraceEvent
 */
export function isLatencyTraceEvent(event: CodaEvent): event is LatencyTraceEvent {
  return event.type === 'latency_trace';
}

/**
 * Type guard for SystemMetricsEvent
 */
export function isSystemMetricsEvent(event: CodaEvent): event is SystemMetricsEvent {
  return event.type === 'system_metrics';
}

/**
 * Type guard for MemoryStoreEvent
 */
export function isMemoryStoreEvent(event: CodaEvent): event is MemoryStoreEvent {
  return event.type === 'memory_store';
}

/**
 * Type guard for ModeChangeEvent
 */
export function isModeChangeEvent(event: CodaEvent): event is ModeChangeEvent {
  return event.type === 'mode_change';
}

/**
 * Type guard for EmotionChangeEvent
 */
export function isEmotionChangeEvent(event: CodaEvent): event is EmotionChangeEvent {
  return event.type === 'emotion_change';
}

/**
 * Type guard for ConversationMessageEvent
 */
export function isConversationMessageEvent(event: CodaEvent): event is ConversationMessageEvent {
  return event.type === 'conversation_message';
}
