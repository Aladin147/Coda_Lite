import { create } from 'zustand';

/**
 * Memory operation log entry
 */
export interface MemoryOperation {
  timestamp: string;
  operation_type: string;
  details: Record<string, any>;
}

/**
 * Memory statistics
 */
export interface MemoryStats {
  short_term: {
    turn_count: number;
    max_turns: number;
  };
  long_term: {
    memory_count: number;
    max_memories: number;
    memory_types: Record<string, number>;
  };
  debug: {
    operations_count: number;
    operations_by_type: Record<string, number>;
    last_update: number;
  };
}

/**
 * Memory search result
 */
export interface MemorySearchResult {
  id: string;
  content: string;
  type: string;
  importance: number;
  timestamp: string;
  similarity?: number;
}

/**
 * Memory debug state
 */
interface MemoryDebugState {
  // Operations log
  operations: MemoryOperation[];
  
  // Memory statistics
  stats: MemoryStats | null;
  
  // Search results
  searchResults: MemorySearchResult[];
  searchQuery: string;
  
  // Selected memory
  selectedMemoryId: string | null;
  
  // UI state
  activeTab: 'operations' | 'stats' | 'search';
  showDebugPanel: boolean;
  
  // Actions
  addOperation: (operation: MemoryOperation) => void;
  updateStats: (stats: MemoryStats) => void;
  setSearchResults: (results: MemorySearchResult[], query: string) => void;
  selectMemory: (memoryId: string | null) => void;
  setActiveTab: (tab: 'operations' | 'stats' | 'search') => void;
  toggleDebugPanel: () => void;
  clearOperations: () => void;
}

/**
 * Create the memory debug store
 */
export const useMemoryDebugStore = create<MemoryDebugState>((set) => ({
  // Initial state
  operations: [],
  stats: null,
  searchResults: [],
  searchQuery: '',
  selectedMemoryId: null,
  activeTab: 'operations',
  showDebugPanel: false,
  
  // Actions
  addOperation: (operation) => set((state) => ({
    operations: [operation, ...state.operations].slice(0, 100), // Keep only the last 100 operations
  })),
  
  updateStats: (stats) => set({
    stats,
  }),
  
  setSearchResults: (results, query) => set({
    searchResults: results,
    searchQuery: query,
  }),
  
  selectMemory: (memoryId) => set({
    selectedMemoryId: memoryId,
  }),
  
  setActiveTab: (tab) => set({
    activeTab: tab,
  }),
  
  toggleDebugPanel: () => set((state) => ({
    showDebugPanel: !state.showDebugPanel,
  })),
  
  clearOperations: () => set({
    operations: [],
  }),
}));

/**
 * Memory debug selectors
 */
export const useMemoryDebugOperations = () => useMemoryDebugStore((state) => ({
  operations: state.operations,
  addOperation: state.addOperation,
  clearOperations: state.clearOperations,
}));

export const useMemoryDebugStats = () => useMemoryDebugStore((state) => ({
  stats: state.stats,
  updateStats: state.updateStats,
}));

export const useMemoryDebugSearch = () => useMemoryDebugStore((state) => ({
  searchResults: state.searchResults,
  searchQuery: state.searchQuery,
  setSearchResults: state.setSearchResults,
}));

export const useMemoryDebugUI = () => useMemoryDebugStore((state) => ({
  activeTab: state.activeTab,
  showDebugPanel: state.showDebugPanel,
  selectedMemoryId: state.selectedMemoryId,
  setActiveTab: state.setActiveTab,
  toggleDebugPanel: state.toggleDebugPanel,
  selectMemory: state.selectMemory,
}));
