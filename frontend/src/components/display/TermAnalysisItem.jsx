import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

function TermAnalysisItem({
  item, // { term, definition, source, year }
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
    setEditedYear(item.year);
  }, [item]);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleSaveClick = () => {
    // Validate data if needed
    if (onSave) {
      onSave({
        ...item, // Keep original id/keys if any
        term: editedTerm,
        definition: editedDefinition,
        year: editedYear,
      });
      setIsEditing(false);
    }
  };

  const handleCancelClick = () => {
    // Reset fields to original item values
    setEditedTerm(item.term);
    setEditedDefinition(item.definition);
    setEditedYear(item.year);
    setIsEditing(false);
  };

  if (isEditing) {
    return (
      <div style={{ marginBottom: '10px', border: '1px solid #ccc', padding: '10px' }}>
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
        <div>
          <label>Термин:</label>
          <input
            type="text"
            value={editedTerm}
            onChange={(e) => setEditedTerm(e.target.value)}
          />
        </div>
        <div>
          <label>Определение:</label>
          <textarea
            value={editedDefinition}
            onChange={(e) => setEditedDefinition(e.target.value)}
            rows="4"
            cols="50"
          />
        </div>
        <div>
          <label>Год:</label>
          <input
            type="text"
            value={editedYear}
            onChange={(e) => setEditedYear(e.target.value)}
          />
        </div>
        {/* Отображение источника, если есть, нередактируемым */}
        {item.source && <p><strong>Источник:</strong> {item.source}</p>}
        <div>
          <button onClick={handleSaveClick}>Сохранить изменения</button>
          <button onClick={handleCancelClick}>Отмена</button>
        </div>
      </div>
    );
  } else {
    return (
      <div style={{ marginBottom: '10px', border: '1px solid #ccc', padding: '10px' }}>
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
        {item.source && <p><strong>Источник:</strong> {item.source}</p>}
        {item.year && <p><strong>Год:</strong> {item.year}</p>}
        <button onClick={handleEditClick}>Редактировать</button>
      </div>
    );
  }
}

export default TermAnalysisItem; 