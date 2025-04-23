import { useState, useEffect, useRef } from 'react';
import '../styles/ConversationView.css';

/**
 * ConversationView component that displays the conversation between user and Coda
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 */
function ConversationView({ events }) {
  const [messages, setMessages] = useState([]);
  const endOfMessagesRef = useRef(null);
  
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    // Extract conversation messages from events
    const sttResults = events
      .filter(e => e.type === 'stt_result')
      .map(e => ({
        type: 'user',
        text: e.data?.text || '',
        timestamp: e.timestamp
      }));
    
    const llmResults = events
      .filter(e => e.type === 'llm_result')
      .map(e => ({
        type: 'assistant',
        text: e.data?.text || '',
        timestamp: e.timestamp
      }));
    
    // Combine and sort by timestamp
    const allMessages = [...sttResults, ...llmResults];
    allMessages.sort((a, b) => 
      new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    );
    
    setMessages(allMessages);
  }, [events]);
  
  // Scroll to bottom when messages change
  useEffect(() => {
    if (endOfMessagesRef.current) {
      endOfMessagesRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [messages]);
  
  const formatTime = (timestamp) => {
    if (!timestamp) return '';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  };
  
  return (
    <div className="conversation-container">
      <h3 className="conversation-title">Conversation</h3>
      
      <div className="messages">
        {messages.length > 0 ? (
          messages.map((msg, index) => (
            <div key={index} className={`message ${msg.type}`}>
              <div className="message-header">
                <span className="message-sender">{msg.type === 'user' ? 'You' : 'Coda'}</span>
                <span className="message-time">{formatTime(msg.timestamp)}</span>
              </div>
              <div className="message-content">{msg.text}</div>
            </div>
          ))
        ) : (
          <div className="empty-conversation">
            <p>Your conversation with Coda will appear here.</p>
            <p>Use the Push to Talk button to start speaking.</p>
          </div>
        )}
        <div ref={endOfMessagesRef} />
      </div>
    </div>
  );
}

export default ConversationView;
