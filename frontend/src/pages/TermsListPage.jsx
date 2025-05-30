import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import termsApi from '../api/terms';

function TermsListPage() {
  const { apiClient } = useAuth();
  const [terms, setTerms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [currentPage, setCurrentPage] = useState(1);
  const [totalTerms, setTotalTerms] = useState(0);
  const [searchQuery, setSearchQuery] = useState('');
  const navigate = useNavigate();
  const termsPerPage = 20;

  // Загрузка терминов с учетом пагинации
  useEffect(() => {
    const fetchTerms = async () => {
      setLoading(true);
      try {
        const skip = (currentPage - 1) * termsPerPage;
        const response = await termsApi.getTerms(apiClient, {
          skip,
          limit: termsPerPage,
          search: searchQuery
        });
        
        setTerms(response.items || response);
        setTotalTerms(response.total || response.length);
      } catch (err) {
        console.error('Error fetching terms:', err);
        setError('Не удалось загрузить список терминов.');
      } finally {
        setLoading(false);
      }
    };

    fetchTerms();
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

  // Переход на страницу термина
  const handleTermClick = (termId) => {
    navigate(`/term/${termId}`);
  };

  // Расчет общего количества страниц
  const totalPages = Math.ceil(totalTerms / termsPerPage);

  // Переход на выбранную страницу
  const goToPage = (page) => {
    if (page >= 1 && page <= totalPages) {
      setCurrentPage(page);
    }
  };

  return (
    <div className="terms-list-page">
      <h1>Список терминов</h1>
      
      {/* Форма поиска */}
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          value={searchQuery}
          onChange={handleSearchChange}
          placeholder="Поиск термина..."
          className="search-input"
        />
        <button type="submit" className="search-button">Найти</button>
      </form>
      
      {loading ? (
        <div className="loading">Загрузка...</div>
      ) : error ? (
        <div className="error">{error}</div>
      ) : terms.length === 0 ? (
        <div className="no-results">
          {searchQuery ? 'Термины не найдены по запросу.' : 'Список терминов пуст.'}
        </div>
      ) : (
        <>
          <div className="terms-count">
            Найдено терминов: {totalTerms}
          </div>
          <div className="terms-grid">
            {terms.map((term) => (
              <div 
                key={term.id} 
                className="term-card" 
                onClick={() => handleTermClick(term.id)}
              >
                <h3 className="term-name">{term.name}</h3>
                <p className="term-definition">
                  {term.current_definition.length > 150 
                    ? `${term.current_definition.substring(0, 150)}...` 
                    : term.current_definition}
                </p>
                {term.tags && term.tags.length > 0 && (
                  <div className="term-tags">
                    {term.tags.map((tag, index) => (
                      <span key={index} className="term-tag">{tag}</span>
                    ))}
                  </div>
                )}
              </div>
            ))}
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

export default TermsListPage; 