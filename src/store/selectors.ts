import { useCodaStore } from './index';

/**
 * Connection state selectors
 */
export const useConnectionState = () => useCodaStore(state => ({
  connected: state.connected,
  setConnected: state.setConnected,
}));

/**
 * Coda mode selectors
 */
export const useCodaMode = () => useCodaStore(state => ({
  mode: state.mode,
  emotionContext: state.emotionContext,
  setMode: state.setMode,
  setEmotionContext: state.setEmotionContext,
}));

/**
 * Events selectors
 */
export const useEvents = () => useCodaStore(state => ({
  events: state.events,
  addEvent: state.addEvent,
  processEvent: state.processEvent,
}));

/**
 * Performance metrics selectors
 */
export const usePerformanceMetrics = () => useCodaStore(state => ({
  performanceMetrics: state.performanceMetrics,
  updatePerformanceMetrics: state.updatePerformanceMetrics,
}));

/**
 * System metrics selectors
 */
export const useSystemMetrics = () => useCodaStore(state => ({
  systemMetrics: state.systemMetrics,
  updateSystemMetrics: state.updateSystemMetrics,
}));

/**
 * Memory selectors
 */
export const useMemories = () => useCodaStore(state => ({
  memories: state.memories,
  addMemory: state.addMemory,
}));

/**
 * Conversation selectors
 */
export const useConversation = () => useCodaStore(state => ({
  conversation: state.conversation,
  addConversationMessage: state.addConversationMessage,
}));

/**
 * Tool usage selectors
 */
export const useToolUsage = () => useCodaStore(state => ({
  toolUsage: state.toolUsage,
  addToolUsage: state.addToolUsage,
}));

/**
 * UI state selectors
 */
export const useUIState = () => useCodaStore(state => ({
  darkMode: state.darkMode,
  toggleDarkMode: state.toggleDarkMode,
}));

/**
 * Get the latest event of a specific type
 * @param type The event type to filter by
 */
export const useLatestEventOfType = (type: string) => useCodaStore(state => 
  state.events.find(event => event.type === type)
);

/**
 * Get all events of a specific type
 * @param type The event type to filter by
 */
export const useEventsOfType = (type: string) => useCodaStore(state => 
  state.events.filter(event => event.type === type)
);
