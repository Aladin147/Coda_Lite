import { create } from 'zustand';
import { CodaEvent } from '../types/events';

// Coda mode types
export type CodaMode = 'idle' | 'listening' | 'thinking' | 'speaking' | 'error';
export type EmotionContext = 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused';

/**
 * Interface for the application state
 */
interface AppState {
  // Connection state
  connected: boolean;
  setConnected: (connected: boolean) => void;

  // Events
  events: CodaEvent[];
  addEvent: (event: CodaEvent) => void;
  clearEvents: () => void;

  // Speech recognition
  recognizedText: string;
  isListening: boolean;
  setRecognizedText: (text: string) => void;
  setIsListening: (isListening: boolean) => void;

  // LLM
  llmResponse: string;
  isProcessing: boolean;
  setLLMResponse: (response: string) => void;
  setIsProcessing: (isProcessing: boolean) => void;

  // TTS
  isSpeaking: boolean;
  currentUtterance: string;
  setIsSpeaking: (isSpeaking: boolean) => void;
  setCurrentUtterance: (utterance: string) => void;

  // UI State - Dark mode is now always enabled
  // We've removed the darkMode toggle functionality

  // Coda Mode and Emotion
  mode: CodaMode;
  emotionContext: EmotionContext;
  setMode: (mode: CodaMode) => void;
  setEmotionContext: (emotion: EmotionContext) => void;
}

/**
 * Create the store
 */
export const useStore = create<AppState>((set) => ({
  // Connection state
  connected: false,
  setConnected: (connected) => set({ connected }),

  // Events
  events: [],
  addEvent: (event) => set((state) => ({
    events: [...state.events, event]
  })),
  clearEvents: () => set({ events: [] }),

  // Speech recognition
  recognizedText: '',
  isListening: false,
  setRecognizedText: (text) => set({ recognizedText: text }),
  setIsListening: (isListening) => set({ isListening }),

  // LLM
  llmResponse: '',
  isProcessing: false,
  setLLMResponse: (response) => set({ llmResponse: response }),
  setIsProcessing: (isProcessing) => set({ isProcessing }),

  // TTS
  isSpeaking: false,
  currentUtterance: '',
  setIsSpeaking: (isSpeaking) => set({ isSpeaking }),
  setCurrentUtterance: (utterance) => set({ currentUtterance: utterance }),

  // UI State - Dark mode is now always enabled
  // We've removed the darkMode toggle functionality

  // Coda Mode and Emotion
  mode: 'idle' as CodaMode,
  emotionContext: 'neutral' as EmotionContext,
  setMode: (mode) => set({ mode }),
  setEmotionContext: (emotionContext) => set({ emotionContext }),
}));
