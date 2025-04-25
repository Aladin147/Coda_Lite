import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import './index.css';
import App from './App';
import ErrorBoundary from './components/ErrorBoundary';

// Add console logs to help with debugging
console.log('Starting main.tsx');

try {
  const rootElement = document.getElementById('root');
  console.log('Root element found:', rootElement);

  if (rootElement) {
    const root = createRoot(rootElement);
    console.log('Root created');

    root.render(
      <StrictMode>
        <ErrorBoundary>
          <App />
        </ErrorBoundary>
      </StrictMode>
    );
    console.log('Render called');
  } else {
    console.error('Root element not found');
  }
} catch (error) {
  console.error('Error in main.tsx:', error);
}
