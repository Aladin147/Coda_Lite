import React from 'react';
import { useEvents } from '../store/selectors';

const ConversationView: React.FC = () => {
  const { events } = useEvents();
  
  // Filter events to only include conversation-related events
  const conversationEvents = events.filter(event => 
    event.type === 'speech_recognized' || 
    event.type === 'llm_processing_complete' || 
    event.type === 'speaking_start'
  );
  
  return (
    <div className="h-full overflow-y-auto">
      <h2 className="text-xl font-bold mb-4">Conversation</h2>
      
      <div className="space-y-4">
        {conversationEvents.length === 0 ? (
          <p className="text-gray-500 dark:text-gray-400">No conversation yet. Start speaking to Coda!</p>
        ) : (
          conversationEvents.map((event, index) => {
            let content = '';
            let speaker = '';
            
            if (event.type === 'speech_recognized') {
              content = event.text || '';
              speaker = 'You';
            } else if (event.type === 'llm_processing_complete') {
              content = event.output || '';
              speaker = 'Coda';
            } else if (event.type === 'speaking_start') {
              content = event.text || '';
              speaker = 'Coda';
            }
            
            return (
              <div 
                key={`${event.type}-${index}`} 
                className={`p-3 rounded-lg ${
                  speaker === 'You' 
                    ? 'bg-blue-100 dark:bg-blue-900 ml-8' 
                    : 'bg-gray-100 dark:bg-gray-700 mr-8'
                }`}
              >
                <div className="font-semibold mb-1">{speaker}</div>
                <div>{content}</div>
                <div className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {new Date(event.timestamp).toLocaleTimeString()}
                </div>
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

export default ConversationView;
