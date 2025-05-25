import React from 'react';

function DocumentItem({ document }) {
  return (
    <div style={{
      border: '1px solid #eee',
      padding: '10px',
      marginBottom: '8px',
      borderRadius: '4px',
      backgroundColor: document.hasDiscrepancy ? '#fff0f0' : '#fff' // Выделение цветом при наличии разночтений
    }}>
      <strong>{document.name}</strong>
      {document.hasDiscrepancy && (
        <span style={{ color: 'red', marginLeft: '10px' }}>(Есть разночтение)</span>
      )}
      {/* Здесь можно добавить ссылку на ВНД или другую информацию */}
    </div>
  );
}

export default DocumentItem; 