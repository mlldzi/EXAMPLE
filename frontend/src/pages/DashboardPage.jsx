import React from 'react';
import { useAuth } from '../contexts/AuthContext';

function DashboardPage() {
  const { user, logout } = useAuth();

  if (!user) {
    return <p>Загрузка данных пользователя...</p>;
  }

  return (
    <div>
      <h2>Панель управления</h2>
      <p>Добро пожаловать, {user.full_name || user.email}!</p>
      <p>Это защищенная страница.</p>
      <p><strong>ID пользователя:</strong> {user.id}</p>
      <p><strong>Email:</strong> {user.email}</p>
      <p><strong>Username:</strong> {user.username}</p>
      <p><strong>Роли:</strong> {user.roles.join(', ')}</p>
      <p><strong>Статус:</strong> {user.status}</p>
      <p><strong>Активен:</strong> {user.is_active ? 'Да' : 'Нет'}</p>
      <p><strong>Зарегистрирован:</strong> {new Date(user.created_at).toLocaleString()}</p>
      
      <button onClick={logout} style={{marginTop: '20px', backgroundColor: '#d9534f'}}>
        Выйти
      </button>
    </div>
  );
}

export default DashboardPage; 