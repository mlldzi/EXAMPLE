import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faUpload, faSpinner, faFile } from '@fortawesome/free-solid-svg-icons';

function DocumentUploadForm({ onFileUpload, loading }) {
  const [selectedFile, setSelectedFile] = useState(null);

  const handleFileChange = (event) => {
    // Получаем первый выбранный файл (если пользователь выбрал несколько)
    if (event.target.files && event.target.files.length > 0) {
      setSelectedFile(event.target.files[0]);
    } else {
      setSelectedFile(null);
    }
  };

  const handleUploadButtonClick = () => {
    if (selectedFile && onFileUpload) {
      onFileUpload(selectedFile);
    }
  };

  return (
    <div className="upload-form-container card">
      <h3>Загрузка документа для анализа</h3>
      
      <div className="file-upload-container">
        <label className="file-upload-label">
          <input 
            type="file" 
            onChange={handleFileChange} 
            disabled={loading} 
            className="file-upload-input"
          />
          <span className="file-upload-button">
            <FontAwesomeIcon icon={faFile} /> Выбрать файл
          </span>
        </label>
        
        <button 
          onClick={handleUploadButtonClick} 
          disabled={!selectedFile || loading}
          className="btn btn-primary"
        >
          {loading ? (
            <>
              <FontAwesomeIcon icon={faSpinner} spin /> Загрузка...
            </>
          ) : (
            <>
              <FontAwesomeIcon icon={faUpload} /> Загрузить для анализа
            </>
          )}
        </button>
      </div>

      {/* Отображение имени выбранного файла */}
      {selectedFile && (
        <div className="selected-file">
          <FontAwesomeIcon icon={faFile} className="file-icon" />
          <span>Выбран файл: {selectedFile.name}</span>
        </div>
      )}
    </div>
  );
}

export default DocumentUploadForm; 