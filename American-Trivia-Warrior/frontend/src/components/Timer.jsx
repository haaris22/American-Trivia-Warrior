import React, { useEffect, useRef, useState } from 'react';
import './Timer.css';

export default function Timer({ duration, onExpire, paused = false }) {
  const [remaining, setRemaining] = useState(duration);
  const intervalRef = useRef(null);

  useEffect(() => {
    setRemaining(duration);
  }, [duration]);

  useEffect(() => {
    if (paused) {
      clearInterval(intervalRef.current);
      return;
    }
    intervalRef.current = setInterval(() => {
      setRemaining(prev => {
        if (prev <= 1) {
          clearInterval(intervalRef.current);
          onExpire();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(intervalRef.current);
  }, [paused, onExpire]);

  const pct = (remaining / duration) * 100;
  const urgent = remaining <= 10;
  const warning = remaining <= 30;

  const fmt = (s) => `${Math.floor(s / 60)}:${String(s % 60).padStart(2, '0')}`;

  return (
    <div className={`timer ${urgent ? 'timer--urgent' : warning ? 'timer--warning' : ''}`}>
      <div className="timer__display">{fmt(remaining)}</div>
      <div className="timer__bar-track">
        <div className="timer__bar-fill" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
