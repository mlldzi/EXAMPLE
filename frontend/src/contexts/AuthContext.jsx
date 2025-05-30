import React, { createContext, useContext, useState, useEffect } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext();

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [accessToken, setAccessToken] = useState(localStorage.getItem('accessToken') || null);
  const [refreshToken, setRefreshToken] = useState(localStorage.getItem('refreshToken') || null);
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshLoading, setRefreshLoading] = useState(false);
  const [failedQueue, setFailedQueue] = useState([]);
  // Состояние для дебаг-режима администратора
  const [debugAdminMode, setDebugAdminMode] = useState(
    localStorage.getItem('debugAdminMode') === 'true' || false
  );

  // Проверяем токены при инициализации
  useEffect(() => {
    // Если токены есть, но они невалидны (например, пустые строки), очистим их
    if (accessToken === '' || refreshToken === '') {
      setAccessToken(null);
      setRefreshToken(null);
      localStorage.removeItem('accessToken');
      localStorage.removeItem('refreshToken');
    }
  }, []);

  const processQueue = (error, token = null) => {
    failedQueue.forEach(prom => {
      if (error) {
        prom.reject(error);
      } else {
        prom.resolve(token);
      }
    });
    setFailedQueue([]);
  };

  const setTokens = (newAccessToken, newRefreshToken) => {
    setAccessToken(newAccessToken);
    setRefreshToken(newRefreshToken);
    if (newAccessToken) {
      localStorage.setItem('accessToken', newAccessToken);
    } else {
      localStorage.removeItem('accessToken');
    }
    if (newRefreshToken) {
      localStorage.setItem('refreshToken', newRefreshToken);
    } else {
      localStorage.removeItem('refreshToken');
    }
  };

  // Функция для включения/выключения режима администратора для отладки
  const toggleDebugAdminMode = () => {
    const newMode = !debugAdminMode;
    setDebugAdminMode(newMode);
    localStorage.setItem('debugAdminMode', newMode);
    
    // Если у нас есть пользователь, то модифицируем его роли
    if (user) {
      setUser(prevUser => {
        const userCopy = { ...prevUser };
        
        // Если включаем режим администратора
        if (newMode) {
          // Добавляем роль ADMIN, если её нет
          if (!userCopy.roles.includes('ADMIN')) {
            userCopy.roles = [...userCopy.roles, 'ADMIN'];
          }
          
          // Оповещение о включении режима администратора
          console.log('🔓 Режим администратора включен. Роли пользователя:', userCopy.roles);
          alert('Режим администратора включен. Теперь вы можете редактировать и утверждать термины.');
          
          // Принудительно обновляем данные пользователя с сервера
          setTimeout(fetchUserData, 500);
        } else {
          // Если выключаем и у пользователя была реальная роль ADMIN, оставляем как есть
          // Иначе, удаляем роль ADMIN, добавленную в режиме отладки
          const originalRoles = JSON.parse(localStorage.getItem('originalUserRoles') || '[]');
          if (!originalRoles.includes('ADMIN')) {
            userCopy.roles = userCopy.roles.filter(role => role !== 'ADMIN');
          }
          
          // Оповещение о выключении режима администратора
          console.log('🔒 Режим администратора выключен. Роли пользователя:', userCopy.roles);
          alert('Режим администратора выключен.');
          
          // Принудительно обновляем данные пользователя с сервера
          setTimeout(fetchUserData, 500);
        }
        
        return userCopy;
      });
    }
  };

  const apiClient = axios.create({
    baseURL: '/api/v1',
    headers: {
      'Content-Type': 'application/json',
    },
  });

  apiClient.interceptors.request.use(
    config => {
      // Первым делом проверяем и добавляем заголовок режима отладки
      if (debugAdminMode) {
        console.log('Отправка заголовка X-Debug-Admin-Mode: true');
        config.headers['X-Debug-Admin-Mode'] = 'true';
      }
    
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      
      // Проверка и исправление URL на случай дублирования /api/v1
      if (config.url && config.url.startsWith('/api/v1')) {
        console.warn('Обнаружено дублирование префикса /api/v1 в URL запроса:', config.url);
        config.url = config.url.replace('/api/v1', '');
      }
      
      return config;
    },
    error => Promise.reject(error)
  );

  apiClient.interceptors.response.use(
    response => response,
    async error => {
      const originalRequest = error.config;
      if (error.response?.status === 401 && refreshToken && !originalRequest._retry) {
        originalRequest._retry = true;
        try {
          setRefreshLoading(true);
          // Создаем отдельный экземпляр axios для запроса обновления токена
          const refreshClient = axios.create({
            baseURL: '/api/v1',
            headers: {
              'Content-Type': 'application/json',
            },
          });
          
          const response = await refreshClient.post('/auth/refresh', {
            refresh_token: refreshToken,
          });

          const { access_token, refresh_token } = response.data;
          
          setTokens(access_token, refresh_token);
          originalRequest.headers.Authorization = `Bearer ${access_token}`;
          processQueue(null, access_token);
          setRefreshLoading(false);
          return apiClient(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          logout();
          return Promise.reject(refreshError);
        } finally {
          setRefreshLoading(false);
        }
      }
      return Promise.reject(error);
    }
  );

  const fetchUserData = async () => {
    if (!accessToken) {
      setLoading(false);
      return;
    }
    
    try {
      const response = await apiClient.get('/users/me');
      const userData = response.data;
      
      // Сохраняем оригинальные роли пользователя для возможности возврата
      localStorage.setItem('originalUserRoles', JSON.stringify(userData.roles || []));
      
      // Если включен режим админа для отладки, добавляем роль ADMIN
      if (debugAdminMode && !userData.roles.includes('ADMIN')) {
        userData.roles = [...userData.roles, 'ADMIN'];
      }
      
      setUser(userData);
    } catch (error) {
      console.error('Error fetching user data:', error);
      if (error.response?.status === 401) {
        logout();
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUserData();
  }, [accessToken]);

  // Периодическое обновление токена
  useEffect(() => {
    // Если нет refresh токена, не пытаемся обновлять
    if (!refreshToken) return;

    // Функция обновления токена
    const refreshAccessToken = async () => {
      try {
        setRefreshLoading(true);
        const refreshClient = axios.create({
          baseURL: '/api/v1',
          headers: {
            'Content-Type': 'application/json',
          },
        });
        
        const response = await refreshClient.post('/auth/refresh', {
          refresh_token: refreshToken,
        });

        const { access_token, refresh_token } = response.data;
        
        if (access_token && refresh_token) {
          setTokens(access_token, refresh_token);
          console.log('Токен доступа успешно обновлен');
        }
      } catch (error) {
        console.error('Ошибка при обновлении токена:', error);
        // Если не удалось обновить токен, выходим из системы
        if (error.response?.status === 401) {
          logout();
        }
      } finally {
        setRefreshLoading(false);
      }
    };

    // Запускаем обновление при монтировании
    refreshAccessToken();

    // Запускаем обновление токена каждые 15 минут
    const intervalId = setInterval(refreshAccessToken, 15 * 60 * 1000);

    // Очистка интервала при размонтировании
    return () => clearInterval(intervalId);
  }, [refreshToken]);

  const login = async (email, password) => {
    setLoading(true);
    try {
      const response = await apiClient.post('/auth/login', {
        email,
        password,
      });
      
      const { access_token, refresh_token } = response.data;
      
      if (!access_token || !refresh_token) {
        throw new Error('Токены авторизации не получены');
      }
      
      setTokens(access_token, refresh_token);
      await fetchUserData();
      
      return response.data;
    } catch (error) {
      console.error('Login error:', error);
      throw error;
    } finally {
      setLoading(false);
    }
  };

  const register = async (userData) => {
    const response = await apiClient.post('/auth/register', userData);
    login(userData.email, userData.password);
    return response.data;
  };

  const logout = () => {
    setAccessToken(null);
    setRefreshToken(null);
    setUser(null);
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('originalUserRoles');
    setFailedQueue([]);
    navigate('/login');
  };

  const value = {
    accessToken,
    refreshToken,
    user,
    loading,
    refreshLoading,
    apiClient,
    login,
    register,
    logout,
    fetchUserData,
    debugAdminMode,
    toggleDebugAdminMode
  };

  return (
    <AuthContext.Provider value={value}>
      {refreshLoading && (
        <div style={{
          position: 'fixed',
          top: 0,
          left: 0,
          right: 0,
          height: '3px',
          background: 'var(--color-accent)',
          zIndex: 9999,
          animation: 'loading 1.5s infinite'
        }} />
      )}
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  return useContext(AuthContext);
};

const style = document.createElement('style');
style.textContent = `
  @keyframes loading {
    0% { width: 0; }
    50% { width: 50%; }
    100% { width: 100%; }
  }
`;
document.head.appendChild(style);   