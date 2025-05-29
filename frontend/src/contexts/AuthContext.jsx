import React, { createContext, useState, useContext, useEffect, useCallback } from 'react';
import axios from 'axios';
import { useNavigate } from 'react-router-dom';

const AuthContext = createContext(null);

export const AuthProvider = ({ children }) => {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [accessToken, setAccessTokenState] = useState(localStorage.getItem('accessToken'));
  const [refreshToken, setRefreshTokenState] = useState(localStorage.getItem('refreshToken'));
  const [loading, setLoading] = useState(true);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [failedQueue, setFailedQueue] = useState([]);

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
    setAccessTokenState(newAccessToken);
    setRefreshTokenState(newRefreshToken);
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

  const apiClient = axios.create({
    baseURL: '/api/v1'
  });

  apiClient.interceptors.request.use(
    config => {
      if (accessToken) {
        config.headers.Authorization = `Bearer ${accessToken}`;
      }
      return config;
    },
    error => Promise.reject(error)
  );

  apiClient.interceptors.response.use(
    response => response,
    async error => {
      const originalRequest = error.config;
      if (error.response?.status === 401 && !originalRequest._retry) {
        if (isRefreshing) {
          return new Promise(function(resolve, reject) {
            setFailedQueue(prev => [...prev, { resolve, reject }])
          })
          .then(token => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch(err => {
            return Promise.reject(err);
          });
        }

        originalRequest._retry = true;
        setIsRefreshing(true);

        const localRefreshToken = localStorage.getItem('refreshToken'); // Получаем самый свежий refresh token
        if (!localRefreshToken) {
          setIsRefreshing(false);
          logout(); // Если нет refresh token, выходим
          return Promise.reject(error);
        }

        try {
          const { data } = await axios.post('/api/v1/auth/refresh', { refresh_token: localRefreshToken });
          setTokens(data.access_token, data.refresh_token); // Обновляем оба токена
          originalRequest.headers.Authorization = `Bearer ${data.access_token}`;
          processQueue(null, data.access_token);
          return apiClient(originalRequest);
        } catch (refreshError) {
          processQueue(refreshError, null);
          logout(); // Если обновление не удалось, выходим
          return Promise.reject(refreshError);
        } finally {
          setIsRefreshing(false);
        }
      }
      return Promise.reject(error);
    }
  );

  const fetchUser = useCallback(async () => {
    if (localStorage.getItem('accessToken')) {
      try {
        const { data } = await apiClient.get('/users/me');
        setUser(data);
      } catch (error) {
        console.error("Failed to fetch user", error);
        // Не вызываем logout() здесь, чтобы дать шанс refresh-логике
      }
    }
    setLoading(false);
  }, [apiClient]);

  useEffect(() => {
    fetchUser();
    // eslint-disable-next-line
  }, []); // Только при монтировании

  const login = async (email, password) => {
    const response = await apiClient.post('/auth/login', { email, password });
    setTokens(response.data.access_token, response.data.refresh_token);
    await fetchUser(); // Загружаем пользователя после логина
    return response.data;
  };

  const register = async (userData) => {
    return await apiClient.post('/auth/register', userData);
  };

  const logout = useCallback(async () => {
    const localRefreshToken = localStorage.getItem('refreshToken');
    if (localRefreshToken) {
      try {
        // Предполагаем, что есть эндпоинт для отзыва токена
        // Если его нет, этот запрос упадет, но logout на клиенте все равно произойдет
        await apiClient.post('/auth/revoke_token', { refresh_token: localRefreshToken });
        console.log("Refresh token revoked");
      } catch (error) {
        console.error("Failed to revoke refresh token", error.response?.data?.detail || error.message);
        // Не блокируем выход пользователя, если отзыв не удался
      }
    }
    setUser(null);
    setTokens(null, null); 
    setFailedQueue([]); 
    navigate('/login'); 
  }, [apiClient, navigate]); 

  return (
    <AuthContext.Provider value={{ user, accessToken, login, register, logout, apiClient, loading }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => useContext(AuthContext);   