import React from 'react';
import ThemeToggle from './ThemeToggle';

function Header({ connected }) {
  return (
    <header className="header">
      <div className="header-title">
        <h1>Coda Dashboard</h1>
        <div className="connection-status">
          <div className={`status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`}></div>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>

      <div className="header-controls">
        <ThemeToggle />
      </div>
    </header>
  );
}

export default Header;
