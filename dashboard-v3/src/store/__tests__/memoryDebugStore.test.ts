import { renderHook, act } from '@testing-library/react-hooks';
import { 
  useMemoryDebugStore, 
  useMemoryDebugOperations, 
  useMemoryDebugStats, 
  useMemoryDebugSearch, 
  useMemoryDebugUI 
} from '../memoryDebugStore';

describe('memoryDebugStore', () => {
  beforeEach(() => {
    // Reset the store before each test
    act(() => {
      const { clearOperations, updateStats, setSearchResults, selectMemory, setActiveTab } = useMemoryDebugStore.getState();
      clearOperations();
      updateStats(null);
      setSearchResults([], '');
      selectMemory(null);
      setActiveTab('operations');
    });
  });

  describe('useMemoryDebugOperations', () => {
    it('should add operations', () => {
      const { result } = renderHook(() => useMemoryDebugOperations());
      
      // Initially, operations should be empty
      expect(result.current.operations).toEqual([]);
      
      // Add an operation
      act(() => {
        result.current.addOperation({
          timestamp: '2025-04-26T12:34:56.789Z',
          operation_type: 'add_memory',
          details: { memory_id: 'memory_123' }
        });
      });
      
      // Check that the operation was added
      expect(result.current.operations.length).toBe(1);
      expect(result.current.operations[0].operation_type).toBe('add_memory');
      
      // Add another operation
      act(() => {
        result.current.addOperation({
          timestamp: '2025-04-26T12:35:56.789Z',
          operation_type: 'retrieve_memories',
          details: { query: 'test query' }
        });
      });
      
      // Check that the operation was added (newest first)
      expect(result.current.operations.length).toBe(2);
      expect(result.current.operations[0].operation_type).toBe('retrieve_memories');
      
      // Clear operations
      act(() => {
        result.current.clearOperations();
      });
      
      // Check that operations were cleared
      expect(result.current.operations).toEqual([]);
    });
  });

  describe('useMemoryDebugStats', () => {
    it('should update stats', () => {
      const { result } = renderHook(() => useMemoryDebugStats());
      
      // Initially, stats should be null
      expect(result.current.stats).toBeNull();
      
      // Update stats
      const mockStats = {
        short_term: {
          turn_count: 5,
          max_turns: 20
        },
        long_term: {
          memory_count: 50,
          max_memories: 1000,
          memory_types: {
            fact: 25,
            preference: 15,
            conversation: 10
          }
        },
        debug: {
          operations_count: 100,
          operations_by_type: {
            add_memory: 30,
            retrieve_memories: 50,
            update_importance: 20
          },
          last_update: Date.now() / 1000
        }
      };
      
      act(() => {
        result.current.updateStats(mockStats);
      });
      
      // Check that stats were updated
      expect(result.current.stats).toEqual(mockStats);
    });
  });

  describe('useMemoryDebugSearch', () => {
    it('should set search results', () => {
      const { result } = renderHook(() => useMemoryDebugSearch());
      
      // Initially, search results should be empty
      expect(result.current.searchResults).toEqual([]);
      expect(result.current.searchQuery).toBe('');
      
      // Set search results
      const mockResults = [
        {
          id: 'mem-1',
          content: 'Test memory 1',
          type: 'fact',
          importance: 0.8,
          timestamp: '2025-04-26T12:34:56.789Z',
          similarity: 0.92
        }
      ];
      
      act(() => {
        result.current.setSearchResults(mockResults, 'test query');
      });
      
      // Check that search results were updated
      expect(result.current.searchResults).toEqual(mockResults);
      expect(result.current.searchQuery).toBe('test query');
    });
  });

  describe('useMemoryDebugUI', () => {
    it('should toggle debug panel', () => {
      const { result } = renderHook(() => useMemoryDebugUI());
      
      // Initially, debug panel should be hidden
      expect(result.current.showDebugPanel).toBe(false);
      
      // Toggle debug panel
      act(() => {
        result.current.toggleDebugPanel();
      });
      
      // Check that debug panel is now visible
      expect(result.current.showDebugPanel).toBe(true);
      
      // Toggle debug panel again
      act(() => {
        result.current.toggleDebugPanel();
      });
      
      // Check that debug panel is hidden again
      expect(result.current.showDebugPanel).toBe(false);
    });

    it('should set active tab', () => {
      const { result } = renderHook(() => useMemoryDebugUI());
      
      // Initially, active tab should be 'operations'
      expect(result.current.activeTab).toBe('operations');
      
      // Set active tab to 'stats'
      act(() => {
        result.current.setActiveTab('stats');
      });
      
      // Check that active tab was updated
      expect(result.current.activeTab).toBe('stats');
      
      // Set active tab to 'search'
      act(() => {
        result.current.setActiveTab('search');
      });
      
      // Check that active tab was updated
      expect(result.current.activeTab).toBe('search');
    });

    it('should select memory', () => {
      const { result } = renderHook(() => useMemoryDebugUI());
      
      // Initially, selected memory should be null
      expect(result.current.selectedMemoryId).toBeNull();
      
      // Select a memory
      act(() => {
        result.current.selectMemory('memory_123');
      });
      
      // Check that selected memory was updated
      expect(result.current.selectedMemoryId).toBe('memory_123');
      
      // Clear selected memory
      act(() => {
        result.current.selectMemory(null);
      });
      
      // Check that selected memory was cleared
      expect(result.current.selectedMemoryId).toBeNull();
    });
  });
});
