import React, { useState, useEffect } from 'react';
import termsApi from '../api/terms';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSave, faTimes, faSpinner } from '@fortawesome/free-solid-svg-icons';

function TermEditForm({ term, onSave, onCancel, apiClient }) {
  const [formData, setFormData] = useState({
    name: '',
    definition: '',
    tags: '',
    is_approved: false,
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Заполняем форму текущими данными термина при открытии
    if (term) {
      setFormData({
        name: term.name || '',
        definition: term.current_definition || '',
        tags: term.tags ? term.tags.join(', ') : '',
        is_approved: term.is_approved || false,
      });
    }
  }, [term]);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prevData => ({
      ...prevData,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setSaving(true);
    setError(null);

    // Преобразуем строку тегов в массив
    const tagsArray = formData.tags.split(',').map(tag => tag.trim()).filter(tag => tag);

    const updatedData = {
      name: formData.name,
      definition: formData.definition,
      tags: tagsArray,
      is_approved: formData.is_approved,
    };

    try {
      // Отправляем обновленные данные на бэкенд
      const updatedTerm = await termsApi.updateTerm(apiClient, term.id, updatedData);
      onSave(updatedTerm); // Вызываем callback при успешном сохранении
    } catch (err) {
      setError('Ошибка при сохранении термина.');
      console.error('Error saving term:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="term-edit-form card">
      <h2>Редактировать термин</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name" className="form-label">Название:</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="definition" className="form-label">Определение:</label>
          <textarea
            id="definition"
            name="definition"
            value={formData.definition}
            onChange={handleInputChange}
            required
          />
        </div>
        <div className="form-group">
          <label htmlFor="tags" className="form-label">Теги (через запятую):</label>
          <input
            type="text"
            id="tags"
            name="tags"
            value={formData.tags}
            onChange={handleInputChange}
          />
        </div>
        <div className="form-group checkbox-group">
          <label htmlFor="is_approved" className="form-label checkbox-label">
            <input
              type="checkbox"
              id="is_approved"
              name="is_approved"
              checked={formData.is_approved}
              onChange={handleInputChange}
            />
            <span>Утвержден</span>
          </label>
        </div>
        {error && <p className="error-message">{error}</p>}
        <div className="form-buttons">
          <button 
            type="submit" 
            className="btn btn-primary" 
            disabled={saving}
          >
            {saving ? (
              <>
                <FontAwesomeIcon icon={faSpinner} spin /> Сохранение...
              </>
            ) : (
              <>
                <FontAwesomeIcon icon={faSave} /> Сохранить
              </>
            )}
          </button>
          <button 
            type="button" 
            className="btn" 
            onClick={onCancel} 
            disabled={saving}
          >
            <FontAwesomeIcon icon={faTimes} /> Отмена
          </button>
        </div>
      </form>
    </div>
  );
}

export default TermEditForm; 