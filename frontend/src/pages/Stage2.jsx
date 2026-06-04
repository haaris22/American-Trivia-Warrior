import React, { useState, useCallback } from 'react';
import Timer from '../components/Timer';
import ProgressBar from '../components/ProgressBar';
import QuestionMC from '../components/QuestionMC';
import './Stage2.css';

export default function Stage2({ stageData, onComplete, onFail }) {
  const [obstacle, setObstacle] = useState(0);
  const questions = stageData.questions;

  const handleAnswer = useCallback((correct) => {
    if (!correct) { onFail(obstacle); return; }
    if (obstacle + 1 >= questions.length) onComplete();
    else setObstacle(o => o + 1);
  }, [obstacle, questions.length, onComplete, onFail]);

  const handleExpire = useCallback(() => onFail(obstacle), [obstacle, onFail]);

  const q = questions[obstacle];
  const phase = obstacle < 3 ? 'Phase 1 — Easy' : 'Phase 2 — Medium';

  return (
    <div className="stage2 stage-wrapper">
      <div className="stage2__header">
        <div>
          <div className="stage2__eyebrow">Stage 2</div>
          <h2 className="stage2__title">Technical Skills</h2>
          <div className="stage2__phase">{phase}</div>
        </div>
        <Timer duration={stageData.time_limit} onExpire={handleExpire} />
      </div>

      <ProgressBar total={questions.length} current={obstacle} accentVar="var(--purple)" />

      <div className="card stage2__card">
        <div className="label" style={{ marginBottom: 8 }}>{q.category}</div>
        <QuestionMC
          key={obstacle}
          question={q.question}
          options={q.options}
          correctIndex={q.correct_index}
          onAnswer={handleAnswer}
          questionNum={obstacle + 1}
          totalQuestions={questions.length}
        />
      </div>
    </div>
  );
}
