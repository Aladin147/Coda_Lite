import React from 'react';
import { useConnectionState, useUIState } from '../../store/selectors';

interface LayoutProps {
  children: React.ReactNode;
}

/**
 * Layout component that provides the basic structure for the application
 */
const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { connected } = useConnectionState();
  const { darkMode, toggleDarkMode } = useUIState();
  
  return (
    <div className="min-h-screen bg-background text-text">
      <header className="bg-background-card border-b border-border p-4 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold m-0">Coda Dashboard</h1>
          <div className={`w-2 h-2 rounded-full ${connected ? 'bg-success' : 'bg-danger'}`}></div>
          <span className="text-sm text-text-secondary">
            {connected ? 'Connected' : 'Disconnected'}
          </span>
        </div>
        
        <div className="flex items-center gap-4">
          <button
            onClick={toggleDarkMode}
            className="p-2 rounded-md bg-background-card hover:bg-background text-text-secondary"
          >
            {darkMode ? '☀️' : '🌙'}
          </button>
        </div>
      </header>
      
      <main className="p-4">
        {children}
      </main>
      
      <footer className="bg-background-card border-t border-border p-4 text-center text-text-secondary text-sm">
        Coda Dashboard v2.0 - {new Date().getFullYear()}
      </footer>
    </div>
  );
};

export default Layout;
