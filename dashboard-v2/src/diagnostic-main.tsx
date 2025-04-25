import React from 'react';
import ReactDOM from 'react-dom/client';
import DiagnosticApp from './DiagnosticApp';
import ErrorBoundary from './components/ErrorBoundary';

// Render the diagnostic app
const container = document.getElementById('root');
if (container) {
  const root = ReactDOM.createRoot(container);
  root.render(
    <React.StrictMode>
      <ErrorBoundary>
        <DiagnosticApp />
      </ErrorBoundary>
    </React.StrictMode>
  );
} else {
  console.error('Root element not found');
}
