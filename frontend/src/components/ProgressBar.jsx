import React from 'react';
import './ProgressBar.css';

export default function ProgressBar({ total, current, accentVar = 'var(--blue)' }) {
  return (
    <div className="progress-bar">
      {Array.from({ length: total }).map((_, i) => {
        const state = i < current ? 'done' : i === current ? 'active' : 'upcoming';
        return (
          <div key={i} className={`progress-bar__node progress-bar__node--${state}`}>
            <div
              className="progress-bar__circle"
              style={state === 'active' ? { borderColor: accentVar, boxShadow: `0 0 10px ${accentVar}` } : {}}
            >
              {i < current ? '✓' : i + 1}
            </div>
            <div className="progress-bar__label">OB {i + 1}</div>
          </div>
        );
      })}
    </div>
  );
}
