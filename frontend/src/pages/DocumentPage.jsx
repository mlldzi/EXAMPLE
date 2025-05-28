import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import documentsApi from '../api/documents';
import TermItem from '../components/TermItem'; // Возможно, понадобится для отображения связанных терминов

function DocumentPage() {
  const { docId } = useParams(); // Получаем ID документа из URL
  const { apiClient } = useAuth();
  const [documentData, setDocumentData] = useState(null);
  const [relatedTerms, setRelatedTerms] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      setError(null);
      try {
        // Загружаем данные документа и связанные термины параллельно
        const [docData, termsData] = await Promise.all([
          documentsApi.getDocumentById(apiClient, docId), // Загружаем документ
          documentsApi.getTermsForDocument(apiClient, docId), // Загружаем связанные термины
        ]);
        setDocumentData(docData);
        setRelatedTerms(termsData);
        setLoading(false);
      } catch (err) {
        setError('Не удалось загрузить данные документа или связанные термины.');
        setLoading(false);
        console.error(`Error fetching data for document ${docId}:`, err);
      }
    };

    if (docId) {
      fetchData();
    }
  }, [docId, apiClient]);

  if (loading) {
    return <div>Загрузка данных документа...</div>;
  }

  if (error) {
    return <div style={{ color: 'red' }}>Ошибка: {error}</div>;
  }

  if (!documentData) {
    return <div>Документ не найден.</div>;
  }

  // Отображение деталей документа и списка связанных терминов
  return (
    <div>
      <h1>Документ: {documentData.title}</h1>

      <div className="document-details">
        <p><strong>Номер:</strong> {documentData.document_number}</p>
        <p><strong>Дата утверждения:</strong> {documentData.approval_date ? new Date(documentData.approval_date).toLocaleDateString() : 'Не указана'}</p>
        <p><strong>Статус:</strong> {documentData.status}</p>
        {documentData.description && <p><strong>Описание:</strong> {documentData.description}</p>}
        {documentData.department && <p><strong>Отдел:</strong> {documentData.department}</p>}
        {documentData.tags && documentData.tags.length > 0 && (
          <p><strong>Теги:</strong> {documentData.tags.join(', ')}</p>
        )}
        {documentData.document_url && (
          <p><strong>Ссылка:</strong> <a href={documentData.document_url} target="_blank" rel="noopener noreferrer">{documentData.document_url}</a></p>
        )}
         {documentData.created_at && (
          <p><strong>Создан:</strong> {new Date(documentData.created_at).toLocaleString()}</p>
        )}
        {documentData.updated_at && (
          <p><strong>Последнее обновление:</strong> {new Date(documentData.updated_at).toLocaleString()}</p>
        )}
      </div>

      {relatedTerms.length > 0 && (
        <div className="related-terms">
          <h2>Связанные термины</h2>
          <div>
            {relatedTerms.map((term) => (
              <TermItem key={term.id} term={term} />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export default DocumentPage; 