import { create } from 'zustand';
import { CodaEvent, isLatencyTraceEvent, isSystemMetricsEvent, isMemoryStoreEvent, isModeChangeEvent, isEmotionChangeEvent, isConversationMessageEvent } from '../types/events';

interface EventState {
  events: CodaEvent[];
  performanceMetrics: {
    stt: number;
    llm: number;
    tts: number;
    total: number;
    stt_audio: number;
    tts_audio: number;
    tool_seconds: number;
    memory_seconds: number;
  };
  systemMetrics: {
    memory_mb: number;
    cpu_percent: number;
    gpu_vram_mb: number;
  };
  memories: {
    id: string;
    content: string;
    type: string;
    importance: number;
    timestamp: string;
  }[];
  messages: {
    id: string;
    role: 'user' | 'assistant';
    content: string;
    timestamp: string;
  }[];
  mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
  emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';
  addEvent: (event: CodaEvent) => void;
  clearEvents: () => void;
}

export const useEventStore = create<EventState>((set) => ({
  events: [],
  performanceMetrics: {
    stt: 0,
    llm: 0,
    tts: 0,
    total: 0,
    stt_audio: 0,
    tts_audio: 0,
    tool_seconds: 0,
    memory_seconds: 0,
  },
  systemMetrics: {
    memory_mb: 0,
    cpu_percent: 0,
    gpu_vram_mb: 0,
  },
  memories: [],
  messages: [],
  mode: 'idle',
  emotion: 'neutral',
  addEvent: (event) => set((state) => {
    // Add event to events list
    const newEvents = [event, ...state.events].slice(0, 100);
    
    // Process specific event types
    if (isLatencyTraceEvent(event)) {
      return {
        events: newEvents,
        performanceMetrics: {
          stt: event.data.stt_seconds,
          llm: event.data.llm_seconds,
          tts: event.data.tts_seconds,
          total: event.data.total_seconds,
          stt_audio: event.data.stt_audio_duration || 0,
          tts_audio: event.data.tts_audio_duration || 0,
          tool_seconds: event.data.tool_seconds || 0,
          memory_seconds: event.data.memory_seconds || 0,
        },
      };
    } else if (isSystemMetricsEvent(event)) {
      return {
        events: newEvents,
        systemMetrics: {
          memory_mb: event.data.memory_mb,
          cpu_percent: event.data.cpu_percent,
          gpu_vram_mb: event.data.gpu_vram_mb || 0,
        },
      };
    } else if (isMemoryStoreEvent(event)) {
      const newMemory = {
        id: event.data.memory_id,
        content: event.data.content_preview,
        type: event.data.memory_type,
        importance: event.data.importance,
        timestamp: event.timestamp,
      };
      
      return {
        events: newEvents,
        memories: [newMemory, ...state.memories].slice(0, 50),
      };
    } else if (isModeChangeEvent(event)) {
      return {
        events: newEvents,
        mode: event.data.mode,
      };
    } else if (isEmotionChangeEvent(event)) {
      return {
        events: newEvents,
        emotion: event.data.emotion,
      };
    } else if (isConversationMessageEvent(event)) {
      const newMessage = {
        id: event.data.message_id,
        role: event.data.role,
        content: event.data.content,
        timestamp: event.timestamp,
      };
      
      return {
        events: newEvents,
        messages: [newMessage, ...state.messages].slice(0, 50),
      };
    }
    
    return { events: newEvents };
  }),
  clearEvents: () => set({
    events: [],
    performanceMetrics: {
      stt: 0,
      llm: 0,
      tts: 0,
      total: 0,
      stt_audio: 0,
      tts_audio: 0,
      tool_seconds: 0,
      memory_seconds: 0,
    },
    systemMetrics: {
      memory_mb: 0,
      cpu_percent: 0,
      gpu_vram_mb: 0,
    },
    memories: [],
    messages: [],
    mode: 'idle',
    emotion: 'neutral',
  }),
}));
