import React from 'react';
import ReactDOM from 'react-dom/client';
import App from './App';
import './styles.css';

// Set default theme to dark mode
const savedTheme = localStorage.getItem('theme');
if (!savedTheme) {
  localStorage.setItem('theme', 'dark');
}
document.documentElement.setAttribute('data-theme', savedTheme || 'dark');

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
);
