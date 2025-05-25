import React from 'react';
import { Link } from 'react-router-dom';

function TermItem({ term }) {
  // Ожидаем, что term - это объект { term, definition, source, year }
  return (
    <Link to={`/term/${encodeURIComponent(term.term)}`} style={{ textDecoration: 'none', color: 'inherit' }}>
      <div className="term-item">
        {/* Отображаем поле term из объекта */}
        <h3>{term.term}</h3>
        {/* Можно добавить краткое определение или источник/год, если нужно */}
        {/* <p>{term.definition.substring(0, 100)}...</p> */}
      </div>
    </Link>
  );
}

export default TermItem;
