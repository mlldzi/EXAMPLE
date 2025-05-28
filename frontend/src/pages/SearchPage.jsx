import React, { useEffect, useState } from 'react';
import TermItem from '../components/TermItem';
import termsApi from '../api/terms'; // Импортируем API клиент для терминов
import { useAuth } from '../contexts/AuthContext';

const SearchPage = () => {
  const { apiClient } = useAuth(); // Получаем apiClient из AuthContext
  const [searchTerm, setSearchTerm] = useState(''); // Состояние для поискового запроса
  const [terms, setTerms] = useState([]);
  const [loading, setLoading] = useState(false); // Изначально не загружаем все термины
  const [error, setError] = useState(null);

  // Функция для загрузки терминов с возможностью поиска
  const fetchTerms = async (query = '') => {
    setLoading(true);
    setError(null);
    try {
      // Передаем поисковый запрос в API
      const data = await termsApi.getTerms(apiClient, { query: query });
      setTerms(data);
      setLoading(false);
    } catch (err) {
      setError('Не удалось загрузить термины.');
      setLoading(false);
      console.error('Error fetching terms in SearchPage:', err);
    } finally {
      setLoading(false);
    }
  };

  // Обработчик изменения поля ввода поиска
  const handleSearchInputChange = (event) => {
    setSearchTerm(event.target.value);
  };

  // Обработчик нажатия кнопки поиска или Enter в поле ввода
  const handleSearch = () => {
    fetchTerms(searchTerm); // Запускаем поиск с текущим значением searchTerm
  };
  
  // При монтировании компонента загрузим все термины (пустой поиск)
  useEffect(() => {
      fetchTerms('');
  }, [apiClient]); // Зависимость от apiClient

  if (loading) {
    return <div>Загрузка терминов...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Ошибка: {error}</div>;
  }

  return (
    <div>
      <h1>Единая база знаний: Глоссарий</h1>

      <div style={{ marginBottom: '20px' }}>
        {/* Поле поиска */}
        <input 
          type="text" 
          placeholder="Искать термин..."
          value={searchTerm} // Привязываем значение к состоянию
          onChange={handleSearchInputChange} // Обработчик изменения
          onKeyDown={(e) => { // Поиск по нажатию Enter
            if (e.key === 'Enter') {
              handleSearch();
            }
          }}
          style={{
            padding: '10px',
            marginRight: '8px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        />
        <button onClick={handleSearch} style={{ padding: '10px 15px', fontSize: '1rem' }}>Найти</button>
      </div>

      <h2>Список терминов</h2>
      <div>
        {terms.length > 0 ? (
          terms.map((term) => (
            // Используем id термина в качестве key, предполагая его наличие от API
            <TermItem key={term.id} term={term} />
          ))
        ) : (
          <div>Термины не найдены.</div>
        )}
      </div>
    </div>
  );
}

export default SearchPage; 