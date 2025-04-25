import React from 'react';
import ReactDOM from 'react-dom/client';
import MinimalTest from './MinimalTest';
import ErrorBoundary from './components/ErrorBoundary';

// Add console logs to help with debugging
console.log('Starting minimal-main.tsx');

try {
  const rootElement = document.getElementById('root');
  console.log('Root element found:', rootElement);
  
  if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    console.log('Root created');
    
    root.render(
      <React.StrictMode>
        <ErrorBoundary>
          <MinimalTest />
        </ErrorBoundary>
      </React.StrictMode>
    );
    console.log('Render called');
  } else {
    console.error('Root element not found');
  }
} catch (error) {
  console.error('Error in minimal-main.tsx:', error);
}
