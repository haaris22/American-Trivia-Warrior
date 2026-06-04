import React from 'react';
import './Winner.css';

export default function Winner({ onRestart }) {
  return (
    <div className="winner">
      <div className="winner__content">
        <div className="winner__stars">★ ★ ★</div>
        <div className="winner__badge">All 4 Stages Cleared</div>
        <h1 className="winner__title">AMERICAN<br />TRIVIA<br />WARRIOR</h1>
        <div className="winner__crown">🏆</div>
        <p className="winner__sub">You conquered every obstacle. Come back tomorrow for a new course.</p>
        <button className="btn-secondary winner__cta" onClick={onRestart}>Play Again</button>
      </div>
    </div>
  );
}
