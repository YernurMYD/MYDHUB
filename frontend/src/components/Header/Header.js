import React from 'react';
import './Header.css';

const Header = () => {
  return (
    <header className="dashboard-header">
      <div className="header-content">
        <h1 className="header-title">MYD Production Wi-Fi Analytics Dashboard</h1>
        <div className="header-subtitle">Real-time Network Monitoring</div>
      </div>
    </header>
  );
};

export default Header;
