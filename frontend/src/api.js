import axios from 'axios';

const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

export async function fetchTodayCourse() {
  const res = await axios.get(`${API_URL}/api/course/today`);
  return res.data;
}

export async function validateFreeTextAnswer({ questionId, userAnswer, stageNum, obstacleIndex }) {
  const res = await axios.post(`${API_URL}/api/validate`, {
    question_id: questionId,
    user_answer: userAnswer,
    stage_num: stageNum,
    obstacle_index: obstacleIndex,
  });
  return res.data.correct;
}
