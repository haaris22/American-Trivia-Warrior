import React, { useState, useEffect } from 'react';
import { fetchTodayCourse } from './api';
import Landing from './pages/Landing';
import Stage1 from './pages/Stage1';
import Stage2 from './pages/Stage2';
import Stage3 from './pages/Stage3';
import Stage4 from './pages/Stage4';
import StageComplete from './pages/StageComplete';
import GameOver from './pages/GameOver';
import Winner from './pages/Winner';

// screen values: 'landing' | 'stage' | 'stage-complete' | 'game-over' | 'winner'
const INITIAL_STATE = {
  screen: 'landing',
  currentStage: 1,
  course: null,
  failedAt: null,
};

const STAGE_COMPONENTS = { 1: Stage1, 2: Stage2, 3: Stage3, 4: Stage4 };

export default function App() {
  const [state, setState] = useState(INITIAL_STATE);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (state.screen === 'landing' && !state.course) {
      setLoading(true);
      fetchTodayCourse()
        .then(course => { setState(s => ({ ...s, course })); setLoading(false); })
        .catch(e => { setError(e.message); setLoading(false); });
    }
  }, [state.screen, state.course]);

  const handleStart = () => setState(s => ({ ...s, screen: 'stage', currentStage: 1 }));

  const handleStageComplete = () => {
    if (state.currentStage === 4) {
      setState(s => ({ ...s, screen: 'winner' }));
    } else {
      setState(s => ({ ...s, screen: 'stage-complete' }));
    }
  };

  const handleNextStage = () =>
    setState(s => ({ ...s, screen: 'stage', currentStage: s.currentStage + 1 }));

  const handleFail = (stageNum, obstacleIndex) =>
    setState(s => ({ ...s, screen: 'game-over', failedAt: { stageNum, obstacleIndex } }));

  const handleRestart = () => setState({ ...INITIAL_STATE, course: state.course });

  if (loading) {
    return (
      <div className="loading">
        <h2>LOADING COURSE</h2>
        <p>Building today's obstacle course...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="error">
        <h2>CONNECTION ERROR</h2>
        <p>{error}</p>
        <p>Make sure the backend is running on port 8000.</p>
      </div>
    );
  }

  const { screen, currentStage, course } = state;
  const stageData = course?.stages?.find(s => s.stage_num === currentStage);
  const StageComponent = STAGE_COMPONENTS[currentStage];

  if (screen === 'landing') return <Landing onStart={handleStart} ready={!!course} />;
  if (screen === 'game-over') return <GameOver failedAt={state.failedAt} onRestart={handleRestart} />;
  if (screen === 'winner') return <Winner onRestart={handleRestart} />;
  if (screen === 'stage-complete') return <StageComplete stageNum={currentStage} onNext={handleNextStage} />;
  if (screen === 'stage' && StageComponent && stageData) {
    return (
      <StageComponent
        stageData={stageData}
        onComplete={handleStageComplete}
        onFail={(obstacleIndex) => handleFail(currentStage, obstacleIndex)}
      />
    );
  }

  return <div className="loading"><h2>PREPARING...</h2></div>;
}
