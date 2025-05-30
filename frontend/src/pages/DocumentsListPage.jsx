import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileAlt, faCalendarAlt, faBuilding, faTag } from '@fortawesome/free-solid-svg-icons';

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
      <form onSubmit={handleSearch} className="search-form" style={{
        marginBottom: '20px',
        display: 'flex',
        gap: '10px'
      }}>
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Поиск по названию или номеру документа..."
          className="search-input"
          style={{
            padding: '10px',
            borderRadius: '4px',
            border: '1px solid #ccc',
            flex: '1'
          }}
        />
        <button 
          type="submit" 
          className="search-button"
          style={{
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: 'pointer'
          }}
        >
          Найти
        </button>
      </form>
      
      {loading ? (
        <div className="loading" style={{ textAlign: 'center', padding: '20px' }}>Загрузка...</div>
      ) : error ? (
        <div className="error" style={{ color: 'red', padding: '20px' }}>{error}</div>
      ) : documents.length === 0 ? (
        <div className="no-results" style={{ textAlign: 'center', padding: '20px' }}>
          {searchQuery ? 'Документы не найдены по запросу.' : 'Список документов пуст.'}
        </div>
      ) : (
        <>
          <div className="documents-count" style={{ 
            marginBottom: '20px', 
            fontWeight: 'bold',
            fontSize: '16px'
          }}>
            Найдено документов: {documents.length}
          </div>
          
          {/* Карточки документов вместо таблицы */}
          <div className="documents-grid" style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))',
            gap: '20px',
            marginBottom: '20px'
          }}>
            {documents.map((doc) => (
              <div 
                key={doc.id} 
                className="document-card" 
                onClick={() => handleDocumentClick(doc.id)}
                style={{
                  padding: '15px',
                  backgroundColor: 'white',
                  borderRadius: '8px',
                  boxShadow: '0 2px 5px rgba(0,0,0,0.1)',
                  cursor: 'pointer',
                  transition: 'transform 0.2s, box-shadow 0.2s',
                  position: 'relative',
                  overflow: 'hidden'
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-3px)';
                  e.currentTarget.style.boxShadow = '0 4px 10px rgba(0,0,0,0.15)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 2px 5px rgba(0,0,0,0.1)';
                }}
              >
                {/* Статус документа как верхняя полоса */}
                <div style={{
                  position: 'absolute',
                  top: '0',
                  left: '0',
                  right: '0',
                  height: '5px',
                  backgroundColor: getStatusColor(doc.status)
                }}></div>
                
                <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px', marginTop: '5px' }}>
                  <span 
                    className="document-status"
                    style={{
                      fontSize: '12px',
                      padding: '3px 8px',
                      borderRadius: '12px',
                      backgroundColor: getStatusColor(doc.status),
                      color: 'white',
                      marginRight: '10px'
                    }}
                  >
                    {getStatusLabel(doc.status)}
                  </span>
                  <span className="document-number" style={{ 
                    fontSize: '14px', 
                    color: '#666',
                    fontWeight: 'bold'
                  }}>
                    <FontAwesomeIcon icon={faFileAlt} style={{ marginRight: '5px' }} />
                    {doc.document_number}
                  </span>
                </div>
                
                <h3 className="document-title" style={{ 
                  margin: '0 0 12px 0',
                  fontSize: '18px',
                  lineHeight: '1.3'
                }}>
                  {doc.title}
                </h3>
                
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '5px' }}>
                  <FontAwesomeIcon icon={faBuilding} style={{ marginRight: '5px', width: '16px' }} />
                  {doc.department || 'Отдел не указан'}
                </div>
                
                <div style={{ fontSize: '14px', color: '#666', marginBottom: '10px' }}>
                  <FontAwesomeIcon icon={faCalendarAlt} style={{ marginRight: '5px', width: '16px' }} />
                  {doc.year || 'Год не указан'}
                </div>
                
                {doc.description && (
                  <p style={{ 
                    fontSize: '14px', 
                    margin: '10px 0',
                    color: '#444',
                    display: '-webkit-box',
                    WebkitLineClamp: '3',
                    WebkitBoxOrient: 'vertical',
                    overflow: 'hidden',
                    textOverflow: 'ellipsis'
                  }}>
                    {doc.description}
                  </p>
                )}
                
                {doc.tags && doc.tags.length > 0 && (
                  <div className="document-tags" style={{ 
                    display: 'flex', 
                    flexWrap: 'wrap',
                    gap: '5px',
                    marginTop: '10px'
                  }}>
                    <FontAwesomeIcon icon={faTag} style={{ 
                      marginRight: '5px', 
                      fontSize: '14px',
                      color: '#666'
                    }} />
                    {doc.tags.map((tag, index) => (
                      <span 
                        key={index} 
                        className="document-tag"
                        style={{
                          fontSize: '12px',
                          padding: '2px 8px',
                          backgroundColor: '#f0f0f0',
                          borderRadius: '12px',
                          color: '#666'
                        }}
                      >
                        {tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
          
          {/* Пагинация */}
          {totalPages > 1 && (
            <div className="pagination" style={{
              display: 'flex',
              justifyContent: 'center',
              gap: '15px',
              marginTop: '20px',
              marginBottom: '20px'
            }}>
              <button 
                onClick={() => goToPage(currentPage - 1)} 
                disabled={currentPage === 1}
                className="pagination-button"
                style={{
                  padding: '8px 15px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  backgroundColor: currentPage === 1 ? '#f0f0f0' : 'white',
                  cursor: currentPage === 1 ? 'not-allowed' : 'pointer',
                  color: currentPage === 1 ? '#999' : '#333'
                }}
              >
                &laquo; Предыдущая
              </button>
              
              <span className="pagination-info" style={{
                display: 'flex',
                alignItems: 'center',
                fontSize: '14px'
              }}>
                Страница {currentPage} из {totalPages}
              </span>
              
              <button 
                onClick={() => goToPage(currentPage + 1)} 
                disabled={currentPage === totalPages}
                className="pagination-button"
                style={{
                  padding: '8px 15px',
                  border: '1px solid #ccc',
                  borderRadius: '4px',
                  backgroundColor: currentPage === totalPages ? '#f0f0f0' : 'white',
                  cursor: currentPage === totalPages ? 'not-allowed' : 'pointer',
                  color: currentPage === totalPages ? '#999' : '#333'
                }}
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