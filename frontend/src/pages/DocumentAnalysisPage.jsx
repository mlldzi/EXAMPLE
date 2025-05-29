import React, { useState } from 'react';
import DocumentUploadForm from '../components/forms/DocumentUploadForm';
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import TermAnalysisItem from '../components/display/TermAnalysisItem';
import termsApi from '../api/terms';

function DocumentAnalysisPage() {
  const { apiClient } = useAuth();
  const [analysisItems, setAnalysisItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [termConflicts, setTermConflicts] = useState({});

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setAnalysisItems(null);
    setTermConflicts({});

    try {
      // Вызываем API для анализа документа
      // NOTE: Эта часть будет закомментирована, пока нет реального парсера/API
      // const results = await documentsApi.analyzeDocument(apiClient, file);
      // setAnalysisItems(results);

      // ### Заглушечные данные для фронтенда ###
      // Используем заглушечные данные, пока нет реального API вызова
      const dummyResults = [
          {
              "term": "Заглушка Термин 1 (фронтенд)",
              "definition": "Заглушка Определение 1 (фронтенд)",
              "source": "Заглушка Источник 1 (фронтенд)",
              "year": "2023"
          },
          {
              "term": "Заглушка Термин 2 (фронтенд)",
              "definition": "Заглушка Определение 2 (фронтенд)",
              "source": "Заглушка Источник 2 (фронтенд)",
              "year": "2024"
          },
          {
            "term": "Заглушка Термин 3 (без года)",
            "definition": "Заглушка Определение 3 (без года)",
            "source": "Заглушка Источник 3 (без года)",
            // Нет года для проверки
          }
      ];
      setAnalysisItems(dummyResults);
      // ### Конец заглушечных данных ###

      // Запускаем проверку конфликтов для каждого загруженного термина
      const conflictChecks = dummyResults.map(async (item, index) => {
        try {
          // Передаем только нужные для проверки поля
          const conflicts = await termsApi.checkTermConflict(apiClient, {
            name: item.term,
            definition: item.definition,
            year: item.year
          });
          if (conflicts && conflicts.length > 0) {
            // Сохраняем конфликты, привязывая их к индексу элемента
            setTermConflicts(prevConflicts => ({
              ...prevConflicts,
              [index]: conflicts
            }));
          }
        } catch (conflictErr) {
          console.error(`Error checking conflict for item ${index}:`, conflictErr);
          // Обработка ошибок проверки конфликтов, возможно, установка флага ошибки для этого элемента
        }
      });

      // Ждем завершения всех проверок конфликтов (опционально)
      await Promise.all(conflictChecks);

    } catch (err) {
      setError('Ошибка при анализе документа.');
      console.error('Error analyzing document:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveItem = (updatedItem) => {
    console.log('Элемент обновлен в списке:', updatedItem);
    setAnalysisItems(prevItems =>
      prevItems.map(item =>
        item === updatedItem ? updatedItem : item
      )
    );
  };
  
  const handleSaveAllClick = async () => {
      console.log('Сохранение всех терминов:', analysisItems);
      // TODO: Implement actual API call to save all terms
      // This might involve a new backend endpoint for batch saving, or iterating and calling the existing POST /terms/ endpoint for each new term.
      // При сохранении всех, нужно учитывать конфликты и, возможно, предлагать пользователю их разрешить.

      setLoading(true);
      setError(null);

      try {
          // Отправляем только необходимые поля для bulk-save
          const termsToSave = analysisItems.map(item => ({
              name: item.term,
              definition: item.definition,
              year: item.year || null,
              // tags: item.tags // Если теги будут извлекаться/редактироваться
          }));

          // Вызываем новый API клиент для bulk-save
          const result = await termsApi.bulkSaveTerms(apiClient, termsToSave);

          console.log('Результат bulk-save:', result);

          if (result.errors && result.errors.length > 0) {
              // Обработка ошибок сохранения (например, дубликаты)
              setError(`Ошибка при сохранении некоторых терминов: ${result.errors.length} из ${termsToSave.length}`);
              console.error('Errors during bulk save:', result.errors);
              // Возможно, стоит обновить состояние analysisItems, чтобы пометить термины с ошибками
          } else {
              // Все успешно сохранено
              alert(`Успешно сохранено ${result.saved_count} терминов.`);
              // Возможно, стоит очистить список анализItems или перенаправить пользователя
              setAnalysisItems([]); // Очищаем список после успешного сохранения
          }

      } catch (err) {
          setError('Произошла ошибка при сохранении терминов.');
          console.error('Error during bulk save:', err);
      } finally {
          setLoading(false);
      }
  };

  return (
    <div>
      <h2>Анализ документа</h2>
      <DocumentUploadForm onFileUpload={handleFileUpload} loading={loading} />

      {loading && <p>Анализ документа...</p>}
      {error && <p style={{ color: 'red' }}>{error}</p>}

      {analysisItems && analysisItems.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Результаты анализа</h3>
          <ul>
            {analysisItems.map((item, index) => (
              <li key={index}>
                <TermAnalysisItem
                  item={item}
                  onSave={handleSaveItem}
                  onCancel={() => { /* Логика отмены */ }}
                  conflicts={termConflicts[index]}
                />
              </li>
            ))}
          </ul>
           {/* Кнопка для сохранения всех терминов */}
          <button onClick={handleSaveAllClick} style={{ marginTop: '20px' }}>
              Сохранить все термины
          </button>
        </div>
      )}
      {analysisItems && analysisItems.length === 0 && (
         <p>Термины не найдены в документе.</p>
      )}
    </div>
  );
}

export default DocumentAnalysisPage; 