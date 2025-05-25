import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import DocumentItem from '../components/DocumentItem';

function TermPage() {
  const { termName } = useParams(); // Получаем имя термина из URL
  const [termData, setTermData] = useState(null); // Состояние для данных о термине
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Заглушка для данных о термине в формате API
  // В реальном приложении здесь будет запрос к бэкенду по termName
  const mockTermData = {
    term: termName, // Используем имя из URL для заглушки
    definition: `Это определение для термина "${termName}".`, // Динамическое определение
    source: 'Пример ВНД, где встречается термин',
    year: 2023,
    // Добавим пример данных о ВНД, если API их предоставляет отдельно
    // Если API возвращает только source и year для каждого вхождения, нужно будет переработать
    documents: [
      { id: 'vnd-1', name: 'ВНД 1', hasDiscrepancy: false, context: 'Пример использования термина в ВНД 1.' },
      { id: 'vnd-2', name: 'ВНД 2', hasDiscrepancy: true, discrepancyText: 'Отличное определение в этом документе.', context: 'Другой пример использования термина в ВНД 2.' },
      { id: 'vnd-3', name: 'ВНД 3', hasDiscrepancy: false, context: 'Еще один пример использования.' },
    ]
  };

  useEffect(() => {
    // Имитация получения данных с API
    setLoading(true);
    // В реальном приложении: fetch(`/api/terms/${termName}`).then(...)
    setTimeout(() => {
      setTermData(mockTermData);
      setLoading(false);
    }, 500); // Имитация задержки сети
  }, [termName]); // Перезагружаем данные при изменении termName

  if (loading) {
    return <div>Загрузка...</div>;
  }

  if (error) {
    return <div>Ошибка: {error.message}</div>; // Обработка ошибок
  }

  if (!termData) {
    return <div>Термин не найден.</div>; // Если данные не получены
  }

  return (
    <div>
      <h1>Термин: {termData.term}</h1>

      <div className="term-section">
        <h2>Определение</h2>
        <p>{termData.definition}</p>
      </div>

      {/* Отображаем Source и Year, если они есть в данных термина */}
      {(termData.source || termData.year) && (
        <div className="term-section">
          <h2>Источник и Год</h2>
          <p>
            {termData.source && <span>Источник: {termData.source}</span>}
            {termData.source && termData.year && <span>, </span>}
            {termData.year && <span>Год: {termData.year}</span>}
          </p>
        </div>
      )}

      {/* Отображение списка ВНД, если данные о документах доступны */}
      {termData.documents && termData.documents.length > 0 && (
        <div className="term-section">
          <h2>Использование в ВНД</h2>
          <div>
            {termData.documents.map((doc) => (
              <DocumentItem key={doc.id} document={doc} />
            ))}
          </div>
        </div>
      )}

      {/* Секция для выявления разночтений, если есть документы с разночтениями */}
      {termData.documents && termData.documents.some(doc => doc.hasDiscrepancy) && (
        <div className="term-section">
          <h2>Разночтения</h2>
          {termData.documents.filter(doc => doc.hasDiscrepancy).map(doc => (
            <div key={doc.id} style={{ marginBottom: '10px', padding: '10px', border: '1px dashed #ccc', borderRadius: '4px' }}>
              <strong>{doc.name}:</strong> {doc.discrepancyText}
            </div>
          ))}
        </div>
      )}

    </div>
  );
}

export default TermPage; 