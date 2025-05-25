import React from 'react';
import TermItem from '../components/TermItem';

function SearchPage() {
  // Заглушка для списка терминов в формате API
  const terms = [
    { term: 'Термин 1', definition: 'Определение 1', source: 'ВНД 1', year: 2023 },
    { term: 'Термин 2', definition: 'Определение 2', source: 'ВНД 2', year: 2022 },
    { term: 'Термин 3', definition: 'Определение 3', source: 'ВНД 3', year: 2024 },
    { term: 'Еще один термин', definition: 'Определение 4', source: 'ВНД 4', year: 2021 },
  ];

  return (
    <div>
      <h1>Единая база знаний: Глоссарий</h1>

      <div style={{ marginBottom: '20px' }}>
        {/* Поле поиска */}
        <input 
          type="text" 
          placeholder="Искать термин..."
          style={{
            padding: '10px',
            marginRight: '8px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            fontSize: '1rem'
          }}
        />
        <button style={{ padding: '10px 15px', fontSize: '1rem' }}>Найти</button>
      </div>

      <h2>Список терминов</h2>
      <div>
        {terms.map((term, index) => (
          // Используем index в качестве key пока нет уникального id от API
          <TermItem key={index} term={term} />
        ))}
      </div>
    </div>
  );
}

export default SearchPage; 