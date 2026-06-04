import React, { useState, useCallback } from 'react';
import ProgressBar from '../components/ProgressBar';
import QuestionMC from '../components/QuestionMC';
import QuestionFreeText from '../components/QuestionFreeText';
import './Stage3.css';

export default function Stage3({ stageData, onComplete, onFail }) {
  const [obstacle, setObstacle] = useState(0);
  const questions = stageData.questions;

  const handleAnswer = useCallback((correct) => {
    if (!correct) { onFail(obstacle); return; }
    if (obstacle + 1 >= questions.length) onComplete();
    else setObstacle(o => o + 1);
  }, [obstacle, questions.length, onComplete, onFail]);

  const q = questions[obstacle];
  const isFreeText = q.format === 'free_text';
  const phase = obstacle < 4 ? 'Hard Distractors' : 'Free Answer — AI Judged';

  return (
    <div className="stage3 stage-wrapper">
      <div className="stage3__header">
        <div>
          <div className="stage3__eyebrow">Stage 3</div>
          <h2 className="stage3__title">Burnout</h2>
          <div className="stage3__phase">{phase}</div>
        </div>
        <div className="stage3__no-timer">
          <div className="stage3__infinity">∞</div>
          <div className="label">No Limit</div>
        </div>
      </div>

      <ProgressBar total={questions.length} current={obstacle} accentVar="var(--red)" />

      <div className="card stage3__card">
        <div className="label" style={{ marginBottom: 8 }}>{q.category}</div>
        {isFreeText ? (
          <QuestionFreeText
            key={obstacle}
            question={q.question}
            questionId={q.id}
            stageNum={3}
            obstacleIndex={obstacle}
            onAnswer={handleAnswer}
            questionNum={obstacle + 1}
            totalQuestions={questions.length}
          />
        ) : (
          <QuestionMC
            key={obstacle}
            question={q.question}
            options={q.options}
            correctIndex={q.correct_index}
            onAnswer={handleAnswer}
            questionNum={obstacle + 1}
            totalQuestions={questions.length}
          />
        )}
      </div>
    </div>
  );
}
