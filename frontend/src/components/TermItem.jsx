import React from 'react';
import { Link } from 'react-router-dom';

function TermItem({ term }) {
  // Ожидаем, что term - это объект, полученный от API (например, { id, name, current_definition, ... })
  return (
    // Ссылка на страницу термина по его ID
    <Link to={`/term/${term.id}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <div className="term-item">
        {/* Отображаем поле name из объекта термина */}
        <h3>{term.name}</h3>
        {/* Отображаем текущее определение (current_definition) */}
        <p>{term.current_definition ? `${term.current_definition.substring(0, 150)}${term.current_definition.length > 150 ? '...' : ''}` : 'Определение отсутствует'}</p>
      </div>
    </Link>
  );
}

export default TermItem;
