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
  const processedEventsRef = useRef(new Set());

  useEffect(() => {
    if (!events || events.length === 0) return;

    // Process only new events to avoid duplicate messages
    const newEvents = events.filter(e => !processedEventsRef.current.has(e.timestamp + e.type));

    if (newEvents.length === 0) return;

    // Mark these events as processed
    newEvents.forEach(e => processedEventsRef.current.add(e.timestamp + e.type));

    // Extract conversation messages from events
    const newUserMessages = newEvents
      .filter(e => e.type === 'stt_result' || e.type === 'user_message')
      .map(e => ({
        type: 'user',
        text: e.data?.text || '',
        timestamp: e.timestamp,
        id: e.timestamp + '-user'
      }));

    const newAssistantMessages = newEvents
      .filter(e => e.type === 'llm_result' || e.type === 'tts_start' || e.type === 'assistant_message')
      .map(e => ({
        type: 'assistant',
        text: e.data?.text || '',
        timestamp: e.timestamp,
        id: e.timestamp + '-assistant'
      }));

    // Add new messages to existing ones
    setMessages(prevMessages => {
      const updatedMessages = [...prevMessages, ...newUserMessages, ...newAssistantMessages];

      // Sort by timestamp
      updatedMessages.sort((a, b) =>
        new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
      );

      // Remove duplicates (by id)
      const uniqueMessages = [];
      const messageIds = new Set();

      for (const message of updatedMessages) {
        if (!messageIds.has(message.id)) {
          messageIds.add(message.id);
          uniqueMessages.push(message);
        }
      }

      return uniqueMessages;
    });

    // Log for debugging
    if (newUserMessages.length > 0 || newAssistantMessages.length > 0) {
      console.log('Added new messages:', {
        user: newUserMessages.length,
        assistant: newAssistantMessages.length,
        total: messages.length + newUserMessages.length + newAssistantMessages.length
      });
    }
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
      <div className="section-header">
        <h3 className="section-title">Conversation</h3>
      </div>

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
