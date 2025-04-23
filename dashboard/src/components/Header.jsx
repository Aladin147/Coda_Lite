import React from 'react';

function Header({ connected, activeTab, onTabChange }) {
  return (
    <header className="header">
      <div className="header-title">
        <h1>Coda Dashboard</h1>
        <div className="connection-status">
          <div className={`status-indicator ${connected ? 'status-connected' : 'status-disconnected'}`}></div>
          <span>{connected ? 'Connected' : 'Disconnected'}</span>
        </div>
      </div>
      
      <div className="tabs">
        <div 
          className={`tab ${activeTab === 'dashboard' ? 'active' : ''}`}
          onClick={() => onTabChange('dashboard')}
        >
          Dashboard
        </div>
        <div 
          className={`tab ${activeTab === 'events' ? 'active' : ''}`}
          onClick={() => onTabChange('events')}
        >
          Events
        </div>
        <div 
          className={`tab ${activeTab === 'performance' ? 'active' : ''}`}
          onClick={() => onTabChange('performance')}
        >
          Performance
        </div>
        <div 
          className={`tab ${activeTab === 'memory' ? 'active' : ''}`}
          onClick={() => onTabChange('memory')}
        >
          Memory
        </div>
      </div>
    </header>
  );
}

export default Header;
