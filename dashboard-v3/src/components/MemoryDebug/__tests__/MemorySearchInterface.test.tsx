import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import MemorySearchInterface from '../MemorySearchInterface';
import { useMemoryDebugSearch } from '../../../store/memoryDebugStore';

// Mock the store
jest.mock('../../../store/memoryDebugStore', () => ({
  useMemoryDebugSearch: jest.fn(),
}));

describe('MemorySearchInterface', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
    
    // Mock setTimeout to execute immediately
    jest.useFakeTimers();
  });
  
  afterEach(() => {
    jest.useRealTimers();
  });

  it('renders the search form', () => {
    // Mock the store to return empty search results
    (useMemoryDebugSearch as jest.Mock).mockReturnValue({
      searchResults: [],
      searchQuery: '',
      setSearchResults: jest.fn(),
    });

    render(<MemorySearchInterface />);
    
    // Check that the search form is rendered
    expect(screen.getByText('Search Query')).toBeInTheDocument();
    expect(screen.getByText('Memory Type')).toBeInTheDocument();
    expect(screen.getByText(/Min Importance/)).toBeInTheDocument();
    expect(screen.getByText('Search Memories')).toBeInTheDocument();
  });

  it('disables search button when query is empty', () => {
    // Mock the store
    (useMemoryDebugSearch as jest.Mock).mockReturnValue({
      searchResults: [],
      searchQuery: '',
      setSearchResults: jest.fn(),
    });

    render(<MemorySearchInterface />);
    
    // Check that the search button is disabled
    expect(screen.getByText('Search Memories')).toBeDisabled();
    
    // Enter a query
    fireEvent.change(screen.getByPlaceholderText('Enter search query...'), {
      target: { value: 'test query' }
    });
    
    // Check that the search button is enabled
    expect(screen.getByText('Search Memories')).not.toBeDisabled();
  });

  it('performs search when form is submitted', async () => {
    // Mock the store with a spy for setSearchResults
    const setSearchResults = jest.fn();
    (useMemoryDebugSearch as jest.Mock).mockReturnValue({
      searchResults: [],
      searchQuery: '',
      setSearchResults,
    });

    render(<MemorySearchInterface />);
    
    // Enter a query
    fireEvent.change(screen.getByPlaceholderText('Enter search query...'), {
      target: { value: 'test query' }
    });
    
    // Submit the form
    fireEvent.click(screen.getByText('Search Memories'));
    
    // Fast-forward timers
    jest.runAllTimers();
    
    // Check that setSearchResults was called with simulated results
    await waitFor(() => {
      expect(setSearchResults).toHaveBeenCalledTimes(1);
      expect(setSearchResults.mock.calls[0][1]).toBe('test query');
      expect(setSearchResults.mock.calls[0][0].length).toBeGreaterThan(0);
    });
  });

  it('renders search results when available', () => {
    // Mock the store to return search results
    (useMemoryDebugSearch as jest.Mock).mockReturnValue({
      searchResults: [
        {
          id: 'mem-1',
          content: 'Test memory 1',
          type: 'fact',
          importance: 0.8,
          timestamp: new Date().toISOString(),
          similarity: 0.92
        },
        {
          id: 'mem-2',
          content: 'Test memory 2',
          type: 'preference',
          importance: 0.6,
          timestamp: new Date().toISOString(),
          similarity: 0.75
        }
      ],
      searchQuery: 'test query',
      setSearchResults: jest.fn(),
    });

    render(<MemorySearchInterface />);
    
    // Check that the results are rendered
    expect(screen.getByText('Results for "test query"')).toBeInTheDocument();
    expect(screen.getByText('Test memory 1')).toBeInTheDocument();
    expect(screen.getByText('Test memory 2')).toBeInTheDocument();
    expect(screen.getByText('fact')).toBeInTheDocument();
    expect(screen.getByText('preference')).toBeInTheDocument();
  });

  it('displays memory details when a result is clicked', () => {
    // Mock the store to return search results
    (useMemoryDebugSearch as jest.Mock).mockReturnValue({
      searchResults: [
        {
          id: 'mem-1',
          content: 'Test memory 1',
          type: 'fact',
          importance: 0.8,
          timestamp: new Date().toISOString(),
          similarity: 0.92
        }
      ],
      searchQuery: 'test query',
      setSearchResults: jest.fn(),
    });

    render(<MemorySearchInterface />);
    
    // Initially, memory details should not be visible
    expect(screen.queryByText('Memory Details')).not.toBeInTheDocument();
    
    // Click a search result
    fireEvent.click(screen.getByText('Test memory 1'));
    
    // Now memory details should be visible
    expect(screen.getByText('Memory Details')).toBeInTheDocument();
    expect(screen.getByText('ID: mem-1')).toBeInTheDocument();
    expect(screen.getByText('Reinforce')).toBeInTheDocument();
    expect(screen.getByText('Forget')).toBeInTheDocument();
  });

  it('removes a memory from results when forgotten', () => {
    // Mock the store with a spy for setSearchResults
    const setSearchResults = jest.fn();
    (useMemoryDebugSearch as jest.Mock).mockReturnValue({
      searchResults: [
        {
          id: 'mem-1',
          content: 'Test memory 1',
          type: 'fact',
          importance: 0.8,
          timestamp: new Date().toISOString(),
          similarity: 0.92
        },
        {
          id: 'mem-2',
          content: 'Test memory 2',
          type: 'preference',
          importance: 0.6,
          timestamp: new Date().toISOString(),
          similarity: 0.75
        }
      ],
      searchQuery: 'test query',
      setSearchResults,
    });

    render(<MemorySearchInterface />);
    
    // Click a search result to select it
    fireEvent.click(screen.getByText('Test memory 1'));
    
    // Click the Forget button
    fireEvent.click(screen.getByText('Forget'));
    
    // Check that setSearchResults was called with the memory removed
    expect(setSearchResults).toHaveBeenCalledTimes(1);
    expect(setSearchResults.mock.calls[0][0].length).toBe(1);
    expect(setSearchResults.mock.calls[0][0][0].id).toBe('mem-2');
  });
});
