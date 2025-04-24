import React, { memo, useRef, useEffect } from 'react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface ConversationViewProps {
  messages: Message[];
}

// Format the timestamp in a more readable way
const formatTimestamp = (timestamp: string): string => {
  const date = new Date(timestamp);
  const now = new Date();
  const isToday = date.toDateString() === now.toDateString();

  if (isToday) {
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  } else {
    return date.toLocaleDateString([], { month: 'short', day: 'numeric' }) +
           ' ' +
           date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  }
};

// Group messages by date
const groupMessagesByDate = (messages: Message[]): { date: string; messages: Message[] }[] => {
  const groups: { [key: string]: Message[] } = {};

  messages.forEach(message => {
    const date = new Date(message.timestamp).toLocaleDateString();
    if (!groups[date]) {
      groups[date] = [];
    }
    groups[date].push(message);
  });

  return Object.entries(groups).map(([date, messages]) => ({
    date,
    messages
  })).sort((a, b) => new Date(b.date).getTime() - new Date(a.date).getTime());
};

const ConversationView: React.FC<ConversationViewProps> = ({ messages }) => {
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to the bottom when new messages arrive
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);

  // Group messages by date
  const groupedMessages = groupMessagesByDate(messages);

  return (
    <div className="card p-4 h-[500px] overflow-y-auto">
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold">Conversation</h2>

        {messages.length > 0 && (
          <button
            className="text-xs text-gray-400 hover:text-white transition-colors"
            onClick={() => {
              if (messagesEndRef.current) {
                messagesEndRef.current.scrollIntoView({ behavior: 'smooth' });
              }
            }}
          >
            Scroll to Latest
          </button>
        )}
      </div>

      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-64 text-gray-400">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-12 w-12 mb-4 opacity-50" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z" />
          </svg>
          <p>No conversation history yet.</p>
          <p className="text-xs mt-2">Start talking to Coda to see your conversation here.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {groupedMessages.map((group) => (
            <div key={group.date} className="space-y-4">
              <div className="flex items-center justify-center">
                <div className="h-px bg-dark-500 flex-grow"></div>
                <span className="px-4 text-xs text-gray-400">
                  {new Date(group.date).toLocaleDateString([], {
                    weekday: 'long',
                    month: 'long',
                    day: 'numeric'
                  })}
                </span>
                <div className="h-px bg-dark-500 flex-grow"></div>
              </div>

              {group.messages.map((message) => (
                <div
                  key={message.id}
                  className={`p-4 rounded-lg ${
                    message.role === 'user'
                      ? 'bg-dark-600 ml-12 border-l-4 border-blue-500'
                      : 'bg-primary-900/40 mr-12 border-l-4 border-primary-500'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center">
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center mr-2 ${
                        message.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-primary-500 text-white'
                      }`}>
                        {message.role === 'user' ? 'U' : 'C'}
                      </div>
                      <span className="font-medium">
                        {message.role === 'user' ? 'You' : 'Coda'}
                      </span>
                    </div>
                    <span className="text-xs text-gray-400">
                      {formatTimestamp(message.timestamp)}
                    </span>
                  </div>

                  <div className="prose prose-sm prose-invert max-w-none pl-10">
                    <ReactMarkdown
                      components={{
                        code({ node, inline, className, children, ...props }) {
                          const match = /language-(\w+)/.exec(className || '');
                          return !inline && match ? (
                            <SyntaxHighlighter
                              style={vscDarkPlus}
                              language={match[1]}
                              PreTag="div"
                              {...props}
                            >
                              {String(children).replace(/\n$/, '')}
                            </SyntaxHighlighter>
                          ) : (
                            <code className={`${className} bg-dark-800 px-1 py-0.5 rounded text-sm`} {...props}>
                              {children}
                            </code>
                          );
                        }
                      }}
                    >
                      {message.content}
                    </ReactMarkdown>
                  </div>

                  {message.role === 'assistant' && (
                    <div className="flex justify-end mt-2">
                      <button
                        className="text-xs text-gray-400 hover:text-white transition-colors mr-2"
                        onClick={() => navigator.clipboard.writeText(message.content)}
                        title="Copy to clipboard"
                      >
                        Copy
                      </button>
                    </div>
                  )}
                </div>
              ))}
            </div>
          ))}
          <div ref={messagesEndRef} />
        </div>
      )}
    </div>
  );
};

// Use memo to prevent unnecessary re-renders
export default memo(ConversationView);
