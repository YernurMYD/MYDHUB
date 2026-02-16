import React, { useState, useRef, useEffect } from 'react';
import { Outlet, useLocation } from 'react-router-dom';
import Sidebar from '../Sidebar/Sidebar';
import './Layout.css';

const PAGE_TITLES = {
  '/dashboard': 'Дэшборд',
  '/devices': 'WiFi Роутеры',
  '/users': 'Пользователи',
  '/settings': 'Настройки',
};

const Layout = () => {
  const location = useLocation();
  const pageTitle = PAGE_TITLES[location.pathname] || 'MYDhub';
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    setDropdownOpen(false);
    // TODO: логика выхода (очистка токена, редирект и т.д.)
    window.location.href = '/';
  };

  return (
    <div className="layout">
      <Sidebar />
      <div className="layout__content">
        <header className="layout__header">
          <div className="layout__header-left">
            <h1 className="layout__header-title">{pageTitle}</h1>
            <div className="layout__header-subtitle">Wi-Fi Analytics Platform</div>
          </div>

          <div className="layout__header-user" ref={dropdownRef}>
            <button
              className="layout__user-btn"
              onClick={() => setDropdownOpen((prev) => !prev)}
            >
              <span className="layout__user-name">Администратор</span>
              <div className="layout__user-avatar">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round">
                  <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2" />
                  <circle cx="12" cy="7" r="4" />
                </svg>
              </div>
            </button>

            {dropdownOpen && (
              <div className="layout__user-dropdown">
                <div className="layout__dropdown-info">
                  <span className="layout__dropdown-name">Администратор</span>
                  <span className="layout__dropdown-role">Оператор</span>
                </div>
                <div className="layout__dropdown-divider" />
                <button className="layout__dropdown-item" onClick={handleLogout}>
                  <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
                    <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4" />
                    <polyline points="16 17 21 12 16 7" />
                    <line x1="21" y1="12" x2="9" y2="12" />
                  </svg>
                  Выйти
                </button>
              </div>
            )}
          </div>
        </header>
        <main className="layout__main">
          <Outlet />
        </main>
      </div>
    </div>
  );
};

export default Layout;
