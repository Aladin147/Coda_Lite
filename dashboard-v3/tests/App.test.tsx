import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import App from '../src/App';

// Mock WebSocketClient
vi.mock('../src/WebSocketClient', () => {
  return {
    default: vi.fn().mockImplementation(() => {
      return {
        url: 'ws://localhost:8765',
        socket: {
          readyState: 1, // OPEN
          send: vi.fn()
        },
        connect: vi.fn(),
        disconnect: vi.fn(),
        isConnected: vi.fn().mockReturnValue(true),
        onConnect: null,
        onDisconnect: null,
        onEvent: null,
        onError: null
      };
    })
  };
});

describe('App', () => {
  let mockWsClient: any;
  let sentMessages: any[] = [];

  beforeEach(() => {
    // Clear sent messages
    sentMessages = [];

    // Create mock WebSocketClient
    mockWsClient = {
      socket: {
        readyState: 1, // OPEN
        send: vi.fn((data) => {
          sentMessages.push(JSON.parse(data));
        })
      },
      isConnected: vi.fn().mockReturnValue(true)
    };

    // Set mock WebSocketClient in window
    (window as any).wsClient = mockWsClient;
  });

  afterEach(() => {
    // Clear mocks
    vi.clearAllMocks();
    // Clear window.wsClient
    (window as any).wsClient = undefined;
  });

  it('should render the App component', () => {
    render(<App />);
    expect(screen.getByText('Coda')).toBeInTheDocument();
  });

  it('should send a text message when the text input form is submitted', async () => {
    render(<App />);
    
    // Find the text input
    const textInput = screen.getByPlaceholderText('Type your message here...');
    expect(textInput).toBeInTheDocument();
    
    // Type a message
    fireEvent.change(textInput, { target: { value: 'Hello, Coda!' } });
    
    // Submit the form
    const form = textInput.closest('form');
    expect(form).toBeInTheDocument();
    fireEvent.submit(form!);
    
    // Check that the message was sent
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalled();
      expect(sentMessages.length).toBe(1);
      expect(sentMessages[0].type).toBe('text_input');
      expect(sentMessages[0].data.text).toBe('Hello, Coda!');
    });
  });

  it('should send only one message when the text input form is submitted', async () => {
    render(<App />);
    
    // Find the text input
    const textInput = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message
    fireEvent.change(textInput, { target: { value: 'Hello, Coda!' } });
    
    // Submit the form
    const form = textInput.closest('form');
    fireEvent.submit(form!);
    
    // Check that only one message was sent
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalledTimes(1);
      expect(sentMessages.length).toBe(1);
    });
  });

  it('should send a start listening message when the start listening button is clicked', async () => {
    render(<App />);
    
    // Find the start listening button
    const startButton = screen.getByText('Start Listening');
    expect(startButton).toBeInTheDocument();
    
    // Click the button
    fireEvent.click(startButton);
    
    // Check that the message was sent
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalled();
      expect(sentMessages.length).toBe(1);
      expect(sentMessages[0].type).toBe('stt_start');
    });
  });

  it('should send a stop listening message when the stop listening button is clicked', async () => {
    render(<App />);
    
    // Find the stop listening button
    const stopButton = screen.getByText('Stop Listening');
    expect(stopButton).toBeInTheDocument();
    
    // Click the button
    fireEvent.click(stopButton);
    
    // Check that the message was sent
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalled();
      expect(sentMessages.length).toBe(1);
      expect(sentMessages[0].type).toBe('stt_stop');
    });
  });

  it('should send a demo flow message when the run demo button is clicked', async () => {
    render(<App />);
    
    // Find the run demo button
    const demoButton = screen.getByText('Run Demo');
    expect(demoButton).toBeInTheDocument();
    
    // Click the button
    fireEvent.click(demoButton);
    
    // Check that the message was sent
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalled();
      expect(sentMessages.length).toBe(1);
      expect(sentMessages[0].type).toBe('demo_flow');
      expect(sentMessages[0].data.text).toBe('Tell me a short joke about programming.');
    });
  });

  it('should not send duplicate messages when buttons are clicked multiple times', async () => {
    render(<App />);
    
    // Find the buttons
    const startButton = screen.getByText('Start Listening');
    const stopButton = screen.getByText('Stop Listening');
    const demoButton = screen.getByText('Run Demo');
    
    // Click each button multiple times
    fireEvent.click(startButton);
    fireEvent.click(startButton);
    fireEvent.click(stopButton);
    fireEvent.click(stopButton);
    fireEvent.click(demoButton);
    fireEvent.click(demoButton);
    
    // Check that only three messages were sent (one for each button)
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalledTimes(6);
      expect(sentMessages.length).toBe(6);
      
      // Check message types
      expect(sentMessages[0].type).toBe('stt_start');
      expect(sentMessages[1].type).toBe('stt_start');
      expect(sentMessages[2].type).toBe('stt_stop');
      expect(sentMessages[3].type).toBe('stt_stop');
      expect(sentMessages[4].type).toBe('demo_flow');
      expect(sentMessages[5].type).toBe('demo_flow');
    });
  });

  // Test for rapid message sending
  it('should handle rapid message sending correctly', async () => {
    render(<App />);
    
    // Find the buttons
    const startButton = screen.getByText('Start Listening');
    const stopButton = screen.getByText('Stop Listening');
    
    // Click buttons rapidly
    for (let i = 0; i < 5; i++) {
      fireEvent.click(startButton);
      fireEvent.click(stopButton);
    }
    
    // Check that all messages were sent
    await waitFor(() => {
      expect(mockWsClient.socket.send).toHaveBeenCalledTimes(10);
      expect(sentMessages.length).toBe(10);
      
      // Check message types alternate correctly
      for (let i = 0; i < 5; i++) {
        expect(sentMessages[i * 2].type).toBe('stt_start');
        expect(sentMessages[i * 2 + 1].type).toBe('stt_stop');
      }
    });
  });
});
