import React, { useState, useEffect } from 'react';
import termsApi from '../api/terms';
import documentsApi from '../api/documents';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faSave, faTimes, faSpinner, faFileAlt } from '@fortawesome/free-solid-svg-icons';

function CreateTermForm({ onSave, onCancel, apiClient }) {
  const [formData, setFormData] = useState({
    name: '',
    definition: '',
    tags: '',
    source_document_id: ''
  });
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState(null);
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  // Загрузка списка документов для выбора источника
  useEffect(() => {
    const fetchDocuments = async () => {
      setLoadingDocs(true);
      try {
        const response = await documentsApi.getDocuments(apiClient, 0, 100);
        setDocuments(response);
      } catch (err) {
        console.error('Ошибка при загрузке списка документов:', err);
      } finally {
        setLoadingDocs(false);
      }
    };

    fetchDocuments();
  }, [apiClient]);

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

    // Преобразуем идентификатор документа
    const sourceDocId = formData.source_document_id ? formData.source_document_id : null;

    const termData = {
      name: formData.name,
      definition: formData.definition,
      tags: tagsArray,
      source_document_id: sourceDocId
    };

    try {
      // Отправляем данные на бэкенд
      const createdTerm = await termsApi.createTerm(apiClient, termData);
      onSave(createdTerm); // Вызываем callback при успешном создании
    } catch (err) {
      setError('Ошибка при создании термина.');
      console.error('Error creating term:', err);
    } finally {
      setSaving(false);
    }
  };

  return (
    <div className="term-edit-form card">
      <h2>Создать новый термин</h2>
      <form onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="name" className="form-label">Название:</label>
          <input
            type="text"
            id="name"
            name="name"
            value={formData.name}
            onChange={handleInputChange}
            placeholder="Введите название термина"
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
            placeholder="Введите определение термина"
            required
            rows="4"
          />
        </div>
        <div className="form-group">
          <label htmlFor="source_document_id" className="form-label">
            <FontAwesomeIcon icon={faFileAlt} className="form-icon" />
            Документ-источник:
          </label>
          <select
            id="source_document_id"
            name="source_document_id"
            value={formData.source_document_id}
            onChange={handleInputChange}
            className="form-select"
          >
            <option value="">Выберите документ (необязательно)</option>
            {loadingDocs ? (
              <option disabled>Загрузка списка документов...</option>
            ) : (
              documents.map(doc => (
                <option key={doc.id} value={doc.id}>
                  {doc.title} {doc.document_number ? `(№${doc.document_number})` : ''}
                </option>
              ))
            )}
          </select>
          <div className="form-note">
            Указание документа-источника поможет отслеживать происхождение терминов
          </div>
        </div>
        <div className="form-group">
          <label htmlFor="tags" className="form-label">Теги (через запятую):</label>
          <input
            type="text"
            id="tags"
            name="tags"
            value={formData.tags}
            onChange={handleInputChange}
            placeholder="финансы, бухгалтерия, отчетность"
          />
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
                <FontAwesomeIcon icon={faSave} /> Создать
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

export default CreateTermForm; 