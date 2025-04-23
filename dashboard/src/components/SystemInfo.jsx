import { useState, useEffect } from 'react';
import '../styles/SystemInfo.css';

/**
 * SystemInfo component that displays system information in the footer
 * @param {Object} props - Component props
 * @param {Array} props.events - Array of WebSocket events
 */
function SystemInfo({ events }) {
  const [systemInfo, setSystemInfo] = useState({
    version: 'Unknown',
    uptime: '0s',
    memory: '0 MB'
  });
  
  useEffect(() => {
    if (!events || events.length === 0) return;
    
    // Filter for system_info events
    const sysInfoEvents = events.filter(e => e.type === 'system_info');
    if (sysInfoEvents.length === 0) return;
    
    // Get the latest system_info event
    const latest = sysInfoEvents[0];
    
    setSystemInfo({
      version: latest.data?.version || 'Unknown',
      uptime: formatUptime(latest.data?.uptime || 0),
      memory: formatMemory(latest.data?.memory || 0)
    });
  }, [events]);
  
  const formatUptime = (seconds) => {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    return `${hours}h ${minutes}m ${secs}s`;
  };
  
  const formatMemory = (bytes) => {
    const mb = bytes / (1024 * 1024);
    return `${mb.toFixed(1)} MB`;
  };
  
  return (
    <div className="system-info-container">
      <span>Coda v{systemInfo.version}</span>
      <span>Uptime: {systemInfo.uptime}</span>
      <span>Memory: {systemInfo.memory}</span>
    </div>
  );
}

export default SystemInfo;
