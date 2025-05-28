import React, { useEffect, useState } from 'react';
import { useAuth } from '../contexts/AuthContext';
import termsApi from '../api/terms';
import termDocumentRelationsApi from '../api/termDocumentRelations';
import TermStatisticsTable from '../components/display/TermStatisticsTable';
import AllConflictsReportList from '../components/display/AllConflictsReportList';

const DashboardPage = () => {
  const { user, logout, apiClient } = useAuth();
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
          termsApi.getTermStatistics(apiClient),
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
      
      <hr style={{ margin: '20px 0' }} />

      <h3>Общая статистика и отчеты</h3>
      {loadingStats ? (
        <p>Загрузка статистики и отчетов...</p>
      ) : errorStats ? (
        <p style={{ color: 'red' }}>Ошибка загрузки статистики: {errorStats}</p>
      ) : (
        <div>
          <h4>Статистика использования терминов</h4>
          <TermStatisticsTable statistics={termStatistics} />

          <hr style={{ margin: '20px 0' }} />

          <h4>Полный отчет о конфликтах</h4>
          <AllConflictsReportList report={allConflictsReport} />
        </div>
      )}

      <button onClick={logout} style={{marginTop: '20px', backgroundColor: '#d9534f'}}>
        Выйти
      </button>
    </div>
  );
}

export default DashboardPage; 