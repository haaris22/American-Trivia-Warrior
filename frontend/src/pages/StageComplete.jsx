import React from 'react';
import './StageComplete.css';

const STAGE_NAMES = { 1: 'High-Stakes Sprint', 2: 'Technical Skills', 3: 'Burnout' };
const NEXT_NAMES = { 1: 'Technical Skills', 2: 'Burnout', 3: 'Mt. Midoriyama' };

export default function StageComplete({ stageNum, onNext }) {
  return (
    <div className="stage-complete">
      <div className="stage-complete__bg" />
      <div className="stage-complete__content">
        <div className="stage-complete__badge">STAGE {stageNum} COMPLETE</div>
        <h1 className="stage-complete__name">{STAGE_NAMES[stageNum]}</h1>
        <div className="stage-complete__checkmark">✓</div>
        <p className="stage-complete__sub">
          You cleared the {STAGE_NAMES[stageNum]}. The course isn't over yet.
        </p>
        <div className="stage-complete__next-label">Up Next</div>
        <div className="stage-complete__next-name">Stage {stageNum + 1} — {NEXT_NAMES[stageNum]}</div>
        <button className="btn-primary stage-complete__cta" onClick={onNext}>
          Continue →
        </button>
      </div>
    </div>
  );
}
