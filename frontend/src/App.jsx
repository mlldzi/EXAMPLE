import React, { useState } from 'react';
import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom';
import { AuthProvider, useAuth } from './contexts/AuthContext';
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import DashboardPage from './pages/DashboardPage';
import SearchPage from './pages/SearchPage';
import TermPage from './pages/TermPage';
import DocumentAnalysisPage from './pages/DocumentAnalysisPage';
import DocumentPage from './pages/DocumentPage';
import TermsListPage from './pages/TermsListPage';
import DocumentsListPage from './pages/DocumentsListPage';
import Modal from './components/Modal';
import CreateTermForm from './components/CreateTermForm';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faPlus } from '@fortawesome/free-solid-svg-icons';

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
          <Link to="/terms" className={location.pathname === '/terms' ? 'active' : ''}>
            <i className="fas fa-book"></i> Термины
          </Link>
        </li>
        <li>
          <Link to="/documents" className={location.pathname === '/documents' ? 'active' : ''}>
            <i className="fas fa-file-alt"></i> ВНД
          </Link>
        </li>
        <li>
          <Link to="/analyze-document" className={location.pathname === '/analyze-document' ? 'active' : ''}>
            <i className="fas fa-file-upload"></i> Анализ документа
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
  const { user, apiClient } = useAuth();
  const [isModalOpen, setIsModalOpen] = useState(false);
  
  const openModal = () => {
    setIsModalOpen(true);
  };

  const closeModal = () => {
    setIsModalOpen(false);
  };

  const handleTermCreated = (newTerm) => {
    // Закрываем модальное окно после создания термина
    closeModal();
    // Перенаправляем на страницу созданного термина
    window.location.href = `/term/${newTerm.id}`;
  };
  
  return (
    <div className="app-wrapper">
      <Navigation />
      <div className="container">
        <Routes>
          <Route path="/" element={<Navigate to="/search" replace />} />

          <Route path="/search" element={<SearchPage />} />
          <Route path="/terms" element={<TermsListPage />} />
          <Route path="/documents" element={<DocumentsListPage />} />
          <Route path="/term/:termId" element={<TermPage />} />
          <Route path="/document/:docId" element={<DocumentPage />} />
          <Route path="/analyze-document" element={<DocumentAnalysisPage />} />

          <Route path="/login" element={<PublicRoute><LoginPage /></PublicRoute>} />
          <Route path="/register" element={<PublicRoute><RegisterPage /></PublicRoute>} />
          <Route path="/dashboard" element={<ProtectedRoute><DashboardPage /></ProtectedRoute>} />
        </Routes>
      </div>
      
      {/* Глобальные компоненты */}
      {user && (
        <button className="add-term-button" onClick={openModal} title="Добавить новый термин">
          <FontAwesomeIcon icon={faPlus} />
        </button>
      )}
      
      <Modal isOpen={isModalOpen} onClose={closeModal} title="Создание нового термина">
        <CreateTermForm 
          onSave={handleTermCreated} 
          onCancel={closeModal}
          apiClient={apiClient}
        />
      </Modal>
    </div>
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