import React, { useEffect, useState, useMemo } from 'react';
import { useParams } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { 
  faHistory, 
  faBook, 
  faInfoCircle, 
  faEdit,
  faExclamationTriangle,
  faCheckCircle,
  faTimesCircle,
  faClock,
  faUser,
  faFileAlt,
  faTags,
  faUserShield
} from '@fortawesome/free-solid-svg-icons';
import DocumentItem from '../components/DocumentItem';
import termsApi from '../api/terms'; // Import the terms API client
import termDocumentRelationsApi from '../api/termDocumentRelations'; // Import relations API client
import TermConflictReport from '../components/display/TermConflictReport'; // Import the new component
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import TermEditForm from '../components/TermEditForm';
import axios from 'axios';

function TermPage() {
  const { termId } = useParams(); // Get termId from URL
  const { apiClient, user } = useAuth(); // Получаем apiClient и user из AuthContext
  const [termData, setTermData] = useState(null);
  const [relatedDocuments, setRelatedDocuments] = useState([]);
  const [conflictsReport, setConflictsReport] = useState(null); // State for conflicts report
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [sourceDocuments, setSourceDocuments] = useState({});
  const [isEditing, setIsEditing] = useState(false); // Новое состояние для управления видимостью формы редактирования
  const [activeTab, setActiveTab] = useState('definition');

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
    return (
      <div className="loading-container">
        <div className="loading-animation">
          <div className="loader"></div>
        </div>
        <p>Загрузка данных термина...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error-container">
        <FontAwesomeIcon icon={faTimesCircle} className="error-icon" />
        <p>Ошибка: {error}</p>
      </div>
    );
  }

  if (!termData) {
    return (
      <div className="not-found-container">
        <FontAwesomeIcon icon={faTimesCircle} className="not-found-icon" />
        <p>Термин не найден.</p>
      </div>
    );
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
    <div className="term-page">
      <div className="term-page-header">
        <h1 className="term-page-title">{termData.name}</h1>
        {user && (
          user.roles?.includes('ADMIN') || 
          user.roles?.includes('MODERATOR')
        ) && (
          <div className="admin-controls">
            <button className="btn-edit" onClick={() => setIsEditing(true)}>
              <FontAwesomeIcon icon={faEdit} />
              <span>Редактировать</span>
            </button>
            {user.roles?.includes('ADMIN') && (
              <div className="admin-badge">
                <FontAwesomeIcon icon={faUserShield} />
                <span>Администратор</span>
              </div>
            )}
          </div>
        )}
      </div>

      <div className="term-status-badge">
        {termData.is_approved ? (
          <span className="badge approved">
            <FontAwesomeIcon icon={faCheckCircle} />
            Утвержден
          </span>
        ) : (
          <span className="badge pending">
            <FontAwesomeIcon icon={faTimesCircle} />
            Не утвержден
          </span>
        )}
      </div>

      <div className="term-navigation">
        <div 
          className={`tab ${activeTab === 'definition' ? 'active' : ''}`}
          onClick={() => setActiveTab('definition')}
        >
          <FontAwesomeIcon icon={faBook} />
          <span>Определение</span>
        </div>
        <div 
          className={`tab ${activeTab === 'history' ? 'active' : ''}`}
          onClick={() => setActiveTab('history')}
        >
          <FontAwesomeIcon icon={faHistory} />
          <span>История</span>
        </div>
        <div 
          className={`tab ${activeTab === 'documents' ? 'active' : ''}`}
          onClick={() => setActiveTab('documents')}
        >
          <FontAwesomeIcon icon={faFileAlt} />
          <span>ВНД</span>
          {relatedDocuments.length > 0 && (
            <span className="tab-badge">{relatedDocuments.length}</span>
          )}
        </div>
        <div 
          className={`tab ${activeTab === 'conflicts' ? 'active' : ''}`}
          onClick={() => setActiveTab('conflicts')}
        >
          <FontAwesomeIcon icon={faExclamationTriangle} />
          <span>Конфликты</span>
          {conflictsReport && conflictsReport.length > 0 && (
            <span className="tab-badge warning">{conflictsReport.length}</span>
          )}
        </div>
      </div>

      <div className="term-content">
        {activeTab === 'definition' && (
          <div className="term-definition-section">
            <div className="definition-card">
              <h2>Определение</h2>
              <div className="definition-text">
                {termData.current_definition || 'Определение отсутствует.'}
              </div>
              
              <div className="term-meta">
                {termData.updated_at && (
                  <div className="meta-item">
                    <FontAwesomeIcon icon={faClock} />
                    <span>Обновлено: {new Date(termData.updated_at).toLocaleString()}</span>
                  </div>
                )}
                
                {termData.approved_at && (
                  <div className="meta-item">
                    <FontAwesomeIcon icon={faCheckCircle} />
                    <span>Утверждено: {new Date(termData.approved_at).toLocaleString()}</span>
                  </div>
                )}
              </div>
              
              {termData.tags && termData.tags.length > 0 && (
                <div className="term-tags">
                  <FontAwesomeIcon icon={faTags} />
                  {termData.tags.map((tag, index) => (
                    <span key={index} className="term-tag">{tag}</span>
                  ))}
                </div>
              )}
            </div>
          </div>
        )}

        {activeTab === 'history' && (
          <div className="term-history-section">
            <h2>
              <FontAwesomeIcon icon={faHistory} />
              История определений
            </h2>
            
            {termData.definitions_history && termData.definitions_history.length > 1 ? (
              <div className="history-timeline">
                {termData.definitions_history.map((def, index) => (
                  <div 
                    key={index} 
                    className={`timeline-item ${index === 0 ? 'current' : ''}`}
                  >
                    <div className="timeline-point"></div>
                    <div className="timeline-content">
                      <div className="timeline-header">
                        <div className="timeline-date">
                          <FontAwesomeIcon icon={faClock} />
                          <span>{def.created_at ? new Date(def.created_at).toLocaleString() : 'Неизвестно'}</span>
                        </div>
                        {index === 0 && (
                          <span className="current-badge">Текущее</span>
                        )}
                      </div>
                      
                      <div className="timeline-definition">
                        {def.definition}
                      </div>
                      
                      <div className="timeline-meta">
                        {def.created_by && (
                          <div className="meta-item">
                            <FontAwesomeIcon icon={faUser} />
                            <span>Создано пользователем ID: {def.created_by}</span>
                          </div>
                        )}
                        
                        {def.source_document_id !== undefined && (
                          <div className="meta-item">
                            <FontAwesomeIcon icon={faFileAlt} />
                            <span>Источник: {
                              def.source_document_id === null 
                              ? 'Не указан' 
                              : (memoizedSourceDocuments[def.source_document_id]?.title || 'Загрузка...')
                            }</span>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="no-history">
                <p>История определений отсутствует.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'documents' && (
          <div className="term-documents-section">
            <h2>
              <FontAwesomeIcon icon={faFileAlt} />
              Использование во ВНД
            </h2>
            
            {relatedDocuments.length > 0 ? (
              <div className="documents-grid">
                {relatedDocuments.map((doc) => (
                  <DocumentItem key={doc.id} document={doc} />
                ))}
              </div>
            ) : (
              <div className="no-documents">
                <p>Термин не найден в нормативных документах.</p>
              </div>
            )}
          </div>
        )}

        {activeTab === 'conflicts' && (
          <div className="term-conflicts-section">
            <h2>
              <FontAwesomeIcon icon={faExclamationTriangle} />
              Отчет о конфликтах определений
            </h2>
            
            <TermConflictReport conflicts={conflictsReport} />
          </div>
        )}
      </div>
    </div>
  );
}

export default TermPage; 