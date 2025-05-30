import React, { useState } from 'react';
import { FontAwesomeIcon } from '@fortawesome/react-fontawesome';
import { faExclamationTriangle, faChevronDown, faChevronUp } from '@fortawesome/free-solid-svg-icons';

function TermConflictReport({ conflicts }) {
  const [expandedConflicts, setExpandedConflicts] = useState({});

  const toggleExpand = (index) => {
    setExpandedConflicts(prev => ({
      ...prev,
      [index]: !prev[index]
    }));
  };

  if (!conflicts || conflicts.length === 0) {
    return (
      <div className="no-conflicts-card">
        <FontAwesomeIcon icon={faExclamationTriangle} className="no-conflicts-icon" />
        <p>Конфликты определений не обнаружены</p>
      </div>
    );
  }

  return (
    <div className="conflicts-container">
      {conflicts.map((conflict, index) => {
        const isExpanded = expandedConflicts[index] || false;
        
        return (
          <div key={index} className={`conflict-card ${isExpanded ? 'expanded' : ''}`}>
            <div 
              className="conflict-header" 
              onClick={() => toggleExpand(index)}
            >
              <div className="conflict-title">
                <FontAwesomeIcon icon={faExclamationTriangle} className="conflict-icon" />
                <span>Конфликт {index + 1}</span>
              </div>
              <FontAwesomeIcon 
                icon={isExpanded ? faChevronUp : faChevronDown} 
                className="conflict-toggle-icon" 
              />
            </div>
            
            <div className={`conflict-content ${isExpanded ? 'visible' : ''}`}>
              <div className="conflict-comparison">
                <div className="definition-block definition-first">
                  <h4>Определение 1</h4>
                  <p>{conflict.definition1}</p>
                  <div className="definition-documents">
                    <h5>Документы:</h5>
                    <ul>
                      {conflict.documents1.map((doc, idx) => (
                        <li key={idx}>{doc}</li>
                      ))}
                    </ul>
                  </div>
                </div>
                
                <div className="conflict-divider">
                  <div className="conflict-divider-line"></div>
                  <div className="conflict-vs">VS</div>
                  <div className="conflict-divider-line"></div>
                </div>
                
                <div className="definition-block definition-second">
                  <h4>Определение 2</h4>
                  <p>{conflict.definition2}</p>
                  <div className="definition-documents">
                    <h5>Документы:</h5>
                    <ul>
                      {conflict.documents2.map((doc, idx) => (
                        <li key={idx}>{doc}</li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

export default TermConflictReport; 