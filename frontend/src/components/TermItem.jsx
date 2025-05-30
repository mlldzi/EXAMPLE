import React from 'react';
import { Link } from 'react-router-dom';

function TermItem({ term }) {
  // Ожидаем, что term - это объект, полученный от API (например, { id, name, current_definition, ... })
  return (
    <Link to={`/term/${term.id}`} className="term-card">
      <div className="term-header">
        <h3 className="term-name">{term.name}</h3>
        {term.is_approved && (
          <span className="term-badge approved">
            <i className="fas fa-check-circle"></i>
          </span>
        )}
      </div>
      <div className="term-definition">
        <p>{term.current_definition.length > 150 
          ? `${term.current_definition.substring(0, 150)}...` 
          : term.current_definition}
        </p>
      </div>
      {term.tags && term.tags.length > 0 && (
        <div className="term-tags">
          {term.tags.map((tag, index) => (
            <span key={index} className="term-tag">{tag}</span>
          ))}
        </div>
      )}
      <div className="term-card-footer">
        <span className="term-view-more">Подробнее <i className="fas fa-arrow-right"></i></span>
      </div>
    </Link>
  );
}

export default TermItem;
