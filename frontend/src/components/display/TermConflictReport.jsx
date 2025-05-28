import React from 'react';

function TermConflictReport({ conflicts }) {
  return (
    <div>
      {conflicts.map((conflict, index) => (
        <div key={index} style={{ marginBottom: '15px', padding: '10px', border: '1px dashed #f00', borderRadius: '4px' }}>
          <p><strong>Конфликт {index + 1}:</strong></p>
          <div style={{ marginLeft: '10px' }}>
            <p><strong>Определение 1:</strong> {conflict.definition1}</p>
            <p>Документы: {conflict.documents1.join(', ')}</p>
            <p><strong>Определение 2:</strong> {conflict.definition2}</p>
            <p>Документы: {conflict.documents2.join(', ')}</p>
          </div>
        </div>
      ))}
    </div>
  );
}

export default TermConflictReport; 