import React from 'react';
import DocumentUploadForm from '../components/forms/DocumentUploadForm';

function DocumentAnalysisPage() {
  return (
    <div>
      <h2>Анализ документа</h2>
      <DocumentUploadForm />
      {/* Здесь будут отображаться результаты анализа */}
    </div>
  );
}

export default DocumentAnalysisPage; 