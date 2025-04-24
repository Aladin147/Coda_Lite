import React from 'react';

interface LayoutProps {
  children: React.ReactNode;
}

const Layout: React.FC<LayoutProps> = ({ children }) => {
  return (
    <div className="min-h-screen bg-dark-800 text-white">
      <header className="bg-dark-700 border-b border-dark-600 py-4">
        <div className="container mx-auto px-4">
          <div className="flex justify-between items-center">
            <h1 className="text-2xl font-bold text-primary-400">Coda Dashboard</h1>
            <div className="flex items-center space-x-4">
              <span className="text-sm text-gray-400">v3.0</span>
            </div>
          </div>
        </div>
      </header>
      
      <main className="container mx-auto px-4 py-6">
        {children}
      </main>
      
      <footer className="bg-dark-700 border-t border-dark-600 py-3 mt-auto">
        <div className="container mx-auto px-4">
          <div className="text-center text-sm text-gray-400">
            Coda Dashboard &copy; {new Date().getFullYear()}
          </div>
        </div>
      </footer>
    </div>
  );
};

export default Layout;
