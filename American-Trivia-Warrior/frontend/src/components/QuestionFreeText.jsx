import React, { useState } from 'react';
import { validateFreeTextAnswer } from '../api';
import './QuestionFreeText.css';

export default function QuestionFreeText({ question, questionId, stageNum, obstacleIndex, onAnswer, questionNum, totalQuestions }) {
  const [input, setInput] = useState('');
  const [state, setState] = useState('idle'); // idle | checking | correct | wrong

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!input.trim() || state !== 'idle') return;
    setState('checking');
    try {
      const correct = await validateFreeTextAnswer({
        questionId,
        userAnswer: input.trim(),
        stageNum,
        obstacleIndex,
      });
      setState(correct ? 'correct' : 'wrong');
      setTimeout(() => onAnswer(correct), 1000);
    } catch {
      setState('wrong');
      setTimeout(() => onAnswer(false), 1000);
    }
  };

  return (
    <div className="question-ft">
      <div className="question-ft__meta label">
        Obstacle {questionNum} of {totalQuestions} — Free Answer
      </div>
      <div className="question-ft__question">{question}</div>
      <form className="question-ft__form" onSubmit={handleSubmit}>
        <input
          className={`question-ft__input ${state !== 'idle' ? `question-ft__input--${state}` : ''}`}
          type="text"
          placeholder="Type your answer..."
          value={input}
          onChange={e => setInput(e.target.value)}
          disabled={state !== 'idle'}
          autoFocus
        />
        <button
          type="submit"
          className="btn-primary"
          disabled={!input.trim() || state !== 'idle'}
        >
          {state === 'checking' ? 'Checking...' : 'Submit'}
        </button>
      </form>
      {state === 'correct' && <div className="question-ft__feedback question-ft__feedback--correct">✓ Correct!</div>}
      {state === 'wrong' && <div className="question-ft__feedback question-ft__feedback--wrong">✗ Incorrect</div>}
    </div>
  );
}
