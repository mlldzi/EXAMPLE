import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import DocumentItem from '../components/DocumentItem';
import termsApi from '../api/terms'; // Import the terms API client
import termDocumentRelationsApi from '../api/termDocumentRelations'; // Import relations API client
import TermConflictReport from '../components/display/TermConflictReport'; // Import the new component
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import TermEditForm from '../components/TermEditForm';

function TermPage() {
  const { termId } = useParams(); // Get termId from URL
  const { apiClient } = useAuth(); // Получаем apiClient из AuthContext
  const [termData, setTermData] = useState(null);
  const [relatedDocuments, setRelatedDocuments] = useState([]);
  const [conflictsReport, setConflictsReport] = useState(null); // State for conflicts report
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sourceDocuments, setSourceDocuments] = useState({});
  const [isEditing, setIsEditing] = useState(false); // Новое состояние для управления видимостью формы редактирования

  // Обработчик сохранения формы редактирования
  const handleSave = (updatedTerm) => {
    setTermData(updatedTerm); // Обновляем данные термина на странице
    setIsEditing(false); // Скрываем форму редактирования
  };

  // Обработчик отмены редактирования
  const handleCancel = () => {
    setIsEditing(false); // Скрываем форму редактирования
  };

  useEffect(() => {
    // console.log('useEffect in TermPage triggered. termId:', termId);
    // console.log('Current accessToken in TermPage:', apiClient.defaults.headers.common['Authorization']);
    const fetchData = async () => {
      console.log('Fetching data for termId:', termId);
      setLoading(true);
      setError(null);
      try {
        // Загружаем данные термина и связанные документы параллельно
        const [termData, documentsData, conflictsData] = await Promise.all([
          termsApi.getTermById(apiClient, termId), // Передаем apiClient
          termsApi.getDocumentsForTerm(apiClient, termId), // Передаем apiClient
          termDocumentRelationsApi.getTermConflictsReport(apiClient, termId) // Передаем apiClient
        ]);
        setTermData(termData);
        setRelatedDocuments(documentsData);
        setConflictsReport(conflictsData); // Store conflicts report
        setLoading(false);

        // Загружаем данные документов-источников для истории определений
        if (termData && termData.definitions_history) {
          const uniqueDocIds = [...new Set(termData.definitions_history
            .map(def => def.source_document_id)
            .filter(docId => docId != null))]; // Получаем уникальные не-null ID документов

          const fetchSourceDocuments = async () => {
            const docsData = {};
            for (const docId of uniqueDocIds) {
              if (!sourceDocuments[docId]) { // Проверяем, загружен ли уже документ
                try {
                  const doc = await documentsApi.getDocumentById(apiClient, docId); // Загружаем документ
                  docsData[docId] = doc; // Сохраняем данные документа
                } catch (docError) {
                  console.error(`Error fetching source document ${docId}:`, docError);
                  docsData[docId] = { id: docId, title: 'Не удалось загрузить' }; // Сохраняем плейсхолдер при ошибке
                }
              }
            }
            setSourceDocuments(prevDocs => ({ ...prevDocs, ...docsData })); // Обновляем состояние
          };

          fetchSourceDocuments();
        }

      } catch (err) {
        setError('Не удалось загрузить данные термина или отчет о конфликтах.');
        setLoading(false);
        console.error(`Error fetching data for term ${termId}:`, err);
      }
    };

    if (termId) {
      fetchData();
    }
  }, [termId, apiClient]); // Добавляем apiClient в зависимости

  // Мемоизируем данные документов-источников для рендеринга
  const memoizedSourceDocuments = useMemo(() => sourceDocuments, [sourceDocuments]);

  if (loading) {
    return <div>Загрузка данных термина...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Ошибка: {error}</div>;
  }

  if (!termData) {
    return <div>Термин не найден.</div>; // If no term data is fetched (e.g., invalid ID)
  }

  // Форма редактирования термина (отображается, если isEditing true)
  if (isEditing) {
    return (
      <TermEditForm
        term={termData}
        onSave={handleSave}
        onCancel={handleCancel}
        apiClient={apiClient}
      />
    );
  }

  return (
    <div>
      {/* Используем termData.name и termData.current_definition */}
      <h1>Термин: {termData.name}</h1>

      <div className="term-section">
        <h2>Определение</h2>
        <p>{termData.current_definition || 'Определение отсутствует.'}</p>
      </div>

      {/* Дополнительная информация о термине */}
      <div className="term-section">
        <h2>Дополнительная информация</h2>
        <p><strong>Статус:</strong> {termData.is_approved ? 'Утвержден' : 'Не утвержден'}</p>
        {termData.approved_at && (
          <p><strong>Утвержден:</strong> {new Date(termData.approved_at).toLocaleString()}</p>
        )}
        {termData.updated_at && (
          <p><strong>Последнее обновление:</strong> {new Date(termData.updated_at).toLocaleString()}</p>
        )}
        {termData.tags && termData.tags.length > 0 && (
          <p><strong>Теги:</strong> {termData.tags.join(', ')}</p>
        )}
        <button onClick={() => setIsEditing(true)}>Редактировать термин</button>
      </div>

      {/* Добавляем секцию для истории определений */}
      {termData.definitions_history && termData.definitions_history.length > 1 && ( // Проверяем, что история существует и содержит более одного определения (первое - текущее)
        <div className="term-section">
          <h2>История определений</h2>
          <ul>
            {/* Пропускаем первое определение, так как оно текущее */}
            {termData.definitions_history.slice(1).map((def, index) => (
              <li key={index} style={{ marginBottom: '10px' }}>
                <p><strong>Определение:</strong> {def.definition}</p>
                {/* Проверяем, что created_at является объектом Date перед форматированием */}
                <p><strong>Дата создания:</strong> {def.created_at ? new Date(def.created_at).toLocaleString() : 'Неизвестно'}</p>
                {/* Добавляем отображение пользователя и документа-источника */}
                {def.created_by && <p><strong>Создано пользователем ID:</strong> {def.created_by}</p>}
                {/* Отображаем информацию о документе-источнике, даже если ID null */}
                {def.source_document_id !== undefined && (
                  <div>
                    <p>
                      <strong>Источник:</strong>
                      {def.source_document_id === null ? 'Не указан' : (
                        memoizedSourceDocuments[def.source_document_id]?.title || 'Загрузка...'
                      )}
                    </p>
                    <p style={{ marginLeft: '20px' }}>
                      ID: {def.source_document_id === null ? 'null' : def.source_document_id}
                    </p>
                  </div>
                )}
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Source and Year fields might not be directly on the term model from API. */}
      {/* If needed, we would fetch document details to get this info. */}
      {/* For now, removing this section as it's based on mock data. */}
      {/*
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
      */}

      {/* Отображение списка ВНД, связанных с термином */}
      {relatedDocuments.length > 0 && (
        <div className="term-section">
          <h2>Использование во ВНД</h2>
          <div>
            {relatedDocuments.map((doc) => (
              <DocumentItem key={doc.id} document={doc} />
            ))}
          </div>
        </div>
      )}

      {/* Секция для выявления разночтений и отчета о конфликтах */}
      <div className="term-section">
        <h2>Отчет о конфликтах определений</h2>
        {/* Здесь будет отображаться отчет о конфликтах с использованием нового компонента */}
        {conflictsReport && conflictsReport.length > 0 ? (
          <TermConflictReport conflicts={conflictsReport} /> // Передаем отчет в новый компонент
        ) : (
          <p>Конфликты определений не обнаружены.</p>
        )}
      </div>

    </div>
  );
}

export default TermPage; 