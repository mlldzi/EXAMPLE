import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit, faSave, faTimes, faExclamationTriangle } from '@fortawesome/free-solid-svg-icons';

function TermAnalysisItem({
  item, // { term, definition, year } - year используется только при сохранении
  onSave, // Callback function to save the item
  onCancel, // Callback function to cancel editing
  conflicts, // Добавляем пропс для конфликтов
}) {
  const [isEditing, setIsEditing] = useState(false);
  const [editedTerm, setEditedTerm] = useState(item.term);
  const [editedDefinition, setEditedDefinition] = useState(item.definition);
  const [editedYear, setEditedYear] = useState(item.year);

  // Обновляем локальное состояние, если props.item изменился (например, после сохранения)
  useEffect(() => {
    setEditedTerm(item.term);
    setEditedDefinition(item.definition);
    setEditedYear(item.year || '');
  }, [item]);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleSaveClick = () => {
    // Validate data if needed
    if (onSave) {
      const updatedItem = {
        ...item, // Keep original id/keys if any
        term: editedTerm,
        definition: editedDefinition,
        year: editedYear,
      };
      
      onSave(updatedItem);
      setIsEditing(false);
    }
  };

  const handleCancelClick = () => {
    // Reset fields to original item values
    setEditedTerm(item.term);
    setEditedDefinition(item.definition);
    setEditedYear(item.year || '');
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div className="term-analysis-item card">
        {conflicts && conflicts.length > 0 && (
          <div className="conflicts-alert">
            <div className="conflicts-header">
              <FontAwesomeIcon icon={faExclamationTriangle} className="conflicts-icon" />
              <h4>Обнаружены потенциальные конфликты:</h4>
            </div>
            <ul className="conflicts-list">
              {conflicts.map((conflict, idx) => (
                <li key={idx} className="conflict-item">
                  Термин <Link to={`/terms/${conflict.conflicting_term_id}`} className="term-link">"{conflict.conflicting_term_name}"</Link> 
                  <span className="conflict-id">(ID: {conflict.conflicting_term_id})</span> 
                  <div className="conflict-definition">с определением "{conflict.conflicting_definition}"</div>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="form-group">
          <label className="form-label">Термин:</label>
          <input
            type="text"
            value={editedTerm}
            onChange={(e) => setEditedTerm(e.target.value)}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Определение:</label>
          <textarea
            value={editedDefinition}
            onChange={(e) => setEditedDefinition(e.target.value)}
            rows="4"
          />
        </div>
        {/* Скрываем поле год на UI, но сохраняем его в данных */}
        <div style={{ display: 'none' }}>
          <input
            type="text"
            value={editedYear || ''}
            onChange={(e) => setEditedYear(e.target.value)}
          />
        </div>
        <div className="form-buttons">
          <button 
            onClick={handleSaveClick}
            className="btn btn-primary"
          >
            <FontAwesomeIcon icon={faSave} /> Сохранить
          </button>
          <button 
            onClick={handleCancelClick}
            className="btn"
          >
            <FontAwesomeIcon icon={faTimes} /> Отмена
          </button>
        </div>
      </div>
    );
  } else {
    return (
      <div className="term-analysis-item card">
        {conflicts && conflicts.length > 0 && (
          <div className="conflicts-alert">
            <div className="conflicts-header">
              <FontAwesomeIcon icon={faExclamationTriangle} className="conflicts-icon" />
              <h4>Обнаружены потенциальные конфликты:</h4>
            </div>
            <ul className="conflicts-list">
              {conflicts.map((conflict, idx) => (
                <li key={idx} className="conflict-item">
                  Термин <Link to={`/terms/${conflict.conflicting_term_id}`} className="term-link">"{conflict.conflicting_term_name}"</Link> 
                  <span className="conflict-id">(ID: {conflict.conflicting_term_id})</span> 
                  <div className="conflict-definition">с определением "{conflict.conflicting_definition}"</div>
                </li>
              ))}
            </ul>
          </div>
        )}
        <div className="term-info">
          <div className="term-info-item">
            <span className="term-info-label">Термин:</span>
            <span className="term-info-value">{item.term}</span>
          </div>
          <div className="term-info-item">
            <span className="term-info-label">Определение:</span>
            <span className="term-info-value">{item.definition}</span>
          </div>
        </div>
        <button 
          onClick={handleEditClick}
          className="btn"
        >
          <FontAwesomeIcon icon={faEdit} /> Редактировать
        </button>
      </div>
    );
  }
}

export default TermAnalysisItem; 