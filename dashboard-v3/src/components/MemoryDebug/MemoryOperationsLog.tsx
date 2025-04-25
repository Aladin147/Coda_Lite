import React, { useState } from 'react';
import { useMemoryDebugOperations, MemoryOperation } from '../../store/memoryDebugStore';

/**
 * Memory Operations Log component
 * 
 * This component displays:
 * - Memory operations log
 * - Operation filtering
 * - Operation details
 */
const MemoryOperationsLog: React.FC = () => {
  const { operations, clearOperations } = useMemoryDebugOperations();
  const [filter, setFilter] = useState('');
  const [expandedOperations, setExpandedOperations] = useState<Record<string, boolean>>({});

  // Filter operations by type
  const filteredOperations = filter
    ? operations.filter(op => op.operation_type.includes(filter))
    : operations;

  // Toggle operation expansion
  const toggleExpand = (timestamp: string) => {
    setExpandedOperations(prev => ({
      ...prev,
      [timestamp]: !prev[timestamp]
    }));
  };

  // Get operation type counts
  const operationCounts = operations.reduce((counts, op) => {
    counts[op.operation_type] = (counts[op.operation_type] || 0) + 1;
    return counts;
  }, {} as Record<string, number>);

  // Get unique operation types
  const operationTypes = Object.keys(operationCounts).sort();

  // Format timestamp
  const formatTime = (timestamp: string) => {
    try {
      const date = new Date(timestamp);
      return date.toLocaleTimeString();
    } catch (e) {
      return timestamp;
    }
  };

  // Get operation color
  const getOperationColor = (type: string) => {
    switch (type) {
      case 'add_memory':
      case 'add_turn':
        return 'bg-green-800 text-green-200';
      case 'retrieve_memories':
      case 'search':
      case 'get':
        return 'bg-blue-800 text-blue-200';
      case 'update_importance':
      case 'reinforce':
        return 'bg-yellow-800 text-yellow-200';
      case 'forget':
      case 'apply_forgetting':
        return 'bg-red-800 text-red-200';
      case 'create_snapshot':
      case 'apply_snapshot':
        return 'bg-purple-800 text-purple-200';
      default:
        return 'bg-gray-800 text-gray-200';
    }
  };

  return (
    <div>
      <div className="flex justify-between items-center mb-4">
        <div className="flex items-center">
          <input
            type="text"
            placeholder="Filter operations..."
            value={filter}
            onChange={(e) => setFilter(e.target.value)}
            className="bg-dark-700 border border-dark-600 rounded px-3 py-1 text-sm w-48 mr-2"
          />
          <div className="text-xs text-gray-400">
            {filteredOperations.length} of {operations.length} operations
          </div>
        </div>
        <button
          onClick={clearOperations}
          className="px-3 py-1 bg-red-900 hover:bg-red-800 text-red-200 rounded-md text-xs"
        >
          Clear
        </button>
      </div>

      <div className="flex flex-wrap gap-2 mb-4">
        {operationTypes.map(type => (
          <button
            key={type}
            onClick={() => setFilter(type === filter ? '' : type)}
            className={`px-2 py-1 rounded-md text-xs ${
              filter === type 
                ? 'bg-primary-600 text-white' 
                : getOperationColor(type)
            }`}
          >
            {type} ({operationCounts[type]})
          </button>
        ))}
      </div>

      {filteredOperations.length === 0 ? (
        <div className="text-center py-8 text-gray-400">
          No operations logged yet
        </div>
      ) : (
        <div className="space-y-2">
          {filteredOperations.map((operation, index) => (
            <OperationItem
              key={`${operation.timestamp}-${index}`}
              operation={operation}
              isExpanded={!!expandedOperations[operation.timestamp]}
              toggleExpand={() => toggleExpand(operation.timestamp)}
              formatTime={formatTime}
              getOperationColor={getOperationColor}
            />
          ))}
        </div>
      )}
    </div>
  );
};

interface OperationItemProps {
  operation: MemoryOperation;
  isExpanded: boolean;
  toggleExpand: () => void;
  formatTime: (timestamp: string) => string;
  getOperationColor: (type: string) => string;
}

const OperationItem: React.FC<OperationItemProps> = ({
  operation,
  isExpanded,
  toggleExpand,
  formatTime,
  getOperationColor
}) => {
  // Get operation summary
  const getSummary = (operation: MemoryOperation) => {
    const { operation_type, details } = operation;
    
    switch (operation_type) {
      case 'add_memory':
        return `Added "${details.content_preview || 'memory'}" (${details.memory_type})`;
      case 'add_turn':
        return `Added ${details.role} turn: "${details.content_preview || ''}"`;
      case 'retrieve_memories':
        return `Retrieved ${details.results_count || 0} memories for "${details.query || ''}"`;
      case 'search':
        return `Searched for "${details.query || ''}" (${details.results_count || 0} results)`;
      case 'get':
        return `Retrieved memory ${details.memory_id || ''} (found: ${details.found ? 'yes' : 'no'})`;
      case 'update_importance':
        return `Updated importance of ${details.memory_id || ''} from ${details.old_importance?.toFixed(2) || '?'} to ${details.new_importance?.toFixed(2) || '?'}`;
      case 'reinforce':
        return `Reinforced memory ${details.memory_id || ''} with strength ${details.strength?.toFixed(2) || '?'}`;
      case 'forget':
        return `Forgot memory ${details.memory_id || ''} (${details.success ? 'success' : 'failed'})`;
      case 'apply_forgetting':
        return `Applied forgetting mechanism (forgot ${details.forgotten_count || 0} memories)`;
      case 'create_snapshot':
        return `Created memory snapshot ${details.snapshot_id || ''}`;
      case 'apply_snapshot':
        return `Applied memory snapshot ${details.snapshot_id || ''} (${details.success ? 'success' : 'failed'})`;
      default:
        return `${operation_type} operation`;
    }
  };

  return (
    <div className="bg-dark-700 rounded-md overflow-hidden">
      <div 
        className="flex justify-between items-center p-2 cursor-pointer hover:bg-dark-600"
        onClick={toggleExpand}
      >
        <div className="flex items-center">
          <span className={`px-2 py-0.5 rounded text-xs mr-2 ${getOperationColor(operation.operation_type)}`}>
            {operation.operation_type}
          </span>
          <span className="text-sm">{getSummary(operation)}</span>
        </div>
        <div className="flex items-center">
          <span className="text-xs text-gray-400 mr-2">
            {formatTime(operation.timestamp)}
          </span>
          <span className="text-xs">
            {isExpanded ? '▼' : '▶'}
          </span>
        </div>
      </div>
      
      {isExpanded && (
        <div className="p-2 bg-dark-800 border-t border-dark-600">
          <pre className="text-xs overflow-x-auto whitespace-pre-wrap">
            {JSON.stringify(operation.details, null, 2)}
          </pre>
        </div>
      )}
    </div>
  );
};

export default MemoryOperationsLog;
