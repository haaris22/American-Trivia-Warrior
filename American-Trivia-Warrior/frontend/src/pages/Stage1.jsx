import React, { useState, useCallback } from 'react';
import Timer from '../components/Timer';
import ProgressBar from '../components/ProgressBar';
import QuestionMC from '../components/QuestionMC';
import './Stage1.css';

export default function Stage1({ stageData, onComplete, onFail }) {
  const [obstacle, setObstacle] = useState(0);
  const questions = stageData.questions;

  const handleAnswer = useCallback((correct) => {
    if (!correct) { onFail(obstacle); return; }
    if (obstacle + 1 >= questions.length) onComplete();
    else setObstacle(o => o + 1);
  }, [obstacle, questions.length, onComplete, onFail]);

  const handleExpire = useCallback(() => onFail(obstacle), [obstacle, onFail]);

  const q = questions[obstacle];

  return (
    <div className="stage1 stage-wrapper">
      <div className="stage1__header">
        <div>
          <div className="stage1__eyebrow">Stage 1</div>
          <h2 className="stage1__title">High-Stakes Sprint</h2>
        </div>
        <Timer duration={stageData.time_limit} onExpire={handleExpire} />
      </div>

      <ProgressBar total={questions.length} current={obstacle} accentVar="var(--blue)" />

      <div className="card stage1__card">
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
