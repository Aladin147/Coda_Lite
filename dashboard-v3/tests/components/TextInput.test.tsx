import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import TextInput from '../../src/components/TextInput';

describe('TextInput', () => {
  it('should render the TextInput component', () => {
    render(<TextInput connected={true} onSendMessage={() => {}} />);
    expect(screen.getByText('Text Input')).toBeInTheDocument();
  });

  it('should disable the input when not connected', () => {
    render(<TextInput connected={false} onSendMessage={() => {}} />);
    const textarea = screen.getByPlaceholderText('Connect to Coda to send messages...');
    expect(textarea).toBeDisabled();
  });

  it('should enable the input when connected', () => {
    render(<TextInput connected={true} onSendMessage={() => {}} />);
    const textarea = screen.getByPlaceholderText('Type your message here...');
    expect(textarea).not.toBeDisabled();
  });

  it('should call onSendMessage when the form is submitted', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={true} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message
    fireEvent.change(textarea, { target: { value: 'Hello, Coda!' } });
    
    // Submit the form
    const form = textarea.closest('form');
    fireEvent.submit(form!);
    
    // Check that onSendMessage was called with the correct message
    expect(onSendMessage).toHaveBeenCalledWith('Hello, Coda!');
  });

  it('should clear the input after sending a message', () => {
    render(<TextInput connected={true} onSendMessage={() => {}} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message
    fireEvent.change(textarea, { target: { value: 'Hello, Coda!' } });
    
    // Submit the form
    const form = textarea.closest('form');
    fireEvent.submit(form!);
    
    // Check that the textarea is cleared
    expect(textarea).toHaveValue('');
  });

  it('should not call onSendMessage when the form is submitted with an empty message', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={true} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Submit the form without typing a message
    const form = textarea.closest('form');
    fireEvent.submit(form!);
    
    // Check that onSendMessage was not called
    expect(onSendMessage).not.toHaveBeenCalled();
  });

  it('should not call onSendMessage when not connected', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={false} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Connect to Coda to send messages...');
    
    // Type a message
    fireEvent.change(textarea, { target: { value: 'Hello, Coda!' } });
    
    // Submit the form
    const form = textarea.closest('form');
    fireEvent.submit(form!);
    
    // Check that onSendMessage was not called
    expect(onSendMessage).not.toHaveBeenCalled();
  });

  it('should submit the form when Ctrl+Enter is pressed', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={true} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message
    fireEvent.change(textarea, { target: { value: 'Hello, Coda!' } });
    
    // Press Ctrl+Enter
    fireEvent.keyDown(textarea, { key: 'Enter', ctrlKey: true });
    
    // Check that onSendMessage was called with the correct message
    expect(onSendMessage).toHaveBeenCalledWith('Hello, Coda!');
  });

  it('should not submit the form when Enter is pressed without Ctrl', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={true} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message
    fireEvent.change(textarea, { target: { value: 'Hello, Coda!' } });
    
    // Press Enter without Ctrl
    fireEvent.keyDown(textarea, { key: 'Enter' });
    
    // Check that onSendMessage was not called
    expect(onSendMessage).not.toHaveBeenCalled();
  });

  it('should trim whitespace from the message before sending', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={true} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message with whitespace
    fireEvent.change(textarea, { target: { value: '  Hello, Coda!  ' } });
    
    // Submit the form
    const form = textarea.closest('form');
    fireEvent.submit(form!);
    
    // Check that onSendMessage was called with the trimmed message
    expect(onSendMessage).toHaveBeenCalledWith('Hello, Coda!');
  });

  it('should not call onSendMessage when the message is only whitespace', () => {
    const onSendMessage = vi.fn();
    render(<TextInput connected={true} onSendMessage={onSendMessage} />);
    
    // Find the textarea
    const textarea = screen.getByPlaceholderText('Type your message here...');
    
    // Type a message with only whitespace
    fireEvent.change(textarea, { target: { value: '    ' } });
    
    // Submit the form
    const form = textarea.closest('form');
    fireEvent.submit(form!);
    
    // Check that onSendMessage was not called
    expect(onSendMessage).not.toHaveBeenCalled();
  });
});
