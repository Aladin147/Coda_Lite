import React, { useMemo } from 'react';
import { useConnectionState } from '../store/selectors';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  const { connected } = useConnectionState();

  // Memoize the connection indicator color to prevent unnecessary re-renders
  const connectionColor = useMemo(() => {
    return connected ? 'var(--color-success-500)' : 'var(--color-danger-500)';
  }, [connected]);

  // Memoize the connection status text
  const connectionText = useMemo(() => {
    return connected ? 'Connected' : 'Disconnected';
  }, [connected]);

  return (
    <div className="min-h-screen" style={{ backgroundColor: 'var(--background-color)' }}>
      <header className="shadow" style={{ backgroundColor: 'var(--card-background)' }}>
        <div className="max-w-7xl mx-auto px-4 py-4 flex justify-between items-center">
          <h1 className="text-2xl font-bold" style={{ color: 'var(--text-color)' }}>Coda Dashboard</h1>
          <div className="flex items-center">
            <div className="flex items-center mr-4">
              <span className="mr-2 text-sm" style={{ color: 'var(--text-color)' }}>Connection:</span>
              <span
                className="inline-block w-3 h-3 rounded-full"
                style={{ backgroundColor: connectionColor }}
              ></span>
              <span className="ml-2 text-sm" style={{ color: 'var(--text-color)' }}>
                {connectionText}
              </span>
            </div>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-6">
        {children}
      </main>

      <footer className="shadow-inner" style={{ backgroundColor: 'var(--card-background)' }}>
        <div className="max-w-7xl mx-auto px-4 py-4">
          <div className="text-center text-sm" style={{ color: 'var(--text-color)' }}>
            Coda Dashboard - © {new Date().getFullYear()}
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
