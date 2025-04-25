import React, { useState, useCallback, memo } from 'react';

interface TextInputProps {
  connected: boolean;
  onSendMessage: (text: string) => void;
}

const TextInput: React.FC<TextInputProps> = ({ connected, onSendMessage }) => {
  const [inputText, setInputText] = useState('');

  // Handle input change
  const handleInputChange = useCallback((e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setInputText(e.target.value);
  }, []);

  // Handle form submission
  const handleSubmit = useCallback((e: React.FormEvent) => {
    e.preventDefault();

    if (!connected || !inputText.trim()) {
      console.log(`[TextInput] handleSubmit: Not sending message`, {
        timestamp: new Date().toISOString(),
        component: 'TextInput',
        action: 'submitForm',
        connected,
        hasText: !!inputText.trim(),
        stack: new Error().stack
      });
      return;
    }

    console.log(`[TextInput] handleSubmit: Sending message`, {
      timestamp: new Date().toISOString(),
      component: 'TextInput',
      action: 'sendMessage',
      textLength: inputText.trim().length,
      stack: new Error().stack
    });

    onSendMessage(inputText.trim());
    setInputText('');
  }, [connected, inputText, onSendMessage]);

  // Handle keyboard shortcut (Ctrl+Enter to submit)
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) {
      console.log(`[TextInput] handleKeyDown: Ctrl+Enter pressed`, {
        timestamp: new Date().toISOString(),
        component: 'TextInput',
        action: 'keyboardShortcut',
        key: e.key,
        ctrlKey: e.ctrlKey,
        metaKey: e.metaKey,
        stack: new Error().stack
      });

      e.preventDefault();
      handleSubmit(e);
    }
  }, [handleSubmit]);

  return (
    <div className="card p-4">
      <h2 className="text-xl font-bold mb-4">Text Input</h2>

      <form onSubmit={handleSubmit} className="space-y-3">
        <div>
          <textarea
            className="w-full h-24 bg-dark-600 border border-dark-500 rounded-md p-3 text-white resize-none focus:outline-none focus:ring-2 focus:ring-primary-500"
            placeholder={connected ? "Type your message here..." : "Connect to Coda to send messages..."}
            value={inputText}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            disabled={!connected}
          />
          <p className="text-xs text-gray-400 mt-1">
            Press Ctrl+Enter to send
          </p>
        </div>

        <button
          type="submit"
          className={`w-full py-2 rounded-md transition-colors ${
            connected && inputText.trim()
              ? 'bg-primary-600 hover:bg-primary-700 text-white'
              : 'bg-dark-600 text-gray-400 cursor-not-allowed'
          }`}
          disabled={!connected || !inputText.trim()}
        >
          Send Message
        </button>
      </form>
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(TextInput);
