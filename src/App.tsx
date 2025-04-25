import { useEffect } from 'react';
import { WebSocketProvider } from './services/WebSocketProvider';
import Layout from './components/Layout';
import Avatar from './components/Avatar';
import { useUIState, useCodaMode } from './store/selectors';

function App() {
  const { darkMode } = useUIState();
  const { setMode, setEmotionContext } = useCodaMode();

  // Set the theme on the document element
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', darkMode ? 'dark' : 'light');
  }, [darkMode]);

  // For testing purposes, let's add some buttons to change the mode and emotion
  const handleModeChange = (mode: 'idle' | 'listening' | 'thinking' | 'speaking' | 'error') => {
    setMode(mode);
  };

  const handleEmotionChange = (emotion: 'neutral' | 'playful' | 'supportive' | 'concerned' | 'witty' | 'focused') => {
    setEmotionContext(emotion);
  };

  return (
    <WebSocketProvider>
      <Layout>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <div className="card p-4">
            <h2 className="text-xl font-bold mb-4">Dashboard 2.0</h2>
            <p className="mb-4">
              Welcome to the new Coda Dashboard! This is a work in progress.
            </p>
            <p>
              The foundation has been set up with:
            </p>
            <ul className="list-disc pl-5 mt-2">
              <li>TypeScript + React</li>
              <li>Tailwind CSS for styling</li>
              <li>Zustand for state management</li>
              <li>WebSocket service for real-time communication</li>
            </ul>
          </div>

          <div className="card p-4">
            <h2 className="text-xl font-bold mb-4">Avatar</h2>
            <Avatar />

            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2">Mode</h3>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => handleModeChange('idle')} className="px-2 py-1 text-sm">Idle</button>
                <button onClick={() => handleModeChange('listening')} className="px-2 py-1 text-sm">Listening</button>
                <button onClick={() => handleModeChange('thinking')} className="px-2 py-1 text-sm">Thinking</button>
                <button onClick={() => handleModeChange('speaking')} className="px-2 py-1 text-sm">Speaking</button>
                <button onClick={() => handleModeChange('error')} className="px-2 py-1 text-sm">Error</button>
              </div>
            </div>

            <div className="mt-4">
              <h3 className="text-lg font-semibold mb-2">Emotion</h3>
              <div className="flex flex-wrap gap-2">
                <button onClick={() => handleEmotionChange('neutral')} className="px-2 py-1 text-sm">Neutral</button>
                <button onClick={() => handleEmotionChange('playful')} className="px-2 py-1 text-sm">Playful</button>
                <button onClick={() => handleEmotionChange('supportive')} className="px-2 py-1 text-sm">Supportive</button>
                <button onClick={() => handleEmotionChange('concerned')} className="px-2 py-1 text-sm">Concerned</button>
                <button onClick={() => handleEmotionChange('witty')} className="px-2 py-1 text-sm">Witty</button>
                <button onClick={() => handleEmotionChange('focused')} className="px-2 py-1 text-sm">Focused</button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </WebSocketProvider>
  );
}

export default App;
