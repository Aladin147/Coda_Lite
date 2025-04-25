import React from 'react';
import ReactDOM from 'react-dom/client';

// Minimal React component
const MinimalApp: React.FC = () => {
  return (
    <div style={{
      fontFamily: 'system-ui, sans-serif',
      maxWidth: '800px',
      margin: '0 auto',
      padding: '20px',
      backgroundColor: 'white',
      borderRadius: '8px',
      boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
      color: '#333'
    }}>
      <h1 style={{ color: '#2563eb' }}>Minimal React App</h1>
      <p>This is a minimal React app to test if React is working correctly.</p>
      
      <div style={{
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '16px',
        marginTop: '16px'
      }}>
        <h2>Test Card</h2>
        <p>If you can see this card with styling, then React is working.</p>
        <button 
          style={{
            backgroundColor: '#2563eb',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            cursor: 'pointer'
          }}
          onClick={() => alert('Button clicked!')}
        >
          Test Button
        </button>
      </div>
      
      <div style={{
        border: '1px solid #e5e7eb',
        borderRadius: '8px',
        padding: '16px',
        marginTop: '16px'
      }}>
        <h2>Browser Information</h2>
        <p>User Agent: {navigator.userAgent}</p>
        <p>Screen Size: {window.innerWidth}x{window.innerHeight}</p>
        <p>Time: {new Date().toLocaleTimeString()}</p>
      </div>
    </div>
  );
};

// Create a new entry point for the minimal app
export function renderMinimalApp() {
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
}

export default MinimalApp;
