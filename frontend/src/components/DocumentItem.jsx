import React from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faFileAlt, faCalendarAlt, faTag, faBuilding, faInfoCircle } from '@fortawesome/free-solid-svg-icons';

function DocumentItem({ document }) {
  // Ожидаем, что document - это объект, полученный от API (соответствующий DocumentPublic)
  return (
    <div className="document-card">
      <div className="document-header">
        <FontAwesomeIcon icon={faFileAlt} className="document-icon" />
        <Link to={`/document/${document.id}`} className="document-link">
          {document.title}
        </Link>
      </div>
      
      {/* Номер документа и дата утверждения */}
      {(document.document_number || document.approval_date) && (
        <div className="document-meta">
          {document.document_number && (
            <div className="meta-item">
              <span className="meta-label">Номер:</span>
              <span className="meta-value">{document.document_number}</span>
            </div>
          )}
          
          {document.approval_date && (
            <div className="meta-item">
              <FontAwesomeIcon icon={faCalendarAlt} className="meta-icon" />
              <span className="meta-label">Дата утверждения:</span>
              <span className="meta-value">{new Date(document.approval_date).toLocaleDateString()}</span>
            </div>
          )}
        </div>
      )}

      {/* Дополнительная информация о документе */}
      <div className="document-details">
        {document.status && (
          <div className="detail-item">
            <FontAwesomeIcon icon={faInfoCircle} className="detail-icon" />
            <span className="detail-label">Статус:</span>
            <span className="detail-value">{document.status}</span>
          </div>
        )}
        
        {document.description && (
          <div className="detail-item description">
            <span className="detail-label">Описание:</span>
            <span className="detail-value">{document.description}</span>
          </div>
        )}
        
        {document.department && (
          <div className="detail-item">
            <FontAwesomeIcon icon={faBuilding} className="detail-icon" />
            <span className="detail-label">Отдел:</span>
            <span className="detail-value">{document.department}</span>
          </div>
        )}
        
        {document.tags && document.tags.length > 0 && (
          <div className="detail-item tags">
            <FontAwesomeIcon icon={faTag} className="detail-icon" />
            <span className="detail-label">Теги:</span>
            <div className="tags-container">
              {document.tags.map((tag, index) => (
                <span key={index} className="document-tag">{tag}</span>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
}

export default DocumentItem; 