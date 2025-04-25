# Memory Debug UI

The Memory Debug UI provides a visual interface for debugging and visualizing Coda's memory system. It allows users to view memory operations, statistics, and search for memories.

## Features

- **Memory Operations Log**: View a log of memory operations with filtering and details
- **Memory Statistics**: View memory statistics and metrics
- **Memory Search**: Search for memories with filtering by type and importance
- **Memory Controls**: Reinforce and forget memories

## Components

### MemoryDebugPanel

The main component that provides the UI for the memory debug system. It includes:

- Tab navigation for different debug views
- Show/hide toggle for the debug panel
- Container for the debug content

### MemoryOperationsLog

Displays a log of memory operations with:

- Operation filtering by type
- Operation type counts
- Operation details expansion
- Clear operations button

### MemoryStatsDisplay

Displays memory statistics with:

- Short-term memory usage
- Long-term memory usage
- Memory type distribution
- Operations statistics

### MemorySearchInterface

Provides a search interface for memories with:

- Search query input
- Memory type filtering
- Importance filtering
- Search results display
- Memory details view
- Memory reinforcement and forgetting controls

## State Management

The memory debug UI uses a Zustand store for state management:

- **Operations**: Memory operations log
- **Stats**: Memory statistics
- **Search**: Memory search results and query
- **UI**: Debug panel visibility and active tab

## WebSocket Integration

The memory debug UI integrates with the WebSocket system to receive memory debug events:

- `memory_debug_operation`: Received when a memory operation occurs
- `memory_debug_stats`: Received when memory statistics are updated
- `memory_debug_search`: Received when a memory search is performed

## Usage

To use the memory debug UI:

1. Click the "Show Memory Debug" button to display the debug panel
2. Use the tabs to navigate between different debug views
3. View memory operations in the Operations tab
4. View memory statistics in the Statistics tab
5. Search for memories in the Search tab

## Implementation Details

The memory debug UI is implemented in the following files:

- `dashboard-v3/src/components/MemoryDebug/MemoryDebugPanel.tsx`: Main debug panel component
- `dashboard-v3/src/components/MemoryDebug/MemoryOperationsLog.tsx`: Operations log component
- `dashboard-v3/src/components/MemoryDebug/MemoryStatsDisplay.tsx`: Statistics display component
- `dashboard-v3/src/components/MemoryDebug/MemorySearchInterface.tsx`: Search interface component
- `dashboard-v3/src/store/memoryDebugStore.ts`: State management for memory debug

## Testing

The memory debug UI includes comprehensive tests:

- Component tests for all UI components
- Store tests for state management
- Integration tests for WebSocket events

## Future Enhancements

- **Memory Graph Visualization**: Visualize memory relationships as a graph
- **Memory Timeline**: Display memory operations on a timeline
- **Memory Comparison**: Compare memory states before and after operations
- **Memory Export/Import**: Export and import memory debug data
- **Memory Profiling**: Profile memory performance and usage
- **Memory Anomaly Detection**: Detect anomalies in memory operations
