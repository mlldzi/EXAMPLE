import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faEdit, faSave, faTimes, faExclamationTriangle, faTrashAlt, faEyeSlash, faEye, faCheck, faExchangeAlt, faHistory } from '@fortawesome/free-solid-svg-icons';

function TermAnalysisItem({
  item, // { term, definition, year, excluded } - year используется только при сохранении, excluded - флаг исключения
  onSave, // Callback function to save the item
  onCancel, // Callback function to cancel editing
  onExclude, // Callback function to exclude the item from analysis
  onResolveConflict, // Функция для разрешения конфликтов
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
        // Сохраняем оригинальное имя для корректной идентификации
        originalTerm: item.originalTerm || item.term
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

  const handleExcludeClick = () => {
    if (onExclude) {
      onExclude(item);
    }
  };
  
  // Обработчики для разрешения конфликтов
  const handleUseExistingDefinition = (conflict) => {
    if (onResolveConflict) {
      // Используем определение из существующего конфликтующего термина
      onResolveConflict({
        ...item,
        definition: conflict.conflicting_definition,
        // Отмечаем, что это было разрешение конфликта
        conflictResolved: true,
        // Сохраняем информацию о разрешенном конфликте
        resolvedConflictInfo: {
          type: 'existing', 
          originalDefinition: item.definition,
          conflictingTerm: conflict.conflicting_term_name,
          conflictingDefinition: conflict.conflicting_definition,
          sourceDocument: conflict.source_document_title
        }
      });
    }
  };
  
  const handleKeepCurrentDefinition = (conflict) => {
    if (onResolveConflict) {
      // Сохраняем текущее определение, но отмечаем, что конфликт был рассмотрен
      onResolveConflict({
        ...item,
        // Не меняем определение, но помечаем, что конфликт рассмотрен
        conflictResolved: true,
        // Сохраняем информацию о разрешенном конфликте
        resolvedConflictInfo: {
          type: 'current',
          originalDefinition: item.definition,
          conflictingTerm: conflict.conflicting_term_name,
          conflictingDefinition: conflict.conflicting_definition,
          sourceDocument: conflict.source_document_title
        }
      });
    }
  };

  // Определяем стили для исключенного термина
  const excludedStyle = item.excluded ? {
    opacity: 0.5,
    backgroundColor: '#f0f0f0',
    border: '1px dashed #ccc',
  } : {};

  // Стиль для разрешенного конфликта
  const resolvedConflictStyle = item.conflictResolved ? {
    border: '1px solid #28a745',
    boxShadow: '0 0 5px rgba(40, 167, 69, 0.3)',
  } : {};
  
  // Стиль для термина с конфликтом
  const conflictStyle = conflicts && conflicts.length > 0 && !item.conflictResolved ? {
    border: '1px solid #ffc107',
    boxShadow: '0 0 5px rgba(255, 193, 7, 0.3)',
  } : {};
  
  // Комбинируем стили
  const cardStyle = {
    ...excludedStyle,
    ...resolvedConflictStyle,
    ...conflictStyle
  };

  if (isEditing) {
    return (
      <div className="term-analysis-item card" style={cardStyle}>
        {conflicts && conflicts.length > 0 && (
          <div className="conflicts-alert" style={{ 
            backgroundColor: '#fff3cd', 
            border: '1px solid #ffeeba', 
            padding: '10px', 
            borderRadius: '4px', 
            marginBottom: '15px' 
          }}>
            <div className="conflicts-header" style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <FontAwesomeIcon icon={faExclamationTriangle} style={{ color: '#f0ad4e', marginRight: '10px' }} />
              <h4 style={{ margin: 0, color: '#856404', fontSize: '16px' }}>Различие в определении термина</h4>
            </div>
            <p style={{ margin: '0 0 10px 0', fontSize: '14px' }}>
              Этот термин уже существует в системе, но с другим определением:
            </p>
            
            <ul className="conflicts-list" style={{ margin: '0', padding: '0 0 0 20px' }}>
              {conflicts.map((conflict, idx) => (
                <li key={idx} style={{ marginBottom: '15px' }}>
                  <div style={{ display: 'flex', gap: '10px', alignItems: 'flex-start' }}>
                    <div style={{ flex: '1' }}>
                      <div style={{ fontSize: '14px', marginBottom: '8px', fontWeight: 'bold' }}>
                        Существующее определение:
                      </div>
                      <div style={{ 
                        padding: '10px', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '4px', 
                        fontSize: '14px', 
                        border: '1px solid #e9ecef' 
                      }}>
                        {conflict.conflicting_definition}
                      </div>
                      {conflict.source_document_title && (
                        <div style={{ fontSize: '13px', marginTop: '5px', color: '#666' }}>
                          <FontAwesomeIcon icon={faHistory} style={{ marginRight: '5px' }} />
                          Источник: {conflict.source_document_title}
                        </div>
                      )}
                    </div>
                    <div style={{ flex: '1' }}>
                      <div style={{ fontSize: '14px', marginBottom: '8px', fontWeight: 'bold' }}>
                        Новое определение:
                      </div>
                      <div style={{ 
                        padding: '10px', 
                        backgroundColor: '#f8f9fa', 
                        borderRadius: '4px', 
                        fontSize: '14px', 
                        border: '1px solid #e9ecef',
                        borderColor: '#bee5eb'
                      }}>
                        {item.definition}
                      </div>
                    </div>
                  </div>
                  
                  <div style={{ display: 'flex', gap: '10px', marginTop: '10px', justifyContent: 'center' }}>
                    <button 
                      onClick={() => handleUseExistingDefinition(conflict)}
                      style={{ 
                        padding: '6px 12px', 
                        backgroundColor: '#17a2b8', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px', 
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      <FontAwesomeIcon icon={faCheck} style={{ marginRight: '5px' }} />
                      Использовать существующее определение
                    </button>
                    <button 
                      onClick={() => handleKeepCurrentDefinition(conflict)}
                      style={{ 
                        padding: '6px 12px', 
                        backgroundColor: '#28a745', 
                        color: 'white', 
                        border: 'none', 
                        borderRadius: '4px', 
                        fontSize: '14px',
                        cursor: 'pointer'
                      }}
                    >
                      <FontAwesomeIcon icon={faExchangeAlt} style={{ marginRight: '5px' }} />
                      Использовать новое определение
                    </button>
                  </div>
                </li>
              ))}
            </ul>
            <div style={{ marginTop: '10px', fontSize: '14px', color: '#856404' }}>
              Выберите, какое определение использовать. При выборе нового определения предыдущее будет сохранено в истории.
            </div>
          </div>
        )}
        
        {item.conflictResolved && (
          <div style={{ 
            backgroundColor: '#d4edda', 
            border: '1px solid #c3e6cb', 
            padding: '10px', 
            borderRadius: '4px', 
            marginBottom: '15px',
            color: '#155724'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <FontAwesomeIcon icon={faCheck} style={{ color: '#28a745', marginRight: '10px' }} />
              <h4 style={{ margin: 0, fontSize: '16px' }}>Конфликт разрешен</h4>
            </div>
            <p style={{ margin: '5px 0' }}>
              {item.resolvedConflictInfo?.type === 'existing' 
                ? 'Принято существующее определение. Новое определение не будет сохранено.' 
                : 'Принято новое определение. Предыдущее определение сохранено в истории.'}
            </p>
            {item.resolvedConflictInfo?.sourceDocument && (
              <p style={{ margin: '5px 0', fontSize: '13px' }}>
                Источник предыдущего определения: {item.resolvedConflictInfo.sourceDocument}
              </p>
            )}
          </div>
        )}
        
        <div className="form-group">
          <label className="form-label">Термин:</label>
          <input
            type="text"
            value={editedTerm}
            onChange={(e) => setEditedTerm(e.target.value)}
            style={{ width: '100%', padding: '8px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ced4da' }}
          />
        </div>
        <div className="form-group">
          <label className="form-label">Определение:</label>
          <textarea
            value={editedDefinition}
            onChange={(e) => setEditedDefinition(e.target.value)}
            rows="4"
            style={{ width: '100%', padding: '8px', marginBottom: '10px', borderRadius: '4px', border: '1px solid #ced4da' }}
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
        <div className="form-buttons" style={{ display: 'flex', gap: '10px' }}>
          <button 
            onClick={handleSaveClick}
            style={{ 
              padding: '6px 12px', 
              backgroundColor: '#28a745', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer'
            }}
          >
            <FontAwesomeIcon icon={faSave} /> Сохранить
          </button>
          <button 
            onClick={handleCancelClick}
            style={{ 
              padding: '6px 12px', 
              backgroundColor: '#6c757d', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer'
            }}
          >
            <FontAwesomeIcon icon={faTimes} /> Отмена
          </button>
        </div>
      </div>
    );
  } else {
    return (
      <div className="term-analysis-item card" style={cardStyle}>
        {item.excluded && (
          <div style={{ 
            backgroundColor: '#f0f0f0', 
            padding: '5px 10px', 
            borderRadius: '4px', 
            marginBottom: '10px',
            color: '#666',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'space-between'
          }}>
            <span>
              <FontAwesomeIcon icon={faEyeSlash} style={{ marginRight: '5px' }} />
              Термин исключен из сохранения
            </span>
          </div>
        )}
        
        {item.conflictResolved && (
          <div style={{ 
            backgroundColor: '#d4edda', 
            border: '1px solid #c3e6cb', 
            padding: '10px', 
            borderRadius: '4px', 
            marginBottom: '15px',
            color: '#155724'
          }}>
            <div style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <FontAwesomeIcon icon={faCheck} style={{ color: '#28a745', marginRight: '10px' }} />
              <h4 style={{ margin: 0, fontSize: '16px' }}>Конфликт разрешен</h4>
            </div>
            <p style={{ margin: '5px 0' }}>
              {item.resolvedConflictInfo?.type === 'existing' 
                ? 'Принято существующее определение' 
                : 'Принято новое определение. Предыдущее определение сохранено в истории.'}
            </p>
            {item.resolvedConflictInfo?.sourceDocument && (
              <p style={{ margin: '5px 0', fontSize: '13px' }}>
                Источник: {item.resolvedConflictInfo.sourceDocument}
              </p>
            )}
          </div>
        )}
        
        {conflicts && conflicts.length > 0 && !item.conflictResolved && (
          <div className="conflicts-alert" style={{ 
            backgroundColor: '#fff3cd', 
            border: '1px solid #ffeeba', 
            padding: '10px', 
            borderRadius: '4px', 
            marginBottom: '15px' 
          }}>
            <div className="conflicts-header" style={{ display: 'flex', alignItems: 'center', marginBottom: '8px' }}>
              <FontAwesomeIcon icon={faExclamationTriangle} style={{ color: '#f0ad4e', marginRight: '10px' }} />
              <h4 style={{ margin: 0, color: '#856404', fontSize: '16px' }}>Различие в определении термина</h4>
            </div>
            <p style={{ margin: '0 0 10px 0', fontSize: '14px' }}>
              Термин "{item.term}" уже существует в системе с другим определением.
            </p>
            
            <div style={{ display: 'flex', gap: '10px', marginTop: '10px', justifyContent: 'center' }}>
              <button 
                onClick={() => handleEditClick()}
                style={{ 
                  padding: '6px 12px', 
                  backgroundColor: '#007bff', 
                  color: 'white', 
                  border: 'none', 
                  borderRadius: '4px', 
                  fontSize: '14px',
                  cursor: 'pointer'
                }}
              >
                <FontAwesomeIcon icon={faEdit} style={{ marginRight: '5px' }} />
                Редактировать и разрешить конфликт
              </button>
            </div>
          </div>
        )}
        
        <div className="term-info">
          <div className="term-info-item">
            <span className="term-info-label" style={{ fontWeight: 'bold', marginRight: '5px' }}>Термин:</span>
            <span className="term-info-value">{item.term}</span>
          </div>
          <div className="term-info-item" style={{ marginTop: '8px' }}>
            <span className="term-info-label" style={{ fontWeight: 'bold', marginRight: '5px' }}>Определение:</span>
            <span className="term-info-value">{item.definition}</span>
          </div>
        </div>
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button 
            onClick={handleEditClick}
            style={{ 
              padding: '6px 12px', 
              backgroundColor: '#007bff', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer'
            }}
          >
            <FontAwesomeIcon icon={faEdit} /> Редактировать
          </button>
          <button 
            onClick={handleExcludeClick}
            style={{ 
              padding: '6px 12px', 
              backgroundColor: item.excluded ? '#28a745' : '#dc3545', 
              color: 'white', 
              border: 'none', 
              borderRadius: '4px', 
              cursor: 'pointer'
            }}
          >
            <FontAwesomeIcon icon={item.excluded ? faEye : faEyeSlash} /> {item.excluded ? 'Включить' : 'Исключить'}
          </button>
        </div>
      </div>
    );
  }
}

export default TermAnalysisItem; 