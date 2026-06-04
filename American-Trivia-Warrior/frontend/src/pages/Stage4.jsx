import React, { useState, useCallback } from 'react';
import Timer from '../components/Timer';
import ProgressBar from '../components/ProgressBar';
import QuestionMC from '../components/QuestionMC';
import './Stage4.css';

export default function Stage4({ stageData, onComplete, onFail }) {
  const [obstacle, setObstacle] = useState(0);
  const questions = stageData.questions;

  const handleAnswer = useCallback((correct) => {
    if (!correct) { onFail(obstacle); return; }
    if (obstacle + 1 >= questions.length) onComplete();
    else setObstacle(o => o + 1);
  }, [obstacle, questions.length, onComplete, onFail]);

  const handleExpire = useCallback(() => onFail(obstacle), [obstacle, onFail]);

  const q = questions[obstacle];
  const tierLabels = { easy: 'Easy', medium: 'Medium', hard: 'Hard' };

  return (
    <div className="stage4 stage-wrapper">
      <div className="stage4__header">
        <div>
          <div className="stage4__eyebrow">Stage 4</div>
          <h2 className="stage4__title">MT. MIDORIYAMA</h2>
          <div className="stage4__tier">
            Distractor Level: <span>{tierLabels[q.distractor_tier] || '?'}</span>
          </div>
        </div>
        <Timer duration={stageData.time_limit} onExpire={handleExpire} />
      </div>

      <ProgressBar total={questions.length} current={obstacle} accentVar="var(--gold)" />

      <div className="card stage4__card">
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
