import { create } from 'zustand';
import { CodaEvent, LatencyTraceEvent, SystemMetricsEvent } from '../types/events';

/**
 * Coda's possible states
 */
export type CodaMode = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';

/**
 * Coda's emotional context
 */
export type EmotionContext = 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';

/**
 * Performance metrics
 */
export interface PerformanceMetrics {
  stt: number;
  llm: number;
  tts: number;
  total: number;
  totalProcessing: number;
  sttAudio: number;
  ttsAudio: number;
  totalInteraction: number;
  toolSeconds: number;
  memorySeconds: number;
}

/**
 * System metrics
 */
export interface SystemMetrics {
  memoryMb: number;
  cpuPercent: number;
  gpuVramMb: number;
}

/**
 * Memory item
 */
export interface MemoryItem {
  id: string;
  content: string;
  type: string;
  importance: number;
  timestamp: string;
}

/**
 * Conversation message
 */
export interface ConversationMessage {
  id: string;
  text: string;
  sender: 'user' | 'coda';
  timestamp: string;
}

/**
 * Tool usage
 */
export interface ToolUsage {
  id: string;
  name: string;
  parameters: Record<string, any>;
  result: any;
  success: boolean;
  error?: string;
  timestamp: string;
}

/**
 * Coda store state
 */
export interface CodaState {
  // Connection state
  connected: boolean;
  
  // Coda state
  mode: CodaMode;
  emotionContext: EmotionContext;
  
  // Events
  events: CodaEvent[];
  
  // Performance metrics
  performanceMetrics: PerformanceMetrics;
  systemMetrics: SystemMetrics;
  
  // Memory
  memories: MemoryItem[];
  
  // Conversation
  conversation: ConversationMessage[];
  
  // Tools
  toolUsage: ToolUsage[];
  
  // UI state
  darkMode: boolean;
  
  // Actions
  setConnected: (connected: boolean) => void;
  setMode: (mode: CodaMode) => void;
  setEmotionContext: (context: EmotionContext) => void;
  addEvent: (event: CodaEvent) => void;
  updatePerformanceMetrics: (metrics: Partial<PerformanceMetrics>) => void;
  updateSystemMetrics: (metrics: Partial<SystemMetrics>) => void;
  addMemory: (memory: MemoryItem) => void;
  addConversationMessage: (message: ConversationMessage) => void;
  addToolUsage: (tool: ToolUsage) => void;
  toggleDarkMode: () => void;
  
  // Event processing
  processEvent: (event: CodaEvent) => void;
}

/**
 * Create the Coda store
 */
