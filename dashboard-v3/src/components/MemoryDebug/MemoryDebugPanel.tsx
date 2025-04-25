import React from 'react';
import { useMemoryDebugUI } from '../../store/memoryDebugStore';
import MemoryOperationsLog from './MemoryOperationsLog';
import MemoryStatsDisplay from './MemoryStatsDisplay';
import MemorySearchInterface from './MemorySearchInterface';

/**
 * Memory Debug Panel component
 * 
 * This component displays:
 * - Memory operations log
 * - Memory statistics
 * - Memory search interface
 */
const MemoryDebugPanel: React.FC = () => {
  const { activeTab, showDebugPanel, setActiveTab, toggleDebugPanel } = useMemoryDebugUI();

  if (!showDebugPanel) {
    return (
      <div className="flex justify-end mb-2">
        <button
          onClick={toggleDebugPanel}
          className="px-3 py-1 bg-primary-600 hover:bg-primary-700 rounded-md transition-colors text-sm"
        >
          Show Memory Debug
        </button>
      </div>
    );
  }

  return (
    <div className="card p-4 mb-6">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Memory Debug</h2>
        <button
          onClick={toggleDebugPanel}
          className="px-3 py-1 bg-primary-600 hover:bg-primary-700 rounded-md transition-colors text-sm"
        >
          Hide
        </button>
      </div>

      <div className="flex border-b border-dark-600 mb-4">
        <button
          className={`px-4 py-2 ${activeTab === 'operations' ? 'border-b-2 border-primary-500 text-primary-400' : 'text-gray-400 hover:text-gray-300'}`}
          onClick={() => setActiveTab('operations')}
        >
          Operations
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'stats' ? 'border-b-2 border-primary-500 text-primary-400' : 'text-gray-400 hover:text-gray-300'}`}
          onClick={() => setActiveTab('stats')}
        >
          Statistics
        </button>
        <button
          className={`px-4 py-2 ${activeTab === 'search' ? 'border-b-2 border-primary-500 text-primary-400' : 'text-gray-400 hover:text-gray-300'}`}
          onClick={() => setActiveTab('search')}
        >
          Search
        </button>
      </div>

      <div className="h-96 overflow-y-auto">
        {activeTab === 'operations' && <MemoryOperationsLog />}
        {activeTab === 'stats' && <MemoryStatsDisplay />}
        {activeTab === 'search' && <MemorySearchInterface />}
      </div>
    </div>
  );
};

export default MemoryDebugPanel;
