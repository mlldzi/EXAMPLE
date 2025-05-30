import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSignInAlt, faSpinner, faExclamationCircle } from '@fortawesome/free-solid-svg-icons';

function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!email || !password) {
      setError('Пожалуйста, заполните все поля');
      return;
    }

    try {
      setError('');
      setLoading(true);
      await login(email, password);
      navigate('/dashboard');
    } catch (err) {
      setError('Неверный email или пароль');
      console.error('Login error:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-form-container fade-in">
      <h1>Вход в систему</h1>
      
      {error && (
        <div className="error-message">
          <FontAwesomeIcon icon={faExclamationCircle} /> {error}
        </div>
      )}
      
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="email" className="form-label">Email</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            placeholder="Введите ваш email"
            required
          />
        </div>
        
        <div className="form-group">
          <label htmlFor="password" className="form-label">Пароль</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="Введите ваш пароль"
            required
          />
        </div>
        
        <button 
          type="submit" 
          className="btn btn-primary form-submit" 
          disabled={loading}
        >
          {loading ? (
            <>
              <FontAwesomeIcon icon={faSpinner} spin /> Вход...
            </>
          ) : (
            <>
              <FontAwesomeIcon icon={faSignInAlt} /> Войти
            </>
          )}
        </button>
      </form>
      
      <p className="auth-switch">
        Нет аккаунта? <Link to="/register" className="auth-link">Регистрация</Link>
      </p>
    </div>
  );
}

export default LoginPage; 