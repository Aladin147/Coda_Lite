import { create } from 'zustand';

// Define the types for our state
export type CodaMode = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
export type EmotionContext = 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';

// Define the store state
interface StoreState {
  // Connection state
  connected: boolean;
  setConnected: (connected: boolean) => void;
  
  // Coda mode state
  mode: CodaMode;
  setMode: (mode: CodaMode) => void;
  
  // Emotion context state
  emotionContext: EmotionContext;
  setEmotionContext: (emotion: EmotionContext) => void;
  
  // Performance metrics
  metrics: {
    sttLatency: number;
    llmLatency: number;
    ttsLatency: number;
    totalLatency: number;
  };
  updateMetrics: (metrics: Partial<StoreState['metrics']>) => void;
  
  // Conversation history
  messages: {
    role: 'user' | 'assistant';
    content: string;
    timestamp: number;
  }[];
  addMessage: (role: 'user' | 'assistant', content: string) => void;
  clearMessages: () => void;
  
  // Memory state
  memories: {
    id: string;
    content: string;
    importance: number;
    timestamp: number;
  }[];
  addMemory: (memory: { content: string; importance: number }) => void;
  clearMemories: () => void;
  
  // Debug panel state
  showDebugPanel: boolean;
  setShowDebugPanel: (show: boolean) => void;
}

// Create the store
export const useStore = create<StoreState>((set) => ({
  // Connection state
  connected: false,
  setConnected: (connected) => set({ connected }),
  
  // Coda mode state
  mode: 'idle',
  setMode: (mode) => set({ mode }),
  
  // Emotion context state
  emotionContext: 'neutral',
  setEmotionContext: (emotionContext) => set({ emotionContext }),
  
  // Performance metrics
  metrics: {
    sttLatency: 0,
    llmLatency: 0,
    ttsLatency: 0,
    totalLatency: 0,
  },
  updateMetrics: (metrics) => set((state) => ({
    metrics: { ...state.metrics, ...metrics }
  })),
  
  // Conversation history
  messages: [],
  addMessage: (role, content) => set((state) => ({
    messages: [
      ...state.messages,
      { role, content, timestamp: Date.now() }
    ]
  })),
  clearMessages: () => set({ messages: [] }),
  
  // Memory state
  memories: [],
  addMemory: (memory) => set((state) => ({
    memories: [
      ...state.memories,
      { id: Date.now().toString(), ...memory, timestamp: Date.now() }
    ]
  })),
  clearMemories: () => set({ memories: [] }),
  
  // Debug panel state
  showDebugPanel: false,
  setShowDebugPanel: (showDebugPanel) => set({ showDebugPanel }),
}));
