import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';

function DocumentsListPage() {
  const { apiClient } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const docsPerPage = 15;

  // Загрузка документов с учетом пагинации
  useEffect(() => {
    const fetchDocuments = async () => {
      setLoading(true);
      try {
        const skip = (currentPage - 1) * docsPerPage;
        const response = await documentsApi.getDocuments(
          apiClient, 
          skip, 
          docsPerPage, 
          searchQuery
        );
        
        setDocuments(Array.isArray(response) ? response : (response.items || []));
      } catch (err) {
        console.error('Error fetching documents:', err);
        setError('Не удалось загрузить список документов.');
      } finally {
        setLoading(false);
      }
    };

    fetchDocuments();
  }, [apiClient, currentPage, searchQuery]);

  // Обработчик для поиска
  const handleSearch = (e) => {
    e.preventDefault();
    setCurrentPage(1); // Сбрасываем на первую страницу при поиске
  };

  // Обработчик изменения текста поиска
  const handleSearchChange = (e) => {
    setSearchQuery(e.target.value);
  };

  // Переход на страницу документа
  const handleDocumentClick = (docId) => {
    navigate(`/document/${docId}`);
  };

  // Получение статуса документа в виде текста
  const getStatusLabel = (status) => {
    const statuses = {
      'DRAFT': 'Черновик',
      'ACTIVE': 'Действующий',
      'EXPIRED': 'Истек',
      'CANCELLED': 'Отменен',
      'PENDING': 'На рассмотрении'
    };
    
    return statuses[status] || status;
  };

  // Получение цвета для статуса документа
  const getStatusColor = (status) => {
    const colors = {
      'DRAFT': '#607D8B',     // Серо-синий
      'ACTIVE': '#4CAF50',    // Зеленый
      'EXPIRED': '#FF9800',   // Оранжевый
      'CANCELLED': '#F44336', // Красный
      'PENDING': '#2196F3'    // Синий
    };
    
    return colors[status] || '#757575';
  };

  // Расчет общего количества страниц
  const totalPages = Math.ceil(documents.length / docsPerPage);

  // Переход на выбранную страницу
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="documents-list-page">
      <h1>Внутренние нормативные документы</h1>
      
      {/* Форма поиска */}
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Поиск по названию или номеру документа..."
          className="search-input"
        />
        <button type="submit" className="search-button">Найти</button>
      </form>
      
      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : documents.length === 0 ? (
        <div className="no-results">
          {searchQuery ? 'Документы не найдены по запросу.' : 'Список документов пуст.'}
        </div>
      ) : (
        <>
          <div className="documents-count">
            Найдено документов: {documents.length}
          </div>
          
          <div className="documents-table-container">
            <table className="documents-table">
              <thead>
                <tr>
                  <th>Номер документа</th>
                  <th>Название</th>
                  <th>Отдел</th>
                  <th>Год</th>
                  <th>Статус</th>
                </tr>
              </thead>
              <tbody>
                {documents.map((doc) => (
                  <tr 
                    key={doc.id} 
                    className="document-row" 
                    onClick={() => handleDocumentClick(doc.id)}
                  >
                    <td className="document-number">{doc.document_number}</td>
                    <td className="document-title">{doc.title}</td>
                    <td className="document-department">{doc.department || '-'}</td>
                    <td className="document-year">{doc.year || '-'}</td>
                    <td className="document-status">
                      <span 
                        className="status-indicator" 
                        style={{ backgroundColor: getStatusColor(doc.status) }}
                      >
                        {getStatusLabel(doc.status)}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          
          {/* Пагинация */}
          {totalPages > 1 && (
            <div className="pagination">
              <button 
                onClick={() => goToPage(currentPage - 1)} 
                disabled={currentPage === 1}
                className="pagination-button"
              >
                &laquo; Предыдущая
              </button>
              
              <span className="pagination-info">
                Страница {currentPage} из {totalPages}
              </span>
              
              <button 
                onClick={() => goToPage(currentPage + 1)} 
                disabled={currentPage === totalPages}
                className="pagination-button"
              >
                Следующая &raquo;
              </button>
            </div>
          )}
        </>
      )}
    </div>
  );
}

export default DocumentsListPage; 