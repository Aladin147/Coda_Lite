import { useCallback } from 'react';
import { useStore, CodaMode, EmotionContext } from './store';
import { CodaEvent } from '../types/events';

/**
 * Hook to access and update the connection state
 */
export const useConnectionState = () => {
  const { connected, setConnected } = useStore(state => ({
    connected: state.connected,
    setConnected: state.setConnected
  }));

  return { connected, setConnected };
};

/**
 * Hook to access and update events
 */
export const useEvents = () => {
  const { events, addEvent } = useStore(state => ({
    events: state.events,
    addEvent: state.addEvent
  }));

  const processEvent = useCallback((event: CodaEvent) => {
    addEvent(event);
  }, [addEvent]);

  return { events, processEvent };
};

/**
 * Hook to access the latest speech recognition result
 */
export const useSpeechRecognition = () => {
  return useStore(state => ({
    recognizedText: state.recognizedText,
    isListening: state.isListening
  }));
};

/**
 * Hook to access the latest LLM response
 */
export const useLLMResponse = () => {
  return useStore(state => ({
    llmResponse: state.llmResponse,
    isProcessing: state.isProcessing
  }));
};

/**
 * Hook to access the TTS state
 */
export const useTTSState = () => {
  return useStore(state => ({
    isSpeaking: state.isSpeaking,
    currentUtterance: state.currentUtterance
  }));
};

/**
 * Hook to access UI state
 * Note: We've removed darkMode toggle functionality as we're always using dark theme
 */
export const useUIState = () => {
  // Return an empty object since we're not using any UI state currently
  return {};
};

/**
 * Hook to access and update Coda's mode and emotion context
 */
export const useCodaMode = () => {
  const { mode, emotionContext, setMode, setEmotionContext } = useStore(state => ({
    mode: state.mode,
    emotionContext: state.emotionContext,
    setMode: state.setMode,
    setEmotionContext: state.setEmotionContext
  }));

  return { mode, emotionContext, setMode, setEmotionContext };
};
