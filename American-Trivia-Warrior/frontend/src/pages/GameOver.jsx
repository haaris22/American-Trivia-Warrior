import React from 'react';
import './GameOver.css';

const STAGE_NAMES = { 1: 'High-Stakes Sprint', 2: 'Technical Skills', 3: 'Burnout', 4: 'Mt. Midoriyama' };

export default function GameOver({ failedAt, onRestart }) {
  return (
    <div className="game-over">
      <div className="game-over__bg-text">FALL</div>
      <div className="game-over__content">
        <h1 className="game-over__title">YOU FELL</h1>
        <div className="game-over__detail">
          Stage {failedAt?.stageNum} — {STAGE_NAMES[failedAt?.stageNum]} · Obstacle {failedAt ? failedAt.obstacleIndex + 1 : '?'}
        </div>
        <p className="game-over__sub">The course resets tomorrow. Or try again today.</p>
        <button className="btn-primary game-over__cta" onClick={onRestart}>Try Again</button>
      </div>
    </div>
  );
}
