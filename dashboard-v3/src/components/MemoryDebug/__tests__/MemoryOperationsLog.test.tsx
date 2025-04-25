import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import MemoryOperationsLog from '../MemoryOperationsLog';
import { useMemoryDebugOperations } from '../../../store/memoryDebugStore';

// Mock the store
jest.mock('../../../store/memoryDebugStore', () => ({
  useMemoryDebugOperations: jest.fn(),
}));

describe('MemoryOperationsLog', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });

  it('renders empty state when no operations are available', () => {
    // Mock the store to return empty operations
    (useMemoryDebugOperations as jest.Mock).mockReturnValue({
      operations: [],
      clearOperations: jest.fn(),
    });

    render(<MemoryOperationsLog />);
    
    // Check that the empty state is rendered
    expect(screen.getByText('No operations logged yet')).toBeInTheDocument();
  });

  it('renders operations when available', () => {
    // Mock the store to return some operations
    (useMemoryDebugOperations as jest.Mock).mockReturnValue({
      operations: [
        {
          timestamp: '2025-04-26T12:34:56.789Z',
          operation_type: 'add_memory',
          details: {
            memory_id: 'memory_123',
            content_preview: 'Test memory content',
            memory_type: 'fact',
            importance: 0.8
          }
        },
        {
          timestamp: '2025-04-26T12:35:56.789Z',
          operation_type: 'retrieve_memories',
          details: {
            query: 'test query',
            results_count: 3
          }
        }
      ],
      clearOperations: jest.fn(),
    });

    render(<MemoryOperationsLog />);
    
    // Check that the operations are rendered
    expect(screen.getByText('add_memory')).toBeInTheDocument();
    expect(screen.getByText('retrieve_memories')).toBeInTheDocument();
    expect(screen.getByText(/Added "Test memory content"/)).toBeInTheDocument();
    expect(screen.getByText(/Retrieved 3 memories for "test query"/)).toBeInTheDocument();
  });

  it('filters operations when filter is applied', () => {
    // Mock the store to return some operations
    (useMemoryDebugOperations as jest.Mock).mockReturnValue({
      operations: [
        {
          timestamp: '2025-04-26T12:34:56.789Z',
          operation_type: 'add_memory',
          details: {
            memory_id: 'memory_123',
            content_preview: 'Test memory content',
            memory_type: 'fact',
            importance: 0.8
          }
        },
        {
          timestamp: '2025-04-26T12:35:56.789Z',
          operation_type: 'retrieve_memories',
          details: {
            query: 'test query',
            results_count: 3
          }
        }
      ],
      clearOperations: jest.fn(),
    });

    render(<MemoryOperationsLog />);
    
    // Enter a filter
    fireEvent.change(screen.getByPlaceholderText('Filter operations...'), {
      target: { value: 'add' }
    });
    
    // Check that only the matching operation is shown
    expect(screen.getByText('add_memory')).toBeInTheDocument();
    expect(screen.queryByText('retrieve_memories')).not.toBeInTheDocument();
  });

  it('calls clearOperations when clear button is clicked', () => {
    // Mock the store with a spy for clearOperations
    const clearOperations = jest.fn();
    (useMemoryDebugOperations as jest.Mock).mockReturnValue({
      operations: [
        {
          timestamp: '2025-04-26T12:34:56.789Z',
          operation_type: 'add_memory',
          details: {
            memory_id: 'memory_123',
            content_preview: 'Test memory content',
            memory_type: 'fact',
            importance: 0.8
          }
        }
      ],
      clearOperations,
    });

    render(<MemoryOperationsLog />);
    
    // Click the clear button
    fireEvent.click(screen.getByText('Clear'));
    
    // Check that clearOperations was called
    expect(clearOperations).toHaveBeenCalledTimes(1);
  });

  it('expands operation details when clicked', () => {
    // Mock the store to return an operation
    (useMemoryDebugOperations as jest.Mock).mockReturnValue({
      operations: [
        {
          timestamp: '2025-04-26T12:34:56.789Z',
          operation_type: 'add_memory',
          details: {
            memory_id: 'memory_123',
            content_preview: 'Test memory content',
            memory_type: 'fact',
            importance: 0.8
          }
        }
      ],
      clearOperations: jest.fn(),
    });

    render(<MemoryOperationsLog />);
    
    // Initially, the details should not be visible
    expect(screen.queryByText(/"memory_id": "memory_123"/)).not.toBeInTheDocument();
    
    // Click the operation to expand it
    fireEvent.click(screen.getByText(/Added "Test memory content"/));
    
    // Now the details should be visible
    expect(screen.getByText(/"memory_id": "memory_123"/)).toBeInTheDocument();
  });
});
