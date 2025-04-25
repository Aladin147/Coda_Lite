import React from 'react';
import ReactDOM from 'react-dom/client';
import MinimalTest from './MinimalTest';

// Add console logs to help with debugging
console.log('Starting minimal-test-main.tsx');

try {
  const rootElement = document.getElementById('root');
  console.log('Root element found:', rootElement);
  
  if (rootElement) {
    const root = ReactDOM.createRoot(rootElement);
    console.log('Root created');
    
    root.render(
      <React.StrictMode>
        <MinimalTest />
      </React.StrictMode>
    );
    console.log('Render called');
  } else {
    console.error('Root element not found');
  }
} catch (error) {
  console.error('Error in minimal-test-main.tsx:', error);
}
