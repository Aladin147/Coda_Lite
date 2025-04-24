import React, { memo } from 'react';
import ReactMarkdown from 'react-markdown';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ConversationViewProps {
  messages: Message[];
}

const ConversationView: React.FC<ConversationViewProps> = ({ messages }) => {
  return (
    <div className="card p-4 h-96 overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Conversation</h2>
      
      {messages.length === 0 ? (
        <div className="flex items-center justify-center h-64 text-gray-400">
          <p>No conversation history yet.</p>
        </div>
      ) : (
        <div className="space-y-4">
          {messages.map((message) => (
            <div 
              key={message.id}
              className={`p-3 rounded-lg ${
                message.role === 'user' 
                  ? 'bg-dark-600 ml-8' 
                  : 'bg-primary-900 mr-8'
              }`}
            >
              <div className="flex items-center mb-1">
                <span className="font-semibold">
                  {message.role === 'user' ? 'You' : 'Coda'}
                </span>
                <span className="text-xs text-gray-400 ml-2">
                  {new Date(message.timestamp).toLocaleTimeString()}
                </span>
              </div>
              <div className="prose prose-sm prose-invert max-w-none">
                <ReactMarkdown>{message.content}</ReactMarkdown>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(ConversationView);
