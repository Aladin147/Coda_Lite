import { useStore } from './store';

/**
 * Hook to access connection state
 */
export const useConnectionState = () => {
  const { connected, setConnected } = useStore(state => ({
    connected: state.connected,
    setConnected: state.setConnected
  }));

  return { connected, setConnected };
};

/**
 * Hook to access Coda mode and emotion context
 */
export const useCodaMode = () => {
  const { mode, setMode, emotionContext, setEmotionContext } = useStore(state => ({
    mode: state.mode,
    setMode: state.setMode,
    emotionContext: state.emotionContext,
    setEmotionContext: state.setEmotionContext
  }));

  return { mode, setMode, emotionContext, setEmotionContext };
};

/**
 * Hook to access performance metrics
 */
export const usePerformanceMetrics = () => {
  const { metrics, updateMetrics } = useStore(state => ({
    metrics: state.metrics,
    updateMetrics: state.updateMetrics
  }));

  return { metrics, updateMetrics };
};

/**
 * Hook to access conversation history
 */
export const useConversation = () => {
  const { messages, addMessage, clearMessages } = useStore(state => ({
    messages: state.messages,
    addMessage: state.addMessage,
    clearMessages: state.clearMessages
  }));

  return { messages, addMessage, clearMessages };
};

/**
 * Hook to access memory state
 */
export const useMemories = () => {
  const { memories, addMemory, clearMemories } = useStore(state => ({
    memories: state.memories,
    addMemory: state.addMemory,
    clearMemories: state.clearMemories
  }));

  return { memories, addMemory, clearMemories };
};

/**
 * Hook to access debug panel state
 */
export const useDebugPanel = () => {
  const { showDebugPanel, setShowDebugPanel } = useStore(state => ({
    showDebugPanel: state.showDebugPanel,
    setShowDebugPanel: state.setShowDebugPanel
  }));

  return { showDebugPanel, setShowDebugPanel };
};
