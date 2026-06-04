import React from 'react';
import './Landing.css';

export default function Landing({ onStart, ready }) {
  return (
    <div className="landing">
      <div className="landing__content">
        <div className="landing__eyebrow">
          <span>★</span> AMERICAN <span>★</span>
        </div>
        <h1 className="landing__title">TRIVIA<br />WARRIOR</h1>
        <div className="landing__subtitle">4 Stages · 28 Obstacles · One Shot</div>

        <div className="landing__stages">
          {[
            { num: 1, name: 'High-Stakes Sprint',    desc: '10 obstacles · 150s · MC',                   },
            { num: 2, name: 'Technical Skills',       desc: '6 obstacles · 240s · MC',                   },
            { num: 3, name: 'Burnout',   desc: '8 obstacles · No limit · MC + Free Answer', },
            { num: 4, name: 'Mt. Midoriyama',  desc: '4 obstacles · 60s · MC',                    },
          ].map(s => (
            <div key={s.num} className="landing__stage-item">
              <span className="landing__stage-num">Stage {s.num}</span>
              <span className="landing__stage-name">{s.name}</span>
              <span className="landing__stage-desc">{s.desc}</span>
            </div>
          ))}
        </div>

        <div className="landing__rules">
          <p><strong>One wrong answer and you fall.</strong></p>
          <p>Complete all 4 stages to be crowned an American Trivia Warrior.</p>
          <p>One course per day — same for every competitor.</p>
        </div>

        <button className="btn-primary landing__cta" onClick={onStart} disabled={!ready}>
          {ready ? 'Enter the Course' : 'Loading Course...'}
        </button>
      </div>
    </div>
  );
}