export const useCodaStore = create<CodaState>((set, get) => ({
  // Initial state
  connected: false,
  mode: 'idle',
  emotionContext: 'neutral',
  events: [],
  performanceMetrics: {
    stt: 0,
    llm: 0,
    tts: 0,
    total: 0,
    totalProcessing: 0,
    sttAudio: 0,
    ttsAudio: 0,
    totalInteraction: 0,
    toolSeconds: 0,
    memorySeconds: 0,
  },
  systemMetrics: {
    memoryMb: 0,
    cpuPercent: 0,
    gpuVramMb: 0,
  },
  memories: [],
  conversation: [],
  toolUsage: [],
  darkMode: true,
  
  // Actions
  setConnected: (connected) => set({ connected }),
  
  setMode: (mode) => set({ mode }),
  
  setEmotionContext: (emotionContext) => set({ emotionContext }),
  
  addEvent: (event) => set((state) => ({
    events: [event, ...state.events].slice(0, 100), // Keep only the last 100 events
  })),
  
  updatePerformanceMetrics: (metrics) => set((state) => ({
    performanceMetrics: { ...state.performanceMetrics, ...metrics },
  })),
  
  updateSystemMetrics: (metrics) => set((state) => ({
    systemMetrics: { ...state.systemMetrics, ...metrics },
  })),
  
  addMemory: (memory) => set((state) => ({
    memories: [memory, ...state.memories].slice(0, 50), // Keep only the last 50 memories
  })),
  
  addConversationMessage: (message) => set((state) => ({
    conversation: [...state.conversation, message].slice(-100), // Keep only the last 100 messages
  })),
  
  addToolUsage: (tool) => set((state) => ({
    toolUsage: [tool, ...state.toolUsage].slice(0, 50), // Keep only the last 50 tool usages
  })),
  
  toggleDarkMode: () => set((state) => {
    const newDarkMode = !state.darkMode;
    document.documentElement.setAttribute('data-theme', newDarkMode ? 'dark' : 'light');
    return { darkMode: newDarkMode };
  }),
  
  // Event processing
  processEvent: (event) => {
    const state = get();
    
    // Add the event to the events list
    state.addEvent(event);
    
    // Process specific event types
    switch (event.type) {
      case 'stt_start':
        state.setMode('listening');
        break;
        
      case 'stt_result':
        if (event.data?.text) {
          state.addConversationMessage({
            id: `user-${Date.now()}`,
            text: event.data.text,
            sender: 'user',
            timestamp: event.timestamp,
          });
        }
        break;
        
      case 'stt_stop':
        state.setMode('thinking');
        break;
        
      case 'llm_start':
        state.setMode('thinking');
        break;
        
      case 'llm_result':
        if (event.data?.text) {
          state.addConversationMessage({
            id: `coda-${Date.now()}`,
            text: event.data.text,
            sender: 'coda',
            timestamp: event.timestamp,
          });
        }
        break;
        
      case 'tts_start':
        state.setMode('speaking');
        break;
        
      case 'tts_stop':
      case 'tts_end':
        state.setMode('idle');
        break;
        
      case 'memory_store':
        if (event.data) {
          state.addMemory({
            id: event.data.memory_id,
            content: event.data.content_preview,
            type: event.data.memory_type,
            importance: event.data.importance,
            timestamp: event.timestamp,
          });
        }
        break;
        
      case 'tool_call':
        // Tool call is recorded when we get the result
        break;
        
      case 'tool_result':
        if (event.data) {
          state.addToolUsage({
            id: `tool-${Date.now()}`,
            name: event.data.tool_name,
            parameters: event.data.parameters || {},
            result: event.data.result,
            success: event.data.success,
            error: event.data.error,
            timestamp: event.timestamp,
          });
        }
        break;
        
      case 'latency_trace':
        const latencyData = (event as LatencyTraceEvent).data;
        state.updatePerformanceMetrics({
          stt: latencyData.stt_seconds,
          llm: latencyData.llm_seconds,
          tts: latencyData.tts_seconds,
          total: latencyData.total_seconds,
          totalProcessing: latencyData.total_processing_seconds || latencyData.total_seconds,
          sttAudio: latencyData.stt_audio_duration || 0,
          ttsAudio: latencyData.tts_audio_duration || 0,
          totalInteraction: latencyData.total_interaction_seconds ||
            (latencyData.total_seconds + (latencyData.stt_audio_duration || 0) + (latencyData.tts_audio_duration || 0)),
          toolSeconds: latencyData.tool_seconds || 0,
          memorySeconds: latencyData.memory_seconds || 0,
        });
        break;
        
      case 'system_metrics':
        const metricsData = (event as SystemMetricsEvent).data;
        state.updateSystemMetrics({
          memoryMb: metricsData.memory_mb,
          cpuPercent: metricsData.cpu_percent,
          gpuVramMb: metricsData.gpu_vram_mb || 0,
        });
        break;
        
      case 'emotion':
        if (event.data?.emotion) {
          state.setEmotionContext(event.data.emotion as EmotionContext);
        }
        break;
        
      case 'state_change':
        if (event.data?.new_state) {
          state.setMode(event.data.new_state as CodaMode);
        }
        break;
    }
  },
}));
