import React from 'react';
import { Routes, Route, Navigate, Link } from 'react-router-dom';
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
    return <div>Загрузка...</div>; // Или спиннер
  }
  return accessToken ? children : <Navigate to="/login" replace />;
};

// Компонент для роутов, доступных только неаутентифицированным пользователям
const PublicRoute = ({ children }) => {
  const { accessToken, loading } = useAuth();
  if (loading) {
    return <div>Загрузка...</div>;
  }
  return !accessToken ? children : <Navigate to="/dashboard" replace />;
};

function Navigation() {
  const { accessToken, user, logout } = useAuth();
  return (
    <nav>
      <ul>
        <li><Link to="/">Главная</Link></li>
        <li><Link to="/analyze-document">Анализ документа</Link></li>
        {accessToken ? (
          <>
            <li><Link to="/dashboard">Панель управления</Link></li>
            <li><em>{user ? `Привет, ${user.full_name || user.email}!` : ''}</em></li>
            <li><button onClick={logout} style={{background: 'none', border: 'none', color: 'white', cursor: 'pointer', padding: 0, textDecoration: 'underline'}}>Выйти</button></li>
          </>
        ) : (
          <>
            <li><Link to="/login">Вход</Link></li>
            <li><Link to="/register">Регистрация</Link></li>
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