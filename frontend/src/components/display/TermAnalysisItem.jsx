import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

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
      <div style={{ marginBottom: '10px', padding: '10px' }}>
        {conflicts && conflicts.length > 0 && (
            <div style={{ color: 'orange', marginBottom: '10px' }}>
                <h4>Обнаружены потенциальные конфликты:</h4>
                <ul>
                    {conflicts.map((conflict, idx) => (
                        <li key={idx}>
                            Термин <Link to={`/terms/${conflict.conflicting_term_id}`}>"{conflict.conflicting_term_name}"</Link> (ID: {conflict.conflicting_term_id}) с определением "{conflict.conflicting_definition}"
                        </li>
                    ))}
                </ul>
            </div>
        )}
        <div style={{ marginBottom: '10px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Термин:</label>
          <input
            type="text"
            value={editedTerm}
            onChange={(e) => setEditedTerm(e.target.value)}
            style={{ width: '100%', padding: '5px' }}
          />
        </div>
        <div style={{ marginBottom: '10px' }}>
          <label style={{ display: 'block', marginBottom: '5px' }}>Определение:</label>
          <textarea
            value={editedDefinition}
            onChange={(e) => setEditedDefinition(e.target.value)}
            rows="4"
            style={{ width: '100%', padding: '5px' }}
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
        <div style={{ display: 'flex', gap: '10px', marginTop: '15px' }}>
          <button 
            onClick={handleSaveClick}
            style={{ padding: '5px 10px', backgroundColor: '#4CAF50', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Сохранить изменения
          </button>
          <button 
            onClick={handleCancelClick}
            style={{ padding: '5px 10px', backgroundColor: '#f44336', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
          >
            Отмена
          </button>
        </div>
      </div>
    );
  } else {
    return (
      <div style={{ marginBottom: '10px', padding: '10px' }}>
        {conflicts && conflicts.length > 0 && (
            <div style={{ color: 'orange', marginBottom: '10px' }}>
                 <h4>Обнаружены потенциальные конфликты:</h4>
                <ul>
                    {conflicts.map((conflict, idx) => (
                        <li key={idx}>
                            Термин <Link to={`/terms/${conflict.conflicting_term_id}`}>"{conflict.conflicting_term_name}"</Link> (ID: {conflict.conflicting_term_id}) с определением "{conflict.conflicting_definition}"
                        </li>
                    ))}
                </ul>
            </div>
        )}
        <p><strong>Термин:</strong> {item.term}</p>
        <p><strong>Определение:</strong> {item.definition}</p>
        {/* Убираем отображение года */}
        <button 
          onClick={handleEditClick}
          style={{ padding: '5px 10px', backgroundColor: '#2196F3', color: 'white', border: 'none', borderRadius: '4px', cursor: 'pointer', marginTop: '10px' }}
        >
          Редактировать
        </button>
      </div>
    );
  }
}

export default TermAnalysisItem; 