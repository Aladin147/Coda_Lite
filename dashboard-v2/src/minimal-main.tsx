import React from 'react';
import ReactDOM from 'react-dom/client';
import MinimalApp from './MinimalApp';

// Render the minimal app
const container = document.getElementById('root');
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <MinimalApp />
    </React.StrictMode>
  );
} else {
  console.error('Root element not found');
}
