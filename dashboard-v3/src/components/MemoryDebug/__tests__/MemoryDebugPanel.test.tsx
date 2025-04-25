import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryDebugPanel } from '..';
import { useMemoryDebugUI } from '../../../store/memoryDebugStore';

// Mock the store
jest.mock('../../../store/memoryDebugStore', () => ({
  useMemoryDebugUI: jest.fn(),
  useMemoryDebugOperations: jest.fn().mockReturnValue({
    operations: [],
    addOperation: jest.fn(),
    clearOperations: jest.fn(),
  }),
  useMemoryDebugStats: jest.fn().mockReturnValue({
    stats: null,
    updateStats: jest.fn(),
  }),
  useMemoryDebugSearch: jest.fn().mockReturnValue({
    searchResults: [],
    searchQuery: '',
    setSearchResults: jest.fn(),
  }),
}));

describe('MemoryDebugPanel', () => {
  beforeEach(() => {
    // Reset mocks
    jest.clearAllMocks();
  });

  it('renders the show button when debug panel is hidden', () => {
    // Mock the store to return panel hidden
    (useMemoryDebugUI as jest.Mock).mockReturnValue({
      activeTab: 'operations',
      showDebugPanel: false,
      setActiveTab: jest.fn(),
      toggleDebugPanel: jest.fn(),
    });

    render(<MemoryDebugPanel />);
    
    // Check that the show button is rendered
    expect(screen.getByText('Show Memory Debug')).toBeInTheDocument();
  });

  it('renders the debug panel when showDebugPanel is true', () => {
    // Mock the store to return panel visible
    (useMemoryDebugUI as jest.Mock).mockReturnValue({
      activeTab: 'operations',
      showDebugPanel: true,
      setActiveTab: jest.fn(),
      toggleDebugPanel: jest.fn(),
    });

    render(<MemoryDebugPanel />);
    
    // Check that the panel is rendered
    expect(screen.getByText('Memory Debug')).toBeInTheDocument();
    expect(screen.getByText('Operations')).toBeInTheDocument();
    expect(screen.getByText('Statistics')).toBeInTheDocument();
    expect(screen.getByText('Search')).toBeInTheDocument();
  });

  it('calls toggleDebugPanel when show button is clicked', () => {
    // Mock the store with a spy for toggleDebugPanel
    const toggleDebugPanel = jest.fn();
    (useMemoryDebugUI as jest.Mock).mockReturnValue({
      activeTab: 'operations',
      showDebugPanel: false,
      setActiveTab: jest.fn(),
      toggleDebugPanel,
    });

    render(<MemoryDebugPanel />);
    
    // Click the show button
    fireEvent.click(screen.getByText('Show Memory Debug'));
    
    // Check that toggleDebugPanel was called
    expect(toggleDebugPanel).toHaveBeenCalledTimes(1);
  });

  it('calls setActiveTab when a tab is clicked', () => {
    // Mock the store with a spy for setActiveTab
    const setActiveTab = jest.fn();
    (useMemoryDebugUI as jest.Mock).mockReturnValue({
      activeTab: 'operations',
      showDebugPanel: true,
      setActiveTab,
      toggleDebugPanel: jest.fn(),
    });

    render(<MemoryDebugPanel />);
    
    // Click the Statistics tab
    fireEvent.click(screen.getByText('Statistics'));
    
    // Check that setActiveTab was called with the correct argument
    expect(setActiveTab).toHaveBeenCalledWith('stats');
    
    // Click the Search tab
    fireEvent.click(screen.getByText('Search'));
    
    // Check that setActiveTab was called with the correct argument
    expect(setActiveTab).toHaveBeenCalledWith('search');
  });
});
