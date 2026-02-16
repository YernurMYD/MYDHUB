import React, { useState, useEffect, useCallback } from 'react';
import { getStatistics } from '../../services/api';
import { formatLastSeen } from '../../utils/formatters';
import './DevicesPage.css';

const ROUTERS_KEY = 'myd_routers';

const DEFAULT_ROUTER = {
  id: 'router-default',
  name: 'Роутер 1 (Основной)',
  ip: '192.168.1.1',
  location: 'Не задана',
  mqttTopic: 'wifi/probes',
  isPrimary: true,
};

const loadRouters = () => {
  try {
    const stored = JSON.parse(localStorage.getItem(ROUTERS_KEY));
    if (stored && stored.length > 0) return stored;
    return [DEFAULT_ROUTER];
  } catch {
    return [DEFAULT_ROUTER];
  }
};

const saveRouters = (routers) => {
  localStorage.setItem(ROUTERS_KEY, JSON.stringify(routers));
};

const DevicesPage = () => {
  const [routers, setRouters] = useState(loadRouters);
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [editingRouter, setEditingRouter] = useState(null);
  const [form, setForm] = useState({ name: '', ip: '', location: '', mqttTopic: '' });
  const [formError, setFormError] = useState('');

  const fetchStats = useCallback(async () => {
    try {
      const data = await getStatistics();
      setStats(data);
    } catch (err) {
      console.warn('Failed to fetch statistics:', err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchStats();
    const intervalId = setInterval(fetchStats, 60000);
    return () => clearInterval(intervalId);
  }, [fetchStats]);

  useEffect(() => {
    saveRouters(routers);
  }, [routers]);

  const getRouterStatus = (router) => {
    if (!router.isPrimary || !stats) return 'unknown';
    const lastMsg = stats.last_message_time;
    if (!lastMsg) return 'offline';
    const diffMs = Date.now() - lastMsg * 1000;
    return diffMs < 15 * 60 * 1000 ? 'online' : 'offline';
  };

  const getRouterLastSeen = (router) => {
    if (!router.isPrimary || !stats) return null;
    return stats.last_message_time || null;
  };

  const getRouterDevicesCount = (router) => {
    if (!router.isPrimary || !stats) return '—';
    return stats.current_devices ?? stats.total_devices ?? '—';
  };

  const handleOpenAdd = () => {
    setEditingRouter(null);
    setForm({ name: '', ip: '', location: '', mqttTopic: 'wifi/probes' });
    setFormError('');
    setShowModal(true);
  };

  const handleOpenEdit = (router) => {
    setEditingRouter(router);
    setForm({
      name: router.name,
      ip: router.ip || '',
      location: router.location || '',
      mqttTopic: router.mqttTopic || 'wifi/probes',
    });
    setFormError('');
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setEditingRouter(null);
    setFormError('');
  };

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    if (!form.name.trim()) {
      setFormError('Введите название роутера');
      return;
    }

    if (editingRouter) {
      setRouters((prev) =>
        prev.map((r) =>
          r.id === editingRouter.id
            ? { ...r, name: form.name.trim(), ip: form.ip.trim(), location: form.location.trim(), mqttTopic: form.mqttTopic.trim() }
            : r
        )
      );
    } else {
      const newRouter = {
        id: `router-${Date.now()}`,
        name: form.name.trim(),
        ip: form.ip.trim(),
        location: form.location.trim() || 'Не задана',
        mqttTopic: form.mqttTopic.trim() || 'wifi/probes',
        isPrimary: false,
      };
      setRouters((prev) => [...prev, newRouter]);
    }
    setShowModal(false);
    setEditingRouter(null);
  };

  const handleDelete = (id) => {
    setRouters((prev) => prev.filter((r) => r.id !== id));
  };

  const statusLabel = (status) => {
    switch (status) {
      case 'online': return 'Онлайн';
      case 'offline': return 'Офлайн';
      default: return 'Ожидание';
    }
  };

  return (
    <div className="devices-page">
      <div className="devices-page__toolbar">
        <div className="devices-page__stats">
          <span className="devices-page__count">{routers.length} роутеров</span>
          <span className="devices-page__online">
            {routers.filter((r) => getRouterStatus(r) === 'online').length} онлайн
          </span>
        </div>
        <button className="devices-page__add-btn" onClick={handleOpenAdd}>
          + Добавить роутер
        </button>
      </div>

      {loading && !stats ? (
        <div className="devices-page__loading">Загрузка данных...</div>
      ) : routers.length === 0 ? (
        <div className="devices-page__empty">Нет роутеров. Добавьте первый роутер.</div>
      ) : (
        <div className="devices-page__cards">
          {routers.map((router) => {
            const status = getRouterStatus(router);
            const lastSeen = getRouterLastSeen(router);
            const devicesCount = getRouterDevicesCount(router);

            return (
              <div key={router.id} className="router-card">
                <div className="router-card__header">
                  <div className="router-card__name-row">
                    <div className={`router-card__indicator router-card__indicator--${status}`} />
                    <h3 className="router-card__name">{router.name}</h3>
                  </div>
                  <div className="router-card__actions">
                    <button className="router-card__edit-btn" onClick={() => handleOpenEdit(router)} title="Редактировать">
                      <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
                        <path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7" />
                        <path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z" />
                      </svg>
                    </button>
                    {!router.isPrimary && (
                      <button className="router-card__delete-btn" onClick={() => handleDelete(router.id)} title="Удалить">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" width="16" height="16">
                          <polyline points="3 6 5 6 21 6" />
                          <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2" />
                        </svg>
                      </button>
                    )}
                  </div>
                </div>

                <div className="router-card__body">
                  <div className="router-card__field">
                    <span className="router-card__label">IP адрес</span>
                    <span className="router-card__value">{router.ip || '—'}</span>
                  </div>
                  <div className="router-card__field">
                    <span className="router-card__label">Локация</span>
                    <span className="router-card__value">{router.location || '—'}</span>
                  </div>
                  <div className="router-card__field">
                    <span className="router-card__label">MQTT топик</span>
                    <span className="router-card__value router-card__value--mono">{router.mqttTopic}</span>
                  </div>
                  <div className="router-card__field">
                    <span className="router-card__label">Состояние</span>
                    <span className={`router-card__status router-card__status--${status}`}>
                      {statusLabel(status)}
                    </span>
                  </div>
                  <div className="router-card__field">
                    <span className="router-card__label">Последние данные</span>
                    <span className="router-card__value">
                      {lastSeen ? formatLastSeen(lastSeen) : '—'}
                    </span>
                  </div>
                  <div className="router-card__field">
                    <span className="router-card__label">Устройств обнаружено</span>
                    <span className="router-card__value router-card__value--bold">{devicesCount}</span>
                  </div>
                </div>

                {router.isPrimary && (
                  <div className="router-card__badge">Основной</div>
                )}
              </div>
            );
          })}
        </div>
      )}

      {showModal && (
        <div className="router-modal__overlay" onClick={handleCloseModal}>
          <div className="router-modal" onClick={(e) => e.stopPropagation()}>
            <div className="router-modal__header">
              <h2>{editingRouter ? 'Редактировать роутер' : 'Добавить роутер'}</h2>
              <button className="router-modal__close" onClick={handleCloseModal}>&times;</button>
            </div>
            <form className="router-modal__form" onSubmit={handleSubmit}>
              {formError && <div className="router-modal__error">{formError}</div>}
              <label className="router-modal__label">
                Название
                <input
                  type="text"
                  name="name"
                  className="router-modal__input"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Например: Роутер 2 (Склад)"
                  autoFocus
                />
              </label>
              <label className="router-modal__label">
                IP адрес
                <input
                  type="text"
                  name="ip"
                  className="router-modal__input"
                  value={form.ip}
                  onChange={handleChange}
                  placeholder="192.168.1.1"
                />
              </label>
              <label className="router-modal__label">
                Локация
                <input
                  type="text"
                  name="location"
                  className="router-modal__input"
                  value={form.location}
                  onChange={handleChange}
                  placeholder="Главный офис, 2 этаж"
                />
              </label>
              <label className="router-modal__label">
                MQTT топик
                <input
                  type="text"
                  name="mqttTopic"
                  className="router-modal__input"
                  value={form.mqttTopic}
                  onChange={handleChange}
                  placeholder="wifi/probes"
                />
              </label>
              <div className="router-modal__actions">
                <button type="button" className="router-modal__cancel" onClick={handleCloseModal}>Отмена</button>
                <button type="submit" className="router-modal__submit">
                  {editingRouter ? 'Сохранить' : 'Добавить'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default DevicesPage;
