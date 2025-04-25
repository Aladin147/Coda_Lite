import React, { useEffect, useRef } from 'react';
import { useConversation } from '../store/selectors';

const ConversationView: React.FC = () => {
  const { messages } = useConversation();
  const messagesEndRef = useRef<HTMLDivElement>(null);
  
  // Auto-scroll to the bottom when new messages are added
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);
  
  // Format timestamp
  const formatTime = (timestamp: number) => {
    return new Date(timestamp).toLocaleTimeString([], { 
      hour: '2-digit', 
      minute: '2-digit',
      second: '2-digit'
    });
  };
  
  return (
    <div className="card p-4 h-96 flex flex-col">
      <h2 className="text-xl font-semibold mb-4">Conversation</h2>
      
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.length === 0 ? (
          <div className="text-center py-8 opacity-50">
            No messages yet
          </div>
        ) : (
          messages.map((message, index) => (
            <div 
              key={index} 
              className={`p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-blue-900 bg-opacity-30 ml-8' 
                  : 'bg-purple-900 bg-opacity-30 mr-8'
              }`}
            >
              <div className="flex justify-between items-start mb-1">
                <span className="font-semibold">
                  {message.role === 'user' ? 'You' : 'Coda'}
                </span>
                <span className="text-xs opacity-70">
                  {formatTime(message.timestamp)}
                </span>
              </div>
              <p className="whitespace-pre-wrap">{message.content}</p>
            </div>
          ))
        )}
        <div ref={messagesEndRef} />
      </div>
      
      <div className="flex">
        <input 
          type="text" 
          className="flex-1 p-2 rounded-l-md"
          style={{ 
            backgroundColor: 'rgba(255, 255, 255, 0.1)',
            color: 'var(--text-color)',
            border: '1px solid var(--border-color)'
          }}
          placeholder="Type a message..."
          onKeyDown={(e) => {
            if (e.key === 'Enter' && e.currentTarget.value.trim()) {
              // Add user message
              const content = e.currentTarget.value.trim();
              useConversation.getState().addMessage('user', content);
              
              // Clear input
              e.currentTarget.value = '';
              
              // Simulate assistant response after a delay
              setTimeout(() => {
                useConversation.getState().addMessage(
                  'assistant', 
                  `This is a simulated response to: "${content}"`
                );
              }, 1000);
            }
          }}
        />
        <button 
          className="btn rounded-l-none"
          onClick={() => {
            // Simulate clearing the conversation
            if (confirm('Are you sure you want to clear the conversation?')) {
              useConversation.getState().clearMessages();
            }
          }}
        >
          Clear
        </button>
      </div>
    </div>
  );
};

export default ConversationView;
