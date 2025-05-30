import React, { useState } from 'react';
import DocumentUploadForm from '../components/forms/DocumentUploadForm';
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import TermAnalysisItem from '../components/display/TermAnalysisItem';
import termsApi from '../api/terms';
import termDocumentRelationsApi from '../api/termDocumentRelations';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExclamationTriangle, faCheckCircle } from '@fortawesome/free-solid-svg-icons';

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
      const results = await documentsApi.analyzeDocument(apiClient, file);
      
      // Добавляем свойство excluded = false для каждого термина
      const resultsWithExcluded = results.map(item => ({
        ...item,
        excluded: false,
        // Добавляем originalTerm для отслеживания изменений при редактировании
        originalTerm: item.term
      }));
      
      setAnalysisItems(resultsWithExcluded);

      // Если не получили результатов анализа
      if (!results || results.length === 0) {
        setError('Не удалось извлечь термины из документа. Убедитесь, что документ содержит глоссарий или раздел с терминами и определениями.');
        return;
      }

      // Проверка конфликтов для каждого найденного термина
      const conflictChecks = results.map(async (item, index) => {
        try {
          // Передаем данные термина для проверки конфликтов
          // Теперь проверяем только по имени термина, сравнение определений будет на бэкенде
          const conflicts = await termsApi.checkTermConflict(apiClient, {
            name: item.term,
            // Отправляем определение, но сравнение по определению будет на бэкенде
            definition: item.definition,
            year: item.year || documentData.year || null
          }, {
            // Указываем, что нужно сохранять историю определений
            save_to_history: true
          });
          
          if (conflicts && conflicts.length > 0) {
            // Фильтруем конфликты, чтобы показывать только те, где разные определения
            const definitionConflicts = conflicts.filter(conflict => 
              conflict.conflicting_definition !== item.definition
            );
            
            if (definitionConflicts.length > 0) {
              // Сохраняем только конфликты с разными определениями
              setTermConflicts(prevConflicts => ({
                ...prevConflicts,
                [index]: definitionConflicts
              }));
              
              // Выводим предупреждение в консоль для отладки
              console.log(`Найдены конфликты определений для термина "${item.term}":`, definitionConflicts);
            }
          }
        } catch (conflictErr) {
          console.error(`Ошибка при проверке конфликтов для термина ${item.term}:`, conflictErr);
        }
      });
      
      // Ждем завершения всех проверок конфликтов
      await Promise.all(conflictChecks);
      
    } catch (err) {
      console.error('Error analyzing document:', err);
      setError('Произошла ошибка при анализе документа: ' + (err.message || 'Неизвестная ошибка'));
    } finally {
      setLoading(false);
    }
  };
  
  // Обработчик для разрешения конфликтов терминов
  const handleResolveConflict = (updatedItem) => {
    console.log('Разрешение конфликта для термина:', updatedItem);
    
    // Обновляем элемент в массиве, включая разрешение конфликта
    setAnalysisItems(prevItems => {
      return prevItems.map(item => {
        // Находим элемент для обновления
        if ((item.id && updatedItem.id && item.id === updatedItem.id) || 
            (item.originalTerm && item.originalTerm === updatedItem.originalTerm) || 
            (item.term === updatedItem.originalTerm || item.term === updatedItem.term)) {
          
          // Возвращаем обновленный элемент, сохраняя состояние excluded
          return {
            ...updatedItem,
            excluded: item.excluded
          };
        }
        return item;
      });
    });
    
    // Находим индекс элемента для обновления в массиве
    const itemIndex = analysisItems.findIndex(item => {
      if (item.id && updatedItem.id) {
        return item.id === updatedItem.id;
      } else if (item.originalTerm) {
        return item.originalTerm === updatedItem.originalTerm;
      } else {
        return item.term === updatedItem.originalTerm || item.term === updatedItem.term;
      }
    });
    
    // Если конфликт разрешен, удаляем запись о конфликтах из termConflicts
    if (updatedItem.conflictResolved && itemIndex !== -1) {
      setTermConflicts(prevConflicts => {
        const newConflicts = { ...prevConflicts };
        delete newConflicts[itemIndex];
        return newConflicts;
      });
    }
  };

  const handleSaveItem = (updatedItem) => {
    console.log('Элемент обновлен в списке:', updatedItem);
    
    // Обновляем элемент в массиве, сохраняя флаг excluded
    setAnalysisItems(prevItems => {
      return prevItems.map(item => {
        // Находим элемент по совпадению исходного термина или ID (если есть)
        if (item.id && updatedItem.id) {
          // Если у обоих элементов есть ID, сравниваем их
          return item.id === updatedItem.id ? { ...updatedItem, excluded: item.excluded } : item;
        } else {
          // Если редактируемый термин, ищем по индексу или другим способом
          // Важно: тут ключевая проблема - мы искали по совпадению term, но term уже изменен
          // Нам нужно найти объект по другому принципу (например, по индексу или оригинальному имени)
          
          // Добавляем специальное поле для отслеживания оригинального термина при редактировании
          if (item.originalTerm === updatedItem.originalTerm) {
            return { ...updatedItem, excluded: item.excluded };
          } else if (item.term === updatedItem.originalTerm) {
            // Это случай первого редактирования, когда еще нет originalTerm
            return { ...updatedItem, originalTerm: item.term, excluded: item.excluded };
          }
          
          return item;
        }
      });
    });
    
    // Обновляем проверку конфликтов для измененного термина, если изменилось название или определение
    const checkConflictsForUpdatedTerm = async () => {
      try {
        const conflicts = await termsApi.checkTermConflict(apiClient, {
          name: updatedItem.term,
          definition: updatedItem.definition,
          year: updatedItem.year || documentData.year || null
        }, {
          save_to_history: true
        });
        
        // Находим индекс элемента в массиве, учитывая originalTerm
        const itemIndex = analysisItems.findIndex(item => {
          if (item.id && updatedItem.id) {
            return item.id === updatedItem.id;
          } else if (item.originalTerm) {
            return item.originalTerm === updatedItem.originalTerm;
          } else {
            return item.term === updatedItem.originalTerm || item.term === updatedItem.term;
          }
        });
        
        if (itemIndex !== -1) {
          if (conflicts && conflicts.length > 0) {
            // Фильтруем конфликты, чтобы показывать только те, где разные определения
            const definitionConflicts = conflicts.filter(conflict => 
              conflict.conflicting_definition !== updatedItem.definition
            );
            
            if (definitionConflicts.length > 0) {
              // Обновляем конфликты для этого элемента
              setTermConflicts(prevConflicts => ({
                ...prevConflicts,
                [itemIndex]: definitionConflicts
              }));
            } else {
              // Удаляем запись о конфликтах, если их больше нет
              setTermConflicts(prevConflicts => {
                const newConflicts = { ...prevConflicts };
                delete newConflicts[itemIndex];
                return newConflicts;
              });
            }
          } else {
            // Удаляем запись о конфликтах, если их больше нет
            setTermConflicts(prevConflicts => {
              const newConflicts = { ...prevConflicts };
              delete newConflicts[itemIndex];
              return newConflicts;
            });
          }
        }
      } catch (err) {
        console.error('Ошибка при проверке конфликтов после редактирования:', err);
      }
    };
    
    // Запускаем проверку конфликтов
    checkConflictsForUpdatedTerm();
  };
  
  // Функция для переключения исключения термина (не удаляем, а помечаем)
  const handleExcludeItem = (itemToToggle) => {
    // Переключаем флаг excluded
    setAnalysisItems(prevItems => {
      return prevItems.map(item => {
        // Находим элемент по совпадению термина или ID
        if (item.id && itemToToggle.id) {
          return item.id === itemToToggle.id 
            ? { ...item, excluded: !item.excluded } 
            : item;
        } else {
          return item.term === itemToToggle.term 
            ? { ...item, excluded: !item.excluded } 
            : item;
        }
      });
    });
  };
  
  // Получение количества разрешенных конфликтов
  const getResolvedConflictsCount = () => {
    return analysisItems ? analysisItems.filter(item => item.conflictResolved).length : 0;
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

          // Фильтруем термины, исключая те, которые помечены как excluded
          const termsToSave = analysisItems
            .filter(item => !item.excluded)
            .map(item => ({
              name: item.term,
              definition: item.definition,
              year: item.year || documentData.year || null,
              // Не включаем source, так как источник - это документ
            }));

          // Проверяем, остались ли термины после фильтрации
          if (termsToSave.length === 0) {
            setError('Все термины были исключены из сохранения. Нет терминов для отправки на сервер.');
            setLoading(false);
            return;
          }

          // Вызываем bulk-save для терминов с опцией сохранения истории
          const result = await termsApi.bulkSaveTerms(apiClient, termsToSave, {
            // Сохраняем историю определений при разрешении конфликтов
            save_history: true,
            // Заменяем существующие определения новыми
            replace_definitions: true,
            // Обновляем существующие термины, вместо создания новых
            update_existing: true
          });

          console.log('Результат bulk-save:', result);

          // Проверяем результат - могут быть saved_count или saved_terms
          const savedTerms = result.saved_terms || [];
          const savedCount = result.saved_count || savedTerms.length;
          
          if (savedCount > 0 || (result.updated_count && result.updated_count > 0)) {
              // Создаем связи между терминами и документом
              const relationPromises = [];
              
              // Сохраняем информацию о созданных и обновленных терминах
              const savedOrUpdatedCount = (savedCount || 0) + (result.updated_count || 0);
              
              // Получаем список всех терминов (созданных и обновленных)
              // Или собираем все идентификаторы терминов из сохраненных и обновленных
              let termsList = [];
              
              if (savedTerms && savedTerms.length > 0) {
                // Если в ответе есть saved_terms с полными данными
                termsList = [...savedTerms];
                
                if (result.updated_terms && result.updated_terms.length > 0) {
                  termsList = [...termsList, ...result.updated_terms];
                }
              } else {
                // Если в ответе только количество, запрашиваем термины по именам
                const termNames = termsToSave.map(t => t.name);
                const termsResponse = await termsApi.getTermsByNames(apiClient, termNames);
                
                if (termsResponse && termsResponse.length > 0) {
                  termsList = termsResponse;
                }
              }
              
              // Создаем связи между терминами и документом
              if (termsList.length > 0) {
                relationPromises.push(...termsList.map(async (term) => {
                  try {
                    // Находим соответствующий термин из первоначального списка
                    const originalTerm = analysisItems
                      .filter(item => !item.excluded)
                      .find(item => item.term === term.name);
                    
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

              await Promise.all(relationPromises);

              // Получаем количество исключенных терминов
              const excludedCount = analysisItems.filter(item => item.excluded).length;
              
              // Показываем сообщение с учетом исключенных терминов и разрешенных конфликтов
              const resolvedConflictsCount = getResolvedConflictsCount();
              
              let successMessage = `Успешно обработано ${savedOrUpdatedCount} терминов:`;
              if (savedCount > 0) {
                successMessage += `\n- Создано новых: ${savedCount}`;
              }
              if (result.updated_count > 0) {
                successMessage += `\n- Обновлено существующих: ${result.updated_count}`;
              }
              
              if (excludedCount > 0) {
                successMessage += `\n- Исключено из сохранения: ${excludedCount}`;
              }
              if (resolvedConflictsCount > 0) {
                successMessage += `\n- Разрешено конфликтов: ${resolvedConflictsCount}`;
              }
              
              alert(successMessage);
          } else {
              // Проверяем наличие ошибок
              if (result.errors && result.errors.length > 0) {
                // Формируем сообщение об ошибке с информацией о проблемных терминах
                const errorDetails = result.errors
                  .map(err => `"${err.name}": ${err.detail || 'Неизвестная ошибка'}`)
                  .join("\n");
                
                setError(`Не удалось сохранить термины:\n${errorDetails}`);
              } else {
                setError('Не удалось сохранить термины. Проверьте, возможно, они уже существуют в системе.');
              }
          }

      } catch (err) {
          console.error('Error during bulk save and relations creation:', err);
          if (err.response && err.response.data && err.response.data.detail) {
            // Получаем подробности ошибки от API
            if (Array.isArray(err.response.data.detail)) {
              const errorMsg = err.response.data.detail
                .map(e => e.msg || JSON.stringify(e))
                .join('\n');
              setError(`Ошибка при сохранении: ${errorMsg}`);
            } else {
              setError(`Ошибка при сохранении: ${err.response.data.detail}`);
            }
          } else {
            setError('Произошла ошибка при сохранении терминов и связей: ' + (err.message || 'Неизвестная ошибка'));
          }
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
          
          {/* Статистика обработки терминов */}
          <div style={{ 
            display: 'flex', 
            gap: '10px', 
            marginBottom: '20px',
            flexWrap: 'wrap'
          }}>
            {/* Предупреждение о наличии конфликтов */}
            {Object.keys(termConflicts).length > 0 && (
              <div className="conflicts-summary-alert" style={{ 
                backgroundColor: '#f8d7da', 
                border: '1px solid #f5c6cb', 
                padding: '15px', 
                borderRadius: '4px',
                color: '#721c24',
                flex: '1',
                minWidth: '250px'
              }}>
                <h4 style={{ margin: '0 0 10px 0' }}>
                  <FontAwesomeIcon icon={faExclamationTriangle} style={{ marginRight: '10px' }} />
                  Обнаружены конфликты терминов
                </h4>
                <p>
                  В документе найдены термины, которые уже существуют в системе. 
                  Эти термины отмечены предупреждением. Рекомендуется просмотреть каждый термин с конфликтом 
                  и разрешить конфликт.
                </p>
                <p>
                  Всего терминов с конфликтами: <strong>{Object.keys(termConflicts).length}</strong> из {analysisItems.length}
                </p>
              </div>
            )}
          
            {/* Счетчик исключенных терминов */}
            {analysisItems.some(item => item.excluded) && (
              <div style={{ 
                backgroundColor: '#e2e3e5', 
                border: '1px solid #d6d8db', 
                padding: '15px', 
                borderRadius: '4px',
                color: '#383d41',
                flex: '1',
                minWidth: '250px'
              }}>
                <p style={{ margin: 0 }}>
                  Исключено терминов: <strong>{analysisItems.filter(item => item.excluded).length}</strong> из {analysisItems.length}
                </p>
              </div>
            )}
            
            {/* Счетчик разрешенных конфликтов */}
            {getResolvedConflictsCount() > 0 && (
              <div style={{ 
                backgroundColor: '#d4edda', 
                border: '1px solid #c3e6cb', 
                padding: '15px', 
                borderRadius: '4px',
                color: '#155724',
                flex: '1',
                minWidth: '250px'
              }}>
                <h4 style={{ margin: '0 0 10px 0' }}>
                  <FontAwesomeIcon icon={faCheckCircle} style={{ marginRight: '10px' }} />
                  Разрешено конфликтов
                </h4>
                <p style={{ margin: 0 }}>
                  Разрешено конфликтов: <strong>{getResolvedConflictsCount()}</strong>
                </p>
              </div>
            )}
          </div>
          
          <ul style={{ listStyle: 'none', padding: 0 }}>
            {analysisItems.map((item, index) => (
              <li key={index} style={{ marginBottom: '15px', padding: '10px', border: '1px solid #ddd', borderRadius: '5px' }}>
                <TermAnalysisItem
                  item={item}
                  onSave={handleSaveItem}
                  onCancel={() => { /* Логика отмены */ }}
                  onExclude={handleExcludeItem}
                  onResolveConflict={handleResolveConflict}
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