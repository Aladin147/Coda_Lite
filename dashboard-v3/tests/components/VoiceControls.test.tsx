import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import VoiceControls from '../../src/components/VoiceControls';

describe('VoiceControls', () => {
  it('should render the VoiceControls component', () => {
    render(
      <VoiceControls
        connected={true}
        onStartListening={() => {}}
        onStopListening={() => {}}
        onRunDemo={() => {}}
      />
    );
    expect(screen.getByText('Voice Controls')).toBeInTheDocument();
  });

  it('should disable buttons when not connected', () => {
    render(
      <VoiceControls
        connected={false}
        onStartListening={() => {}}
        onStopListening={() => {}}
        onRunDemo={() => {}}
      />
    );
    
    const startButton = screen.getByText('Start Listening');
    const stopButton = screen.getByText('Stop Listening');
    const demoButton = screen.getByText('Run Demo');
    
    expect(startButton).toBeDisabled();
    expect(stopButton).toBeDisabled();
    expect(demoButton).toBeDisabled();
  });

  it('should enable buttons when connected', () => {
    render(
      <VoiceControls
        connected={true}
        onStartListening={() => {}}
        onStopListening={() => {}}
        onRunDemo={() => {}}
      />
    );
    
    const startButton = screen.getByText('Start Listening');
    const stopButton = screen.getByText('Stop Listening');
    const demoButton = screen.getByText('Run Demo');
    
    expect(startButton).not.toBeDisabled();
    expect(stopButton).not.toBeDisabled();
    expect(demoButton).not.toBeDisabled();
  });

  it('should call onStartListening when the start button is clicked', () => {
    const onStartListening = vi.fn();
    render(
      <VoiceControls
        connected={true}
        onStartListening={onStartListening}
        onStopListening={() => {}}
        onRunDemo={() => {}}
      />
    );
    
    const startButton = screen.getByText('Start Listening');
    fireEvent.click(startButton);
    
    expect(onStartListening).toHaveBeenCalled();
  });

  it('should call onStopListening when the stop button is clicked', () => {
    const onStopListening = vi.fn();
    render(
      <VoiceControls
        connected={true}
        onStartListening={() => {}}
        onStopListening={onStopListening}
        onRunDemo={() => {}}
      />
    );
    
    const stopButton = screen.getByText('Stop Listening');
    fireEvent.click(stopButton);
    
    expect(onStopListening).toHaveBeenCalled();
  });

  it('should call onRunDemo when the demo button is clicked', () => {
    const onRunDemo = vi.fn();
    render(
      <VoiceControls
        connected={true}
        onStartListening={() => {}}
        onStopListening={() => {}}
        onRunDemo={onRunDemo}
      />
    );
    
    const demoButton = screen.getByText('Run Demo');
    fireEvent.click(demoButton);
    
    expect(onRunDemo).toHaveBeenCalled();
  });

  it('should not call handlers when buttons are clicked while disconnected', () => {
    const onStartListening = vi.fn();
    const onStopListening = vi.fn();
    const onRunDemo = vi.fn();
    
    render(
      <VoiceControls
        connected={false}
        onStartListening={onStartListening}
        onStopListening={onStopListening}
        onRunDemo={onRunDemo}
      />
    );
    
    const startButton = screen.getByText('Start Listening');
    const stopButton = screen.getByText('Stop Listening');
    const demoButton = screen.getByText('Run Demo');
    
    fireEvent.click(startButton);
    fireEvent.click(stopButton);
    fireEvent.click(demoButton);
    
    expect(onStartListening).not.toHaveBeenCalled();
    expect(onStopListening).not.toHaveBeenCalled();
    expect(onRunDemo).not.toHaveBeenCalled();
  });

  it('should call handlers only once when buttons are clicked once', () => {
    const onStartListening = vi.fn();
    const onStopListening = vi.fn();
    const onRunDemo = vi.fn();
    
    render(
      <VoiceControls
        connected={true}
        onStartListening={onStartListening}
        onStopListening={onStopListening}
        onRunDemo={onRunDemo}
      />
    );
    
    const startButton = screen.getByText('Start Listening');
    const stopButton = screen.getByText('Stop Listening');
    const demoButton = screen.getByText('Run Demo');
    
    fireEvent.click(startButton);
    fireEvent.click(stopButton);
    fireEvent.click(demoButton);
    
    expect(onStartListening).toHaveBeenCalledTimes(1);
    expect(onStopListening).toHaveBeenCalledTimes(1);
    expect(onRunDemo).toHaveBeenCalledTimes(1);
  });
});
