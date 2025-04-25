import React, { useState } from 'react';
import { useMemoryDebugSearch, MemorySearchResult } from '../../store/memoryDebugStore';

/**
 * Memory Search Interface component
 * 
 * This component displays:
 * - Memory search form
 * - Search results
 * - Memory details
 */
const MemorySearchInterface: React.FC = () => {
  const { searchResults, searchQuery, setSearchResults } = useMemoryDebugSearch();
  const [query, setQuery] = useState('');
  const [memoryType, setMemoryType] = useState('');
  const [minImportance, setMinImportance] = useState(0);
  const [selectedMemory, setSelectedMemory] = useState<MemorySearchResult | null>(null);
  const [isSearching, setIsSearching] = useState(false);

  // Handle search form submission
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!query.trim()) return;
    
    setIsSearching(true);
    
    // In a real implementation, this would call the WebSocket API
    // For now, we'll simulate a search with a timeout
    setTimeout(() => {
      // Simulate search results
      const results: MemorySearchResult[] = [
        {
          id: 'mem-1',
          content: `Result for "${query}" with high relevance`,
          type: memoryType || 'fact',
          importance: 0.8,
          timestamp: new Date().toISOString(),
          similarity: 0.92
        },
        {
          id: 'mem-2',
          content: `Another result for "${query}" with medium relevance`,
          type: memoryType || 'preference',
          importance: 0.6,
          timestamp: new Date().toISOString(),
          similarity: 0.75
        },
        {
          id: 'mem-3',
          content: `A third result for "${query}" with lower relevance`,
          type: memoryType || 'conversation',
          importance: 0.4,
          timestamp: new Date().toISOString(),
          similarity: 0.65
        }
      ].filter(result => result.importance >= minImportance);
      
      setSearchResults(results, query);
      setIsSearching(false);
    }, 500);
  };

  // Handle memory selection
  const handleSelectMemory = (memory: MemorySearchResult) => {
    setSelectedMemory(memory);
  };

  // Handle memory reinforcement
  const handleReinforceMemory = (memoryId: string) => {
    console.log(`Reinforcing memory: ${memoryId}`);
    // In a real implementation, this would call the WebSocket API
  };

  // Handle memory forgetting
  const handleForgetMemory = (memoryId: string) => {
    console.log(`Forgetting memory: ${memoryId}`);
    // In a real implementation, this would call the WebSocket API
    
    // Remove from search results
    setSearchResults(
      searchResults.filter(result => result.id !== memoryId),
      searchQuery
    );
    
    // Clear selected memory if it was forgotten
    if (selectedMemory && selectedMemory.id === memoryId) {
      setSelectedMemory(null);
    }
  };

  return (
    <div className="space-y-4">
      {/* Search form */}
      <form onSubmit={handleSearch} className="bg-dark-700 p-3 rounded-lg">
        <div className="mb-3">
          <label htmlFor="query" className="block text-sm font-medium mb-1">Search Query</label>
          <input
            id="query"
            type="text"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Enter search query..."
            className="w-full bg-dark-600 border border-dark-500 rounded px-3 py-2 text-sm"
          />
        </div>
        
        <div className="grid grid-cols-2 gap-3 mb-3">
          <div>
            <label htmlFor="memoryType" className="block text-sm font-medium mb-1">Memory Type</label>
            <select
              id="memoryType"
              value={memoryType}
              onChange={(e) => setMemoryType(e.target.value)}
              className="w-full bg-dark-600 border border-dark-500 rounded px-3 py-2 text-sm"
            >
              <option value="">All Types</option>
              <option value="fact">Fact</option>
              <option value="preference">Preference</option>
              <option value="conversation">Conversation</option>
              <option value="persona">Persona</option>
            </select>
          </div>
          
          <div>
            <label htmlFor="minImportance" className="block text-sm font-medium mb-1">
              Min Importance: {minImportance.toFixed(1)}
            </label>
            <input
              id="minImportance"
              type="range"
              min="0"
              max="1"
              step="0.1"
              value={minImportance}
              onChange={(e) => setMinImportance(parseFloat(e.target.value))}
              className="w-full"
            />
          </div>
        </div>
        
        <button
          type="submit"
          disabled={isSearching || !query.trim()}
          className="w-full px-4 py-2 bg-primary-600 hover:bg-primary-700 disabled:bg-dark-500 disabled:text-gray-400 rounded-md transition-colors"
        >
          {isSearching ? 'Searching...' : 'Search Memories'}
        </button>
      </form>

      {/* Search results */}
      <div className="bg-dark-700 p-3 rounded-lg">
        <h3 className="text-md font-semibold mb-2">
          {searchQuery ? `Results for "${searchQuery}"` : 'Search Results'}
        </h3>
        
        {searchResults.length === 0 ? (
          <div className="text-center py-4 text-gray-400">
            {searchQuery ? 'No results found' : 'Enter a search query to find memories'}
          </div>
        ) : (
          <div className="space-y-2 max-h-64 overflow-y-auto pr-1">
            {searchResults.map((result) => (
              <div
                key={result.id}
                className={`p-2 rounded-md cursor-pointer transition-colors ${
                  selectedMemory?.id === result.id
                    ? 'bg-primary-900 border border-primary-700'
                    : 'bg-dark-600 hover:bg-dark-500'
                }`}
                onClick={() => handleSelectMemory(result)}
              >
                <div className="flex justify-between items-start mb-1">
                  <span className="text-xs font-semibold bg-dark-500 px-2 py-0.5 rounded">
                    {result.type}
                  </span>
                  <div className="flex items-center">
                    <span className="text-xs text-gray-400 mr-2">
                      Importance: {result.importance.toFixed(1)}
                    </span>
                    {result.similarity && (
                      <span className="text-xs text-gray-400">
                        Similarity: {result.similarity.toFixed(2)}
                      </span>
                    )}
                  </div>
                </div>
                <p className="text-sm">{result.content}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Selected memory details */}
      {selectedMemory && (
        <div className="bg-dark-700 p-3 rounded-lg">
          <h3 className="text-md font-semibold mb-2">Memory Details</h3>
          
          <div className="mb-3">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium">ID: {selectedMemory.id}</span>
              <span className="text-xs text-gray-400">
                {new Date(selectedMemory.timestamp).toLocaleString()}
              </span>
            </div>
            
            <div className="bg-dark-600 p-2 rounded-md mb-2">
              <p className="text-sm whitespace-pre-wrap">{selectedMemory.content}</p>
            </div>
            
            <div className="grid grid-cols-2 gap-2 text-sm">
              <div>
                <span className="text-gray-400">Type:</span> {selectedMemory.type}
              </div>
              <div>
                <span className="text-gray-400">Importance:</span> {selectedMemory.importance.toFixed(2)}
              </div>
              {selectedMemory.similarity && (
                <div>
                  <span className="text-gray-400">Similarity:</span> {selectedMemory.similarity.toFixed(2)}
                </div>
              )}
            </div>
          </div>
          
          <div className="flex space-x-2">
            <button
              onClick={() => handleReinforceMemory(selectedMemory.id)}
              className="flex-1 px-3 py-1.5 bg-blue-800 hover:bg-blue-700 text-blue-200 rounded-md text-sm"
            >
              Reinforce
            </button>
            <button
              onClick={() => handleForgetMemory(selectedMemory.id)}
              className="flex-1 px-3 py-1.5 bg-red-900 hover:bg-red-800 text-red-200 rounded-md text-sm"
            >
              Forget
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default MemorySearchInterface;
