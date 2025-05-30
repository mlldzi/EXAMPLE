import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';

function RegisterPage() {
  const [formData, setFormData] = useState({
    email: '',
    password: '',
    full_name: '',
    username: ''
  });
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!formData.email || !formData.password) {
      setError('Email и пароль обязательны');
      return;
    }
    
    if (formData.password.length < 8) {
      setError('Пароль должен содержать не менее 8 символов');
      return;
    }

    try {
      setError('');
      setLoading(true);
      await register(formData);
      navigate('/dashboard');
    } catch (err) {
      const errorMessage = err.response?.data?.detail || 'Ошибка при регистрации';
      setError(Array.isArray(errorMessage) ? errorMessage[0]?.msg || 'Ошибка валидации' : errorMessage);
      console.error('Registration error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-container fade-in">
      <h1>Регистрация</h1>
      
      {error && (
        <div className="error-message">
          <i className="fas fa-exclamation-circle"></i> {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email" className="form-label">Email *</label>
          <input
            type="email"
            id="email"
            name="email"
            value={formData.email}
            onChange={handleChange}
            placeholder="Введите email"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password" className="form-label">Пароль *</label>
          <input
            type="password"
            id="password"
            name="password"
            value={formData.password}
            onChange={handleChange}
            placeholder="Минимум 8 символов"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="username" className="form-label">Имя пользователя</label>
          <input
            type="text"
            id="username"
            name="username"
            value={formData.username}
            onChange={handleChange}
            placeholder="Введите имя пользователя"
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="full_name" className="form-label">Полное имя</label>
          <input
            type="text"
            id="full_name"
            name="full_name"
            value={formData.full_name}
            onChange={handleChange}
            placeholder="Введите полное имя"
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary form-submit" 
          disabled={loading}
        >
          {loading ? (
            <>
              <i className="fas fa-spinner fa-spin"></i> Регистрация...
            </>
          ) : 'Зарегистрироваться'}
        </button>
      </form>
      
      <p className="auth-switch" style={{ marginTop: '1.5rem', textAlign: 'center' }}>
        Уже есть аккаунт? <Link to="/login" style={{ color: 'var(--color-accent)' }}>Войти</Link>
      </p>
    </div>
  );
}

export default RegisterPage; 