import React, { useState } from 'react';
import ErrorBoundary from './components/ErrorBoundary';

// A very simple component to test rendering
const SimpleComponent: React.FC = () => {
  return (
    <div style={{
      backgroundColor: '#121212',
      color: 'white',
      padding: '20px',
      fontFamily: 'system-ui, sans-serif',
      minHeight: '100vh'
    }}>
      <h1>Diagnostic App</h1>
      <p>If you can see this, basic rendering is working.</p>
      
      <div style={{
        backgroundColor: '#1e1e1e',
        padding: '15px',
        borderRadius: '8px',
        marginTop: '20px'
      }}>
        <h2>Test Card</h2>
        <p>This is a test card to see if basic styling works.</p>
        <button 
          style={{
            backgroundColor: '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            cursor: 'pointer',
            marginTop: '10px'
          }}
          onClick={() => alert('Button clicked!')}
        >
          Test Button
        </button>
      </div>
      
      <div style={{
        marginTop: '20px',
        display: 'flex',
        gap: '20px'
      }}>
        <div style={{
          backgroundColor: '#1e1e1e',
          padding: '15px',
          borderRadius: '8px',
          flex: 1
        }}>
          <h2>Card 1</h2>
          <p>This is a test card.</p>
        </div>
        
        <div style={{
          backgroundColor: '#1e1e1e',
          padding: '15px',
          borderRadius: '8px',
          flex: 1
        }}>
          <h2>Card 2</h2>
          <p>This is another test card.</p>
        </div>
      </div>
    </div>
  );
};

// Component that might cause errors
const PotentiallyProblematicComponent: React.FC = () => {
  // This will throw an error if uncommented
  // throw new Error('Test error');
  
  return (
    <div style={{ marginTop: '20px', padding: '15px', backgroundColor: '#1e1e1e', borderRadius: '8px' }}>
      <h2>Potentially Problematic Component</h2>
      <p>If you can see this, this component is rendering without errors.</p>
    </div>
  );
};

// Main diagnostic app
const DiagnosticApp: React.FC = () => {
  const [showProblematic, setShowProblematic] = useState(false);
  
  return (
    <ErrorBoundary>
      <SimpleComponent />
      
      <div style={{ padding: '20px' }}>
        <button
          style={{
            backgroundColor: showProblematic ? '#ef4444' : '#3b82f6',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            padding: '8px 16px',
            cursor: 'pointer'
          }}
          onClick={() => setShowProblematic(!showProblematic)}
        >
          {showProblematic ? 'Hide' : 'Show'} Potentially Problematic Component
        </button>
        
        {showProblematic && (
          <ErrorBoundary>
            <PotentiallyProblematicComponent />
          </ErrorBoundary>
        )}
      </div>
    </ErrorBoundary>
  );
};

export default DiagnosticApp;
