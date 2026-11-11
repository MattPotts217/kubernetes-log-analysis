import { useState } from 'react';
import './ShellBar.scss';

export default function ShellBar() {
    
  return (
    <header className="shellbar">
      <div className="shellbar-left">
        <button className="icon-btn" aria-label="Menu">☰</button>
        <span className="shellbar-logo">Log Analysis</span>
        <span className="shellbar-title">Logs</span>
      </div>

      <div className="shellbar-right">
        <button className="icon-btn" aria-label="Notifications">
          🔔 <span className="badge">2</span>
        </button>
        <button className="icon-btn" aria-label="Settings">⚙️</button>
        <div className="avatar">MP</div>
      </div>
    </header>
  );
}
