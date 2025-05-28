import React from 'react';
import { Link } from 'react-router-dom';

function DocumentItem({ document }) {
  // Ожидаем, что document - это объект, полученный от API (соответствующий DocumentPublic)
  return (
    <div style={{
      border: '1px solid #eee',
      padding: '10px',
      marginBottom: '8px',
      borderRadius: '4px',
      backgroundColor: '#fff' // Убираем условное выделение цветом
    }}>
      {/* Отображаем заголовок документа как ссылку */}
      <strong>
        <Link to={`/document/${document.id}`} style={{ textDecoration: 'underline', color: 'blue' }}>
          {document.title}
        </Link>
      </strong>
      {/* Опционально: отображаем номер документа и дату утверждения */}
      {(document.document_number || document.approval_date) && (
        <p style={{ fontSize: '0.9em', color: '#666' }}>
          {document.document_number && <span>Номер: {document.document_number}</span>}
          {document.document_number && document.approval_date && <span>, </span>}
          {document.approval_date && <span>Дата утверждения: {new Date(document.approval_date).toLocaleDateString()}</span>}
        </p>
      )}

      {/* Дополнительная информация о документе */}
      <div style={{ fontSize: '0.9em', color: '#666', marginTop: '8px' }}>
        {document.status && <p><strong>Статус:</strong> {document.status}</p>}
        {document.description && <p><strong>Описание:</strong> {document.description}</p>}
        {document.department && <p><strong>Отдел:</strong> {document.department}</p>}
        {document.tags && document.tags.length > 0 && (
          <p><strong>Теги:</strong> {document.tags.join(', ')}</p>
        )}
      </div>
    </div>
  );
}

export default DocumentItem; 