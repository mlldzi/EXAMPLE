import axios from 'axios';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const apiClient = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Добавьте перехватчики запросов или ответов здесь при необходимости
// Например, для добавления токена аутентификации:
/*
apiClient.interceptors.request.use(
  config => {
    const token = localStorage.getItem('accessToken'); // Или из контекста аутентификации
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`;
    }
    return config;
  },
  error => {
    return Promise.reject(error);
  }
);
*/

export default apiClient; 