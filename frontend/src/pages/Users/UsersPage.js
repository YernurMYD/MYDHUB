import React, { useState, useEffect } from 'react';
import './UsersPage.css';

const USERS_KEY = 'myd_users';

const loadUsers = () => {
  try {
    return JSON.parse(localStorage.getItem(USERS_KEY)) || [];
  } catch {
    return [];
  }
};

const saveUsers = (users) => {
  localStorage.setItem(USERS_KEY, JSON.stringify(users));
};

const ROLE_LABELS = {
  client: 'Клиент',
  operator: 'Оператор',
};

const UsersPage = () => {
  const [users, setUsers] = useState(loadUsers);
  const [showModal, setShowModal] = useState(false);
  const [form, setForm] = useState({ name: '', email: '', role: 'client' });
  const [formError, setFormError] = useState('');

  useEffect(() => {
    saveUsers(users);
  }, [users]);

  const handleOpenModal = () => {
    setForm({ name: '', email: '', role: 'client' });
    setFormError('');
    setShowModal(true);
  };

  const handleCloseModal = () => {
    setShowModal(false);
    setFormError('');
  };

  const handleChange = (e) => {
    setForm((prev) => ({ ...prev, [e.target.name]: e.target.value }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();

    if (!form.name.trim()) {
      setFormError('Введите имя');
      return;
    }
    if (!form.email.trim() || !/\S+@\S+\.\S+/.test(form.email)) {
      setFormError('Введите корректный email');
      return;
    }
    if (users.some((u) => u.email.toLowerCase() === form.email.trim().toLowerCase())) {
      setFormError('Пользователь с таким email уже существует');
      return;
    }

    const newUser = {
      id: Date.now().toString(),
      name: form.name.trim(),
      email: form.email.trim(),
      role: form.role,
      createdAt: new Date().toISOString(),
      status: 'active',
    };

    setUsers((prev) => [...prev, newUser]);
    setShowModal(false);
  };

  const handleDelete = (id) => {
    setUsers((prev) => prev.filter((u) => u.id !== id));
  };

  const formatDate = (iso) => {
    try {
      return new Date(iso).toLocaleDateString('ru-RU', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
      });
    } catch {
      return '—';
    }
  };

  return (
    <div className="users-page">
      <div className="users-page__toolbar">
        <span className="users-page__count">{users.length} пользователей</span>
        <button className="users-page__add-btn" onClick={handleOpenModal}>
          + Добавить пользователя
        </button>
      </div>

      {users.length === 0 ? (
        <div className="users-page__empty">
          Нет пользователей. Нажмите «Добавить пользователя» для начала.
        </div>
      ) : (
        <div className="users-page__table-wrapper">
          <table className="users-page__table">
            <thead>
              <tr>
                <th>Имя</th>
                <th>Email</th>
                <th>Роль</th>
                <th>Дата создания</th>
                <th>Статус</th>
                <th>Действия</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.id}>
                  <td className="users-page__name">{user.name}</td>
                  <td>{user.email}</td>
                  <td>
                    <span className={`users-page__role users-page__role--${user.role}`}>
                      {ROLE_LABELS[user.role] || user.role}
                    </span>
                  </td>
                  <td>{formatDate(user.createdAt)}</td>
                  <td>
                    <span className="users-page__status users-page__status--active">
                      Активен
                    </span>
                  </td>
                  <td>
                    <button
                      className="users-page__delete-btn"
                      onClick={() => handleDelete(user.id)}
                      title="Удалить пользователя"
                    >
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {showModal && (
        <div className="users-modal__overlay" onClick={handleCloseModal}>
          <div className="users-modal" onClick={(e) => e.stopPropagation()}>
            <div className="users-modal__header">
              <h2>Добавить пользователя</h2>
              <button className="users-modal__close" onClick={handleCloseModal}>
                &times;
              </button>
            </div>
            <form className="users-modal__form" onSubmit={handleSubmit}>
              {formError && <div className="users-modal__error">{formError}</div>}
              <label className="users-modal__label">
                Имя
                <input
                  type="text"
                  name="name"
                  className="users-modal__input"
                  value={form.name}
                  onChange={handleChange}
                  placeholder="Ерболат Тестов"
                  autoFocus
                />
              </label>
              <label className="users-modal__label">
                Email
                <input
                  type="email"
                  name="email"
                  className="users-modal__input"
                  value={form.email}
                  onChange={handleChange}
                  placeholder="e_testov@example.com"
                />
              </label>
              <label className="users-modal__label">
                Роль
                <select
                  name="role"
                  className="users-modal__select"
                  value={form.role}
                  onChange={handleChange}
                >
                  <option value="client">Клиент</option>
                  <option value="operator">Оператор</option>
                </select>
              </label>
              <div className="users-modal__actions">
                <button type="button" className="users-modal__cancel" onClick={handleCloseModal}>
                  Отмена
                </button>
                <button type="submit" className="users-modal__submit">
                  Добавить
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default UsersPage;
