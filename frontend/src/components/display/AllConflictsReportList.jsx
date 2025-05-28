import React from 'react';
import TermConflictReport from './TermConflictReport'; // Import the TermConflictReport component

function AllConflictsReportList({ report }) {
  if (!report || report.length === 0) {
    return <p>Конфликты определений не обнаружены.</p>;
  }

  return (
    <div>
      {report.map((reportEntry) => (
        <div key={reportEntry.term_id} style={{ marginBottom: '15px', padding: '10px', border: '1px dashed #f00', borderRadius: '4px' }}>
          <strong>Термин с конфликтами: {reportEntry.term_id}</strong> {/* Возможно, здесь нужно будет отобразить имя термина */}
          {reportEntry.conflicts && reportEntry.conflicts.length > 0 ? (
            <div>
              {reportEntry.conflicts.map((conflict, index) => (
                 <div key={index} style={{ marginLeft: '10px', marginTop: '10px', border: '1px solid #ffcccc', padding: '8px', borderRadius: '4px' }}>
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
          ) : (
            <p>Нет деталей конфликтов для этого термина.</p>
          )}
        </div>
      ))}
    </div>
  );
}

export default AllConflictsReportList; 