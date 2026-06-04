import React, { useState } from 'react';
import './QuestionMC.css';

export default function QuestionMC({ question, options, correctIndex, onAnswer, questionNum, totalQuestions }) {
  const [selected, setSelected] = useState(null);

  const handleSelect = (idx) => {
    if (selected !== null) return;
    setSelected(idx);
    const correct = idx === correctIndex;
    setTimeout(() => onAnswer(correct), 900);
  };

  const getOptionClass = (idx) => {
    if (selected === null) return 'mc-option';
    if (idx === correctIndex) return 'mc-option mc-option--correct';
    if (idx === selected && idx !== correctIndex) return 'mc-option mc-option--wrong';
    return 'mc-option mc-option--dim';
  };

  return (
    <div className="question-mc">
      <div className="question-mc__meta label">
        Obstacle {questionNum} of {totalQuestions}
      </div>
      <div className="question-mc__question">{question}</div>
      <div className="question-mc__options">
        {options.map((opt, idx) => (
          <button key={idx} className={getOptionClass(idx)} onClick={() => handleSelect(idx)}>
            <span className="mc-option__letter">{String.fromCharCode(65 + idx)}</span>
            <span className="mc-option__text">{opt}</span>
          </button>
        ))}
      </div>
    </div>
  );
}
