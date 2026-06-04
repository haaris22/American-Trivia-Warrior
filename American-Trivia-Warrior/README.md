# American Trivia Warrior

A web-based trivia game inspired by American Ninja Warrior. Each "obstacle" is a trivia question — one wrong answer and you fall. Complete all 4 stages to be crowned an American Trivia Warrior.

## Setup

### 1. Clone and install backend dependencies
```bash
cd American-Trivia-Warrior
pip install -r requirements.txt
```

### 2. Configure environment variables
```bash
cp .env.example .env
```
Fill in `.env`:
- `GEMINI_API_KEY` — from [aistudio.google.com](https://aistudio.google.com) (free)
- `KAGGLE_USERNAME` + `KAGGLE_KEY` — from [kaggle.com](https://kaggle.com) → Account → API

### 3. Load datasets (run once)
```bash
python load_data.py
```
Downloads ~200k Jeopardy questions + OpenTriviaQA via kagglehub. Takes a few minutes.

### 4. Start backend
```bash
uvicorn backend.server:app --reload
```
On first start, the server generates today's course (Gemini distractor batch — ~30s).

### 5. Start frontend
```bash
cd frontend
npm install
npm start
```

App runs at `http://localhost:3000`.

---

## Architecture

**Backend:** Python + FastAPI. SQLite stores the full question corpus and daily course cache.

**Data:** Jeopardy Kaggle dataset (~200k questions) + OpenTriviaQA Kaggle dataset (pre-made MC questions).

**AI (Gemini 1.5 Flash):**
- Generates 3 difficulty tiers of wrong answers (easy/medium/hard) for each Jeopardy question in the daily course — batched at server startup, cached in SQLite
- Validates free-text answers in Stage 3 in real-time

**Daily course:** Date-seeded random selection from the corpus. Same course for all players each day (Wordle-style). Resets at midnight.

## Stages

| Stage | Name | Questions | Time | Format |
|-------|------|-----------|------|--------|
| 1 | High-Stakes Sprint | 10 | 150s | MC (easy distractors) |
| 2 | Technical Skills | 6 | 240s | MC (easy → medium) |
| 3 | Burnout | 8 | None | MC hard (Q1-4) + Free text (Q5-8) |
| 4 | Mt. Midoriyama | 4 | 60s | MC (random distractor tier) |

## Deployment

- **Frontend:** Vercel — set `REACT_APP_API_URL` to your Render backend URL
- **Backend:** Render — add `GEMINI_API_KEY`, `KAGGLE_USERNAME`, `KAGGLE_KEY` as env vars. Set start command: `python load_data.py && uvicorn backend.server:app --host 0.0.0.0 --port $PORT`
