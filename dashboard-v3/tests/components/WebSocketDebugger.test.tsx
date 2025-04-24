import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import WebSocketDebugger from '../../src/components/WebSocketDebugger';

describe('WebSocketDebugger', () => {
  beforeEach(() => {
    // Mock window.wsClient
    (window as any).wsClient = {
      socket: {
        readyState: WebSocket.OPEN
      },
      isConnected: vi.fn().mockReturnValue(true),
      disconnect: vi.fn(),
      connect: vi.fn()
    };
  });

  it('should render the WebSocketDebugger component', () => {
    render(<WebSocketDebugger events={[]} />);
    expect(screen.getByText('WebSocket Debugger')).toBeInTheDocument();
  });

  it('should show connected status when connected', () => {
    render(<WebSocketDebugger events={[]} />);
    expect(screen.getByText('Connected')).toBeInTheDocument();
  });

  it('should show disconnected status when disconnected', () => {
    // Mock disconnected state
    (window as any).wsClient.isConnected = vi.fn().mockReturnValue(false);
    
    render(<WebSocketDebugger events={[]} />);
    expect(screen.getByText('Disconnected')).toBeInTheDocument();
  });

  it('should display events', () => {
    const events = [
      { type: 'test_event', data: { message: 'Test message' }, timestamp: '2023-06-01T12:34:56.789Z' }
    ];
    
    render(<WebSocketDebugger events={events} />);
    expect(screen.getByText('test_event')).toBeInTheDocument();
  });

  it('should filter events based on search term', () => {
    const events = [
      { type: 'test_event_1', data: { message: 'Test message 1' }, timestamp: '2023-06-01T12:34:56.789Z' },
      { type: 'test_event_2', data: { message: 'Test message 2' }, timestamp: '2023-06-01T12:34:57.789Z' }
    ];
    
    render(<WebSocketDebugger events={events} />);
    
    // Both events should be visible initially
    expect(screen.getByText('test_event_1')).toBeInTheDocument();
    expect(screen.getByText('test_event_2')).toBeInTheDocument();
    
    // Filter for event 1
    const filterInput = screen.getByPlaceholderText('Filter events...');
    fireEvent.change(filterInput, { target: { value: 'event_1' } });
    
    // Only event 1 should be visible
    expect(screen.getByText('test_event_1')).toBeInTheDocument();
    expect(screen.queryByText('test_event_2')).not.toBeInTheDocument();
  });

  it('should call disconnect and connect when reconnect button is clicked', () => {
    render(<WebSocketDebugger events={[]} />);
    
    const reconnectButton = screen.getByText('Reconnect');
    fireEvent.click(reconnectButton);
    
    expect((window as any).wsClient.disconnect).toHaveBeenCalled();
    
    // Wait for the setTimeout to execute
    vi.runAllTimers();
    
    expect((window as any).wsClient.connect).toHaveBeenCalled();
  });

  it('should toggle event expansion when clicked', () => {
    const events = [
      { type: 'test_event', data: { message: 'Test message' }, timestamp: '2023-06-01T12:34:56.789Z' }
    ];
    
    render(<WebSocketDebugger events={events} />);
    
    // Event details should not be visible initially
    expect(screen.queryByText('message:')).not.toBeInTheDocument();
    
    // Click the event to expand it
    const eventElement = screen.getByText('test_event');
    fireEvent.click(eventElement.closest('div')!);
    
    // Event details should now be visible
    expect(screen.getByText('message:')).toBeInTheDocument();
    expect(screen.getByText('Test message')).toBeInTheDocument();
  });

  it('should toggle auto-scroll when checkbox is clicked', () => {
    render(<WebSocketDebugger events={[]} />);
    
    const autoScrollCheckbox = screen.getByLabelText('Auto-scroll');
    
    // Auto-scroll should be enabled by default
    expect(autoScrollCheckbox).toBeChecked();
    
    // Click to disable auto-scroll
    fireEvent.click(autoScrollCheckbox);
    
    // Auto-scroll should now be disabled
    expect(autoScrollCheckbox).not.toBeChecked();
  });

  it('should toggle raw JSON view when checkbox is clicked', () => {
    const events = [
      { type: 'test_event', data: { message: 'Test message' }, timestamp: '2023-06-01T12:34:56.789Z' }
    ];
    
    render(<WebSocketDebugger events={events} />);
    
    // Expand the event
    const eventElement = screen.getByText('test_event');
    fireEvent.click(eventElement.closest('div')!);
    
    // Raw JSON should not be visible initially
    expect(screen.queryByText(/"type": "test_event"/)).not.toBeInTheDocument();
    
    // Click to enable raw JSON view
    const rawJsonCheckbox = screen.getByLabelText('Show raw JSON');
    fireEvent.click(rawJsonCheckbox);
    
    // Expand the event again
    fireEvent.click(eventElement.closest('div')!);
    
    // Raw JSON should now be visible
    expect(screen.getByText(/"type": "test_event"/)).toBeInTheDocument();
  });

  it('should send a test message when the Test Message button is clicked', () => {
    // Mock window.wsClient.socket.send
    (window as any).wsClient.socket.send = vi.fn();
    
    render(<WebSocketDebugger events={[]} />);
    
    const testMessageButton = screen.getByText('Test Message');
    fireEvent.click(testMessageButton);
    
    expect((window as any).wsClient.socket.send).toHaveBeenCalled();
    
    // Check that the message is a test_message
    const sentMessage = JSON.parse((window as any).wsClient.socket.send.mock.calls[0][0]);
    expect(sentMessage.type).toBe('test_message');
  });

  it('should send a text input test message when the Test Text Input button is clicked', () => {
    // Mock window.wsClient.socket.send
    (window as any).wsClient.socket.send = vi.fn();
    
    render(<WebSocketDebugger events={[]} />);
    
    const testTextInputButton = screen.getByText('Test Text Input');
    fireEvent.click(testTextInputButton);
    
    expect((window as any).wsClient.socket.send).toHaveBeenCalled();
    
    // Check that the message is a text_input
    const sentMessage = JSON.parse((window as any).wsClient.socket.send.mock.calls[0][0]);
    expect(sentMessage.type).toBe('text_input');
    expect(sentMessage.data.text).toBe('Hello from WebSocket debugger!');
  });
});
