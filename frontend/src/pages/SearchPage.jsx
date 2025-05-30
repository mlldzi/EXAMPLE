import React, { useState, useEffect } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSearch, faBook } from '@fortawesome/free-solid-svg-icons';
import TermItem from '../components/TermItem';
import { useAuth } from '../contexts/AuthContext';
import termsApi from '../api/terms';

function SearchPage() {
  const [searchQuery, setSearchQuery] = useState('');
  const [terms, setTerms] = useState([]);
  const [loading, setLoading] = useState(false);
  const [initialLoad, setInitialLoad] = useState(true);
  const { apiClient } = useAuth();
  
  useEffect(() => {
    // Загружаем несколько популярных терминов при первом рендере
    const fetchInitialTerms = async () => {
      try {
        setLoading(true);
        const response = await termsApi.getTerms(apiClient, 0, 6);
        setTerms(response);
        setInitialLoad(false);
      } catch (error) {
        console.error('Error fetching initial terms:', error);
      } finally {
        setLoading(false);
      }
    };
    
    if (initialLoad) {
      fetchInitialTerms();
    }
  }, [apiClient, initialLoad]);
  
  const handleSearch = async (e) => {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    
    setLoading(true);
    try {
      const response = await termsApi.getTerms(apiClient, 0, 100, searchQuery);
      setTerms(response);
    } catch (error) {
      console.error('Error searching terms:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="search-page fade-in">
      <div className="search-hero">
        <h1>Единый глоссарий терминов ВНД</h1>
        <p className="search-subtitle">Найдите точные определения терминов из нормативных документов</p>
        
        <form onSubmit={handleSearch} className="search-form">
          <div className="search-input-group">
            <input
              type="text"
              placeholder="Введите термин для поиска..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="search-input"
            />
            <button type="submit" className="btn btn-primary search-btn">
              <FontAwesomeIcon icon={faSearch} />
            </button>
          </div>
        </form>
      </div>
      
      {loading ? (
        <div className="loading-animation">
          <div className="loader"></div>
          <p>Поиск терминов...</p>
        </div>
      ) : (
        <div className="search-results">
          {terms.length > 0 ? (
            <>
              <h2>{searchQuery ? 'Результаты поиска' : 'Популярные термины'}</h2>
              <div className="terms-grid">
                {terms.map((term) => (
                  <TermItem key={term.id} term={term} />
                ))}
              </div>
            </>
          ) : searchQuery ? (
            <div className="no-results">
              <FontAwesomeIcon icon={faSearch} size="4x" style={{ color: 'var(--color-gray-300)', marginBottom: '1rem' }} />
              <h3>Ничего не найдено</h3>
              <p>Попробуйте изменить запрос или добавить новый термин</p>
            </div>
          ) : (
            <div className="no-results">
              <FontAwesomeIcon icon={faBook} size="4x" style={{ color: 'var(--color-gray-300)', marginBottom: '1rem' }} />
              <h3>Термины не найдены</h3>
              <p>В системе пока нет добавленных терминов</p>
            </div>
          )}
        </div>
      )}
    </div>
  );
}

export default SearchPage; 