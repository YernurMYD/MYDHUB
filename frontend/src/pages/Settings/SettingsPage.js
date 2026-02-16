import React, { useState, useEffect } from 'react';
import './SettingsPage.css';

const SETTINGS_KEY = 'myd_settings';

const DEFAULT_SETTINGS = {
  systemName: 'MYD Wi-Fi Analytics',
  refreshInterval: '10',
  notificationsEnabled: false,
  notificationEmail: '',
  theme: 'light',
  language: 'ru',
};

const loadSettings = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(SETTINGS_KEY));
    return { ...DEFAULT_SETTINGS, ...stored };
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
};

const SettingsPage = () => {
  const [settings, setSettings] = useState(loadSettings);
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    if (saved) {
      const timer = setTimeout(() => setSaved(false), 3000);
      return () => clearTimeout(timer);
    }
  }, [saved]);

  const handleChange = (field, value) => {
    setSettings((prev) => ({ ...prev, [field]: value }));
    setSaved(false);
  };

  const handleToggle = (field) => {
    setSettings((prev) => ({ ...prev, [field]: !prev[field] }));
    setSaved(false);
  };

  const handleSave = () => {
    localStorage.setItem(SETTINGS_KEY, JSON.stringify(settings));
    setSaved(true);
  };

  const handleReset = () => {
    setSettings({ ...DEFAULT_SETTINGS });
    localStorage.removeItem(SETTINGS_KEY);
    setSaved(false);
  };

  return (
    <div className="settings-page">
      {/* Общие */}
      <section className="settings-page__section">
        <h2 className="settings-page__section-title">Общие</h2>
        <div className="settings-page__field">
          <label className="settings-page__label">Название системы</label>
          <input
            type="text"
            className="settings-page__input"
            value={settings.systemName}
            onChange={(e) => handleChange('systemName', e.target.value)}
          />
        </div>
        <div className="settings-page__field">
          <label className="settings-page__label">Интервал обновления данных</label>
          <select
            className="settings-page__select"
            value={settings.refreshInterval}
            onChange={(e) => handleChange('refreshInterval', e.target.value)}
          >
            <option value="1">1 минута</option>
            <option value="5">5 минут</option>
            <option value="10">10 минут</option>
            <option value="30">30 минут</option>
          </select>
        </div>
      </section>

      {/* Уведомления */}
      <section className="settings-page__section">
        <h2 className="settings-page__section-title">Уведомления</h2>
        <div className="settings-page__field settings-page__field--row">
          <label className="settings-page__label">Включить уведомления</label>
          <button
            type="button"
            className={`settings-page__toggle ${settings.notificationsEnabled ? 'settings-page__toggle--on' : ''}`}
            onClick={() => handleToggle('notificationsEnabled')}
            role="switch"
            aria-checked={settings.notificationsEnabled}
          >
            <span className="settings-page__toggle-knob" />
          </button>
        </div>
        {settings.notificationsEnabled && (
          <div className="settings-page__field">
            <label className="settings-page__label">Email для уведомлений</label>
            <input
              type="email"
              className="settings-page__input"
              value={settings.notificationEmail}
              onChange={(e) => handleChange('notificationEmail', e.target.value)}
              placeholder="admin@example.com"
            />
          </div>
        )}
      </section>

      {/* Отображение */}
      <section className="settings-page__section">
        <h2 className="settings-page__section-title">Отображение</h2>
        <div className="settings-page__field">
          <label className="settings-page__label">Тема</label>
          <select
            className="settings-page__select"
            value={settings.theme}
            onChange={(e) => handleChange('theme', e.target.value)}
          >
            <option value="light">Светлая</option>
            <option value="dark">Тёмная (скоро)</option>
          </select>
        </div>
        <div className="settings-page__field">
          <label className="settings-page__label">Язык</label>
          <select
            className="settings-page__select"
            value={settings.language}
            onChange={(e) => handleChange('language', e.target.value)}
          >
            <option value="ru">Русский</option>
            <option value="en">English (скоро)</option>
          </select>
        </div>
      </section>

      {/* Действия */}
      <div className="settings-page__actions">
        <button className="settings-page__reset-btn" onClick={handleReset}>
          Сбросить
        </button>
        <button className="settings-page__save-btn" onClick={handleSave}>
          Сохранить
        </button>
      </div>

      {saved && (
        <div className="settings-page__saved-toast">
          Настройки сохранены
        </div>
      )}
    </div>
  );
};

export default SettingsPage;
