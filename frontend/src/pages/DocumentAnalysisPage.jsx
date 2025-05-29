import React, { useState } from 'react';
import DocumentUploadForm from '../components/forms/DocumentUploadForm';
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import TermAnalysisItem from '../components/display/TermAnalysisItem';
import termsApi from '../api/terms';
import termDocumentRelationsApi from '../api/termDocumentRelations';

function DocumentAnalysisPage() {
  const { apiClient } = useAuth();
  const [analysisItems, setAnalysisItems] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [termConflicts, setTermConflicts] = useState({});
  const [documentData, setDocumentData] = useState({
    title: '',
    document_number: '',
    year: new Date().getFullYear().toString(),
    department: '',
    description: '',
    status: 'DRAFT',
    tags: ''
  });
  const [savedDocumentId, setSavedDocumentId] = useState(null);

  const handleDocumentDataChange = (e) => {
    const { name, value } = e.target;
    setDocumentData(prevData => ({
      ...prevData,
      [name]: value
    }));
  };

  const handleFileUpload = async (file) => {
    setLoading(true);
    setError(null);
    setAnalysisItems(null);
    setTermConflicts({});
    setSavedDocumentId(null);

    try {
      // Парсим название файла для названия документа
      if (file && file.name) {
        const fileName = file.name.split('.')[0]; // Берем имя файла без расширения
        setDocumentData(prev => ({
          ...prev,
          title: fileName
        }));
      }

      // Вызываем API для анализа документа
      // NOTE: Эта часть будет закомментирована, пока нет реального парсера/API
      // const results = await documentsApi.analyzeDocument(apiClient, file);
      // setAnalysisItems(results);

      // ### Заглушечные данные для фронтенда ###
      // Используем заглушечные данные, пока нет реального API вызова
      const dummyResults = [
          {
              "term": "Заглушка Термин 1",
              "definition": "Заглушка Определение 1",
              "year": "2023"
          },
          {
              "term": "Заглушка Термин 2",
              "definition": "Заглушка Определение 2",
              "year": "2024"
          },
          {
            "term": "Заглушка Термин 3 (без года)",
            "definition": "Заглушка Определение 3 (без года)",
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
        item.term === updatedItem.term ? updatedItem : item
      )
    );
  };
  
  const handleSaveDocument = async () => {
    if (!documentData.title || !documentData.document_number) {
      setError('Необходимо заполнить обязательные поля документа (название и номер)');
      return;
    }

    setLoading(true);
    setError(null);

    try {
      // Преобразуем тэги из строки в массив
      const tagsArray = documentData.tags 
        ? documentData.tags.split(',').map(tag => tag.trim()).filter(tag => tag) 
        : [];

      // Создаем документ
      const documentToSave = {
        ...documentData,
        tags: tagsArray,
        approval_date: documentData.year ? new Date(`${documentData.year}-01-01`).toISOString() : null
      };

      // Сохраняем документ
      const savedDocument = await documentsApi.createDocument(apiClient, documentToSave);
      
      if (savedDocument && savedDocument.id) {
        setSavedDocumentId(savedDocument.id);
        return savedDocument.id;
      } else {
        throw new Error('Не удалось получить ID сохраненного документа');
      }
    } catch (err) {
      setError('Ошибка при сохранении документа.');
      console.error('Error saving document:', err);
      return null;
    } finally {
      setLoading(false);
    }
  };

  const handleSaveAllClick = async () => {
      if (!analysisItems || analysisItems.length === 0) {
        setError('Нет терминов для сохранения.');
        return;
      }

      setLoading(true);
      setError(null);

      try {
          // Сначала сохраняем документ, если он еще не сохранен
          const documentId = savedDocumentId || await handleSaveDocument();
          
          if (!documentId) {
              throw new Error('Не удалось сохранить документ');
          }

          // Подготавливаем термины для сохранения
          const termsToSave = analysisItems.map(item => ({
              name: item.term,
              definition: item.definition,
              year: item.year || documentData.year || null,
              // Не включаем source, так как источник - это документ
          }));

          // Вызываем bulk-save для терминов
          const result = await termsApi.bulkSaveTerms(apiClient, termsToSave);

          console.log('Результат bulk-save:', result);

          // Проверяем результат - могут быть saved_count или saved_terms
          const savedTerms = result.saved_terms || [];
          const savedCount = result.saved_count || savedTerms.length;
          
          if (savedCount > 0) {
              // Создаем связи между терминами и документом
              const relationPromises = [];
              
              // Если в ответе есть saved_terms с полными данными терминов
              if (savedTerms.length > 0) {
                  relationPromises.push(...savedTerms.map(async (term, index) => {
                      try {
                          // Создаем связь с документом, сохраняя определение из документа
                          await termDocumentRelationsApi.createTermDocumentRelation(apiClient, {
                              term_id: term.id,
                              document_id: documentId,
                              term_definition_in_document: analysisItems[index].definition,
                              // Можно добавить локации/контекст, если они будут доступны от парсера
                          });
                      } catch (relErr) {
                          console.error(`Error creating relation for term ${term.id}:`, relErr);
                      }
                  }));
              } 
              // Если в ответе только количество сохраненных терминов, нужно проверить ID терминов по названию
              else if (savedCount > 0) {
                  // Получаем список всех сохраненных терминов по их названиям
                  const termNames = termsToSave.map(t => t.name);
                  const savedTermsResponse = await termsApi.getTermsByNames(apiClient, termNames);
                  
                  if (savedTermsResponse && savedTermsResponse.length > 0) {
                      // Для каждого сохраненного термина создаем связь с документом
                      relationPromises.push(...savedTermsResponse.map(async (term) => {
                          try {
                              // Находим соответствующий термин из первоначального списка
                              const originalTerm = analysisItems.find(item => item.term === term.name);
                              if (originalTerm) {
                                  await termDocumentRelationsApi.createTermDocumentRelation(apiClient, {
                                      term_id: term.id,
                                      document_id: documentId,
                                      term_definition_in_document: originalTerm.definition,
                                  });
                              }
                          } catch (relErr) {
                              console.error(`Error creating relation for term ${term.id}:`, relErr);
                          }
                      }));
                  }
              }

              await Promise.all(relationPromises);

              alert(`Успешно сохранено ${savedCount} терминов и создано связей с документом.`);
          } else {
              // Обработка ошибок сохранения
              setError('Не удалось сохранить термины.');
          }

          if (result.errors && result.errors.length > 0) {
              console.error('Errors during bulk save:', result.errors);
              // Показываем количество ошибок, но не прерываем процесс создания связей
              setError(`Ошибка при сохранении некоторых терминов: ${result.errors.length} из ${termsToSave.length}`);
          }

      } catch (err) {
          setError('Произошла ошибка при сохранении терминов и связей.');
          console.error('Error during bulk save and relations creation:', err);
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

      {analysisItems && analysisItems.length > 0 && !savedDocumentId && (
        <div style={{ marginTop: '20px', marginBottom: '20px' }}>
          <h3>Информация о документе</h3>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Название документа*:
                <input
                  type="text"
                  name="title"
                  value={documentData.title}
                  onChange={handleDocumentDataChange}
                  style={{ width: '100%', padding: '5px' }}
                  required
                />
              </label>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Номер документа*:
                <input
                  type="text"
                  name="document_number"
                  value={documentData.document_number}
                  onChange={handleDocumentDataChange}
                  style={{ width: '100%', padding: '5px' }}
                  required
                />
              </label>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Год документа:
                <input
                  type="text"
                  name="year"
                  value={documentData.year}
                  onChange={handleDocumentDataChange}
                  style={{ width: '100%', padding: '5px' }}
                />
              </label>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Отдел:
                <input
                  type="text"
                  name="department"
                  value={documentData.department}
                  onChange={handleDocumentDataChange}
                  style={{ width: '100%', padding: '5px' }}
                />
              </label>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Описание:
                <textarea
                  name="description"
                  value={documentData.description}
                  onChange={handleDocumentDataChange}
                  style={{ width: '100%', padding: '5px', minHeight: '80px' }}
                />
              </label>
            </div>
            
            <div>
              <label style={{ display: 'block', marginBottom: '5px' }}>
                Теги (через запятую):
                <input
                  type="text"
                  name="tags"
                  value={documentData.tags}
                  onChange={handleDocumentDataChange}
                  style={{ width: '100%', padding: '5px' }}
                />
              </label>
            </div>
          </div>
        </div>
      )}

      {analysisItems && analysisItems.length > 0 && (
        <div style={{ marginTop: '20px' }}>
          <h3>Найденные термины</h3>
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {analysisItems.map((item, index) => (
              <li key={index} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}>
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
          <button 
            onClick={handleSaveAllClick} 
            style={{ 
              marginTop: '20px', 
              padding: '10px 15px', 
              backgroundColor: '#4CAF50', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer' 
            }}
            disabled={loading}
          >
              {loading ? 'Сохранение...' : 'Сохранить все термины и документ'}
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