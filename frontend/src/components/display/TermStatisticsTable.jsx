import React from 'react';

function TermStatisticsTable({ statistics }) {
  if (!statistics || statistics.length === 0) {
    return <p>Статистика терминов не найдена.</p>;
  }

  return (
    <table>
      <thead>
        <tr>
          <th>Термин</th>
          <th>Количество документов</th>
        </tr>
      </thead>
      <tbody>
        {statistics.map((stat) => (
          <tr key={stat.term_id}>
            <td>{stat.term_name || stat.term_id}</td>
            <td>{stat.document_count}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export default TermStatisticsTable; 