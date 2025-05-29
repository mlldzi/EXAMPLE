import React, { useState } from 'react';

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
    <div style={{ marginBottom: '20px' }}>
      <h3>Загрузка документа для анализа</h3>
      {/* Поле ввода файла */}
      <input type="file" onChange={handleFileChange} disabled={loading} />

      {/* Кнопка загрузки */}
      <button onClick={handleUploadButtonClick} disabled={!selectedFile || loading}>
        {loading ? 'Загрузка...' : 'Загрузить для анализа'}
      </button>

      {/* Отображение имени выбранного файла */}
      {selectedFile && <p>Выбран файл: {selectedFile.name}</p>}

    </div>
  );
}

export default DocumentUploadForm; 