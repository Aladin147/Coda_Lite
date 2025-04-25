import React from 'react';
import { render, screen } from '@testing-library/react';
import MemoryStatsDisplay from '../MemoryStatsDisplay';
import { useMemoryDebugStats } from '../../../store/memoryDebugStore';

// Mock the store
jest.mock('../../../store/memoryDebugStore', () => ({
  useMemoryDebugStats: jest.fn(),
}));

describe('MemoryStatsDisplay', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });

  it('renders empty state when no stats are available', () => {
    // Mock the store to return null stats
    (useMemoryDebugStats as jest.Mock).mockReturnValue({
      stats: null,
      updateStats: jest.fn(),
    });

    render(<MemoryStatsDisplay />);
    
    // Check that the empty state is rendered
    expect(screen.getByText('No memory statistics available yet.')).toBeInTheDocument();
  });

  it('renders memory statistics when available', () => {
    // Mock the store to return stats
    (useMemoryDebugStats as jest.Mock).mockReturnValue({
      stats: {
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
      },
      updateStats: jest.fn(),
    });

    render(<MemoryStatsDisplay />);
    
    // Check that the stats are rendered
    expect(screen.getByText('Short-term Memory')).toBeInTheDocument();
    expect(screen.getByText('Long-term Memory')).toBeInTheDocument();
    expect(screen.getByText('Memory Type Distribution')).toBeInTheDocument();
    expect(screen.getByText('Operations')).toBeInTheDocument();
    
    // Check specific values
    expect(screen.getByText('5 / 20')).toBeInTheDocument(); // Short-term turns
    expect(screen.getByText('50 / 1000')).toBeInTheDocument(); // Long-term memories
    expect(screen.getByText('fact')).toBeInTheDocument();
    expect(screen.getByText('25')).toBeInTheDocument(); // Fact count
    expect(screen.getByText('preference')).toBeInTheDocument();
    expect(screen.getByText('15')).toBeInTheDocument(); // Preference count
    expect(screen.getByText('conversation')).toBeInTheDocument();
    expect(screen.getByText('10')).toBeInTheDocument(); // Conversation count
    expect(screen.getByText('Total Operations')).toBeInTheDocument();
    expect(screen.getByText('100')).toBeInTheDocument(); // Operations count
  });

  it('calculates usage percentages correctly', () => {
    // Mock the store to return stats
    (useMemoryDebugStats as jest.Mock).mockReturnValue({
      stats: {
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
      },
      updateStats: jest.fn(),
    });

    render(<MemoryStatsDisplay />);
    
    // Check usage percentages
    expect(screen.getByText('25.0% of capacity used')).toBeInTheDocument(); // Short-term usage
    expect(screen.getByText('5.0% of capacity used')).toBeInTheDocument(); // Long-term usage
  });

  it('handles empty memory types gracefully', () => {
    // Mock the store to return stats without memory types
    (useMemoryDebugStats as jest.Mock).mockReturnValue({
      stats: {
        short_term: {
          turn_count: 5,
          max_turns: 20
        },
        long_term: {
          memory_count: 50,
          max_memories: 1000,
          memory_types: {}
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
      },
      updateStats: jest.fn(),
    });

    render(<MemoryStatsDisplay />);
    
    // Memory Type Distribution section should not be rendered
    expect(screen.queryByText('Memory Type Distribution')).not.toBeInTheDocument();
  });
});
