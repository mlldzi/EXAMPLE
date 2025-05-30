import React from 'react';
import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import SearchPage from './pages/SearchPage';
import TermPage from './pages/TermPage';
import DocumentAnalysisPage from './pages/DocumentAnalysisPage';
import DocumentPage from './pages/DocumentPage';

// Компонент для защиты роутов
const ProtectedRoute = ({ children }) => {
  const { accessToken, loading } = useAuth();
  if (loading) {
    return <div className="loading-animation"><div className="loader"></div><p>Загрузка...</p></div>;
  }
  return accessToken ? children : <Navigate to="/login" replace />;
};

// Компонент для роутов, доступных только неаутентифицированным пользователям
const PublicRoute = ({ children }) => {
  const { accessToken, loading } = useAuth();
  if (loading) {
    return <div className="loading-animation"><div className="loader"></div><p>Загрузка...</p></div>;
  }
  return !accessToken ? children : <Navigate to="/dashboard" replace />;
};

function Navigation() {
  const { accessToken, user, logout } = useAuth();
  const location = useLocation();
  
  return (
    <nav className="main-nav">
      <div className="nav-logo">
        <span className="logo-text">Глоссарий ВНД</span>
      </div>
      <ul>
        <li>
          <Link to="/" className={location.pathname === '/' || location.pathname === '/search' ? 'active' : ''}>
            <i className="fas fa-search"></i> Поиск
          </Link>
        </li>
        <li>
          <Link to="/analyze-document" className={location.pathname === '/analyze-document' ? 'active' : ''}>
            <i className="fas fa-file-alt"></i> Анализ документа
          </Link>
        </li>
        {accessToken ? (
          <>
            <li>
              <Link to="/dashboard" className={location.pathname === '/dashboard' ? 'active' : ''}>
                <i className="fas fa-chart-bar"></i> Панель управления
              </Link>
            </li>
            <li className="user-info">
              <div className="user-avatar">
                {user?.full_name?.[0] || user?.email?.[0] || 'У'}
              </div>
              <span className="user-name">{user?.full_name || user?.email}</span>
              <button onClick={logout} className="logout-btn">
                <i className="fas fa-sign-out-alt"></i>
              </button>
            </li>
          </>
        ) : (
          <>
            <li className="auth-buttons">
              <Link to="/login" className="btn-auth login">Вход</Link>
              <Link to="/register" className="btn-auth register">Регистрация</Link>
            </li>
          </>
        )}
      </ul>
    </nav>
  );
}

function AppContent() {
  return (
    <>
      <Navigation />
      <div className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/search" replace />} />

          <Route path="/search" element={<SearchPage />} />
          <Route path="/term/:termId" element={<TermPage />} />
          <Route path="/document/:docId" element={<DocumentPage />} />
          <Route path="/analyze-document" element={<DocumentAnalysisPage />} />

          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        </Routes>
      </div>
    </>
  );
}

function App() {
  return (
    <AuthProvider>
      <AppContent />
    </AuthProvider>
  );
}

export default App; 