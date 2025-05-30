import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import termsApi from '../api/terms';
import termDocumentRelationsApi from '../api/termDocumentRelations';
import TermStatisticsTable from '../components/display/TermStatisticsTable';
import AllConflictsReportList from '../components/display/AllConflictsReportList';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSignOutAlt, faUserShield, faTools, faToggleOn, faToggleOff } from '@fortawesome/free-solid-svg-icons';
import axios from 'axios';

const DashboardPage = () => {
  const { user, logout, apiClient, debugAdminMode, toggleDebugAdminMode } = useAuth();
  const [termStatistics, setTermStatistics] = useState([]);
  const [allConflictsReport, setAllConflictsReport] = useState([]);
  const [loadingStats, setLoadingStats] = useState(true);
  const [errorStats, setErrorStats] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoadingStats(true);
      setErrorStats(null);
      try {
        const [statsResponse, conflictsResponse] = await Promise.all([
          termsApi.getTermsStatistics(apiClient),
          termDocumentRelationsApi.getAllConflictsReport(apiClient),
        ]);
        setTermStatistics(statsResponse);
        setAllConflictsReport(conflictsResponse);
        setLoadingStats(false);
      } catch (err) {
        setErrorStats('Не удалось загрузить статистику или отчеты.');
        setLoadingStats(false);
        console.error('Error fetching dashboard data:', err);
      }
    };

    fetchData();
  }, [apiClient]);

  if (!user) {
    return <p>Загрузка данных пользователя...</p>;
  }

  return (
    <div className="dashboard-container card">
      <h2>Панель управления</h2>
      <p>Добро пожаловать, {user.full_name || user.email}!</p>
      <p>Это защищенная страница.</p>
      
      <div className="user-profile-card">
        <h3>Профиль пользователя</h3>
        <div className="profile-details">
          <div className="profile-item">
            <span className="profile-label">ID пользователя:</span>
            <span className="profile-value">{user.id}</span>
          </div>
          <div className="profile-item">
            <span className="profile-label">Email:</span>
            <span className="profile-value">{user.email}</span>
          </div>
          <div className="profile-item">
            <span className="profile-label">Username:</span>
            <span className="profile-value">{user.username}</span>
          </div>
          <div className="profile-item">
            <span className="profile-label">Роли:</span>
            <span className="profile-value">{user.roles.join(', ')}</span>
          </div>
          <div className="profile-item">
            <span className="profile-label">Статус:</span>
            <span className="profile-value">{user.status}</span>
          </div>
          <div className="profile-item">
            <span className="profile-label">Активен:</span>
            <span className="profile-value">{user.is_active ? 'Да' : 'Нет'}</span>
          </div>
          <div className="profile-item">
            <span className="profile-label">Зарегистрирован:</span>
            <span className="profile-value">{new Date(user.created_at).toLocaleString()}</span>
          </div>
        </div>

        <div className="debug-panel">
          <h4>
            <FontAwesomeIcon icon={faTools} /> Панель отладки
          </h4>
          <div className="debug-controls">
            <button 
              onClick={toggleDebugAdminMode} 
              className={`btn admin-toggle-btn ${debugAdminMode ? 'admin-toggle-active' : ''}`}
            >
              <FontAwesomeIcon icon={debugAdminMode ? faToggleOn : faToggleOff} />
              <span className="toggle-label">
                <FontAwesomeIcon icon={faUserShield} /> Режим администратора: {debugAdminMode ? 'Включен' : 'Выключен'}
              </span>
            </button>
            {debugAdminMode && (
              <div className="admin-mode-notice">
                <p>Режим администратора активирован для отладки. В этом режиме доступны все функции администратора.</p>
              </div>
            )}
          </div>
        </div>
      </div>
      
      <hr className="dashboard-divider" />

      <h3>Общая статистика и отчеты</h3>
      {loadingStats ? (
        <div className="loading-animation">
          <div className="loader"></div>
          <p>Загрузка статистики и отчетов...</p>
        </div>
      ) : errorStats ? (
        <div className="error-message">{errorStats}</div>
      ) : (
        <div>
          <div className="dashboard-section">
            <h4>Статистика использования терминов</h4>
            <TermStatisticsTable statistics={termStatistics} />
          </div>

          <hr className="dashboard-divider" />

          <div className="dashboard-section">
            <h4>Полный отчет о конфликтах</h4>
            <AllConflictsReportList report={allConflictsReport} />
          </div>
        </div>
      )}

      <button 
        onClick={logout} 
        className="btn logout-button"
      >
        <FontAwesomeIcon icon={faSignOutAlt} /> Выйти
      </button>
    </div>
  );
}

export default DashboardPage; 