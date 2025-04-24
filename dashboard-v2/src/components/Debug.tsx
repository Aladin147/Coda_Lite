import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useCodaMode, useConnectionState } from '../store/selectors';

const Debug: React.FC = () => {
  const [cssVariables, setCssVariables] = useState<Record<string, string>>({});
  const [tailwindVersion, setTailwindVersion] = useState<string>('Unknown');
  const { mode, emotionContext } = useCodaMode();
  const { connected } = useConnectionState();

  // Use a ref to track if we've already loaded the CSS variables
  const hasLoadedCssVars = useRef(false);

  // Get CSS variables from root element - only run once
  useEffect(() => {
    // Skip if we've already loaded the variables
    if (hasLoadedCssVars.current) return;

    // Mark as loaded to prevent future runs
    hasLoadedCssVars.current = true;

    const rootStyles = getComputedStyle(document.documentElement);
    const variables: Record<string, string> = {};

    // Get all CSS variables
    for (let i = 0; i < rootStyles.length; i++) {
      const prop = rootStyles[i];
      if (prop.startsWith('--')) {
        variables[prop] = rootStyles.getPropertyValue(prop);
      }
    }

    setCssVariables(variables);

    // Try to get Tailwind version
    try {
      // This is a hack to try to get the Tailwind version
      const tailwindScript = document.querySelector('script[src*="tailwind"]');
      if (tailwindScript) {
        setTailwindVersion(tailwindScript.getAttribute('src') || 'Found but version unknown');
      } else {
        setTailwindVersion('Not found in DOM');
      }
    } catch (error) {
      setTailwindVersion(`Error: ${error}`);
    }
  }, []);

  return (
    <div style={{
      position: 'fixed',
      top: 0,
      left: 0,
      right: 0,
      bottom: 0,
      backgroundColor: 'white',
      color: 'black',
      padding: '20px',
      zIndex: 9999,
      display: 'flex',
      flexDirection: 'column',
      alignItems: 'flex-start',
      overflowY: 'auto',
      fontFamily: 'monospace'
    }}>
      <h1 style={{ fontSize: '24px', marginBottom: '20px', alignSelf: 'center' }}>Debug Screen</h1>
      <p style={{ alignSelf: 'center' }}>If you can see this, React is rendering correctly.</p>
      <p style={{ alignSelf: 'center' }}>Press Ctrl+Shift+D to toggle this debug screen.</p>

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px', width: '100%' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '10px' }}>Environment Info</h2>
        <p>Browser: {navigator.userAgent}</p>
        <p>Screen size: {window.innerWidth}x{window.innerHeight}</p>
        <p>Time: {new Date().toLocaleTimeString()}</p>
        <p>Tailwind version: {tailwindVersion}</p>
        <p>Connected: {connected ? 'Yes' : 'No'}</p>
        <p>Mode: {mode}</p>
        <p>Emotion: {emotionContext}</p>
      </div>

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px', width: '100%' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '10px' }}>CSS Variables</h2>
        <div style={{ maxHeight: '300px', overflowY: 'auto' }}>
          {Object.entries(cssVariables).map(([key, value]) => (
            <div key={key} style={{ display: 'flex', marginBottom: '5px' }}>
              <span style={{ fontWeight: 'bold', marginRight: '10px', minWidth: '200px' }}>{key}:</span>
              <span>{value}</span>
            </div>
          ))}
        </div>
      </div>

      <div style={{ marginTop: '20px', padding: '10px', backgroundColor: '#f0f0f0', borderRadius: '5px', width: '100%' }}>
        <h2 style={{ fontSize: '18px', marginBottom: '10px' }}>Test Tailwind Classes</h2>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '10px' }}>
          <div className="bg-blue-500 text-white p-2 rounded">bg-blue-500</div>
          <div className="bg-red-500 text-white p-2 rounded">bg-red-500</div>
          <div className="bg-green-500 text-white p-2 rounded">bg-green-500</div>
          <div className="bg-yellow-500 text-black p-2 rounded">bg-yellow-500</div>
          <div className="bg-purple-500 text-white p-2 rounded">bg-purple-500</div>
        </div>
      </div>
    </div>
  );
};

export default Debug;
