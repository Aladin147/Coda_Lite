# Coda Dashboard Development Documentation

## Current State (as of June 2023)

### Dashboard Versions
- **Dashboard v1**: Original implementation with basic WebSocket connectivity
- **Dashboard v2**: Attempted modernization with Tailwind CSS v4, React hooks, and improved state management

### Current Issues
1. **React Infinite Update Loops**: Components like Avatar and VoiceControls trigger maximum update depth errors
2. **WebSocket Connection Issues**: Event loop warnings in the backend WebSocket server
3. **State Management Challenges**: Prop drilling and unstable references causing re-render cascades
4. **Tailwind CSS v4 Compatibility**: Potential issues with the latest version of Tailwind

### Fixes Implemented
1. **WebSocket Server**: Improved thread-safe event dispatching with proper event loop handling
2. **Component Memoization**: Added useCallback to prevent function recreation on each render
3. **Component Simplification**: Temporarily removed problematic components to maintain basic functionality

## Plan for Dashboard v3

### Technology Stack
- **Frontend Framework**: React 18+
- **CSS Framework**: Tailwind CSS v3 (more stable than v4)
- **State Management**: Zustand for global state
- **WebSocket**: Custom WebSocket service with proper connection management
- **Build Tool**: Vite for fast development and building

### Architecture
1. **Layered Architecture**:
   - **UI Layer**: React components with minimal logic
   - **Service Layer**: WebSocket, API services
   - **State Layer**: Zustand stores for global state
   - **Utility Layer**: Helper functions, formatters, etc.

2. **Component Structure**:
   - **Layout**: Overall dashboard layout
   - **Avatar**: Visual representation of Coda with state-based animations
   - **ConversationView**: Display of conversation history
   - **PerformanceMonitor**: Real-time performance metrics
   - **MemoryViewer**: Display of Coda's memory system
   - **VoiceControls**: Push-to-talk and demo controls
   - **SystemInfo**: System resource usage display

3. **State Management**:
   - **Connection State**: WebSocket connection status
   - **Coda Mode**: Current operational mode (idle, listening, thinking, speaking)
   - **Emotion Context**: Current emotional context for avatar
   - **Events**: WebSocket event history
   - **Performance Metrics**: Processing time metrics
   - **System Metrics**: CPU, memory, GPU usage
   - **Memories**: Memory system data

### Implementation Strategy
1. Start with a minimal working implementation based on v1 dashboard
2. Implement proper state management with Zustand from the beginning
3. Add components incrementally with thorough testing at each step
4. Use React.memo, useCallback, and useMemo strategically to prevent unnecessary re-renders
5. Implement proper WebSocket connection management with reconnection logic
6. Add comprehensive error handling and fallback UI states

### Best Practices
1. **Component Design**:
   - Keep components focused on a single responsibility
   - Use React.memo for pure components
   - Avoid inline function definitions in render methods
   - Use proper dependency arrays in hooks

2. **State Management**:
   - Minimize component state for UI-only concerns
   - Use Zustand for shared state
   - Avoid prop drilling by using context or state management
   - Ensure stable references for objects and functions

3. **Performance**:
   - Lazy load components when possible
   - Use virtualization for long lists
   - Debounce frequent events
   - Profile and optimize render performance

## Lessons Learned
1. **Start Simple**: Begin with a minimal working implementation and add features incrementally
2. **Test Early and Often**: Test components in isolation and integration at each step
3. **Stable Dependencies**: Use stable versions of libraries rather than bleeding edge
4. **State Management**: Implement proper state management from the beginning
5. **Component Boundaries**: Establish clear component boundaries and responsibilities
6. **Reference Stability**: Ensure stable references for objects and functions to prevent unnecessary re-renders
7. **Error Handling**: Implement comprehensive error handling and fallback UI states

## Next Steps
1. Create a new branch for dashboard v3 implementation
2. Set up the basic project structure with Tailwind CSS v3
3. Implement the core WebSocket service with proper connection management
4. Create the basic layout and minimal working components
5. Add state management with Zustand
6. Incrementally add and test each component
7. Implement comprehensive error handling and fallback UI states

## References
- [React Documentation](https://reactjs.org/docs/getting-started.html)
- [Tailwind CSS v3 Documentation](https://v3.tailwindcss.com/docs)
- [Zustand Documentation](https://github.com/pmndrs/zustand)
- [WebSocket API](https://developer.mozilla.org/en-US/docs/Web/API/WebSocket)
- [Vite Documentation](https://vitejs.dev/guide/)
