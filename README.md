# American Trivia Warrior

A web-based trivia game inspired by American Ninja Warrior. Each "obstacle" is a trivia question — one wrong answer and you fall. Complete all 4 stages to be crowned an American Trivia Warrior.

# Web Link
https://american-trivia-warrior.vercel.app/

## Setup

### 1. Clone and install backend dependencies
```bash
cd American-Trivia-Warrior
pip install -r requirements.txt
```

### 2. Configure environment variables

Fill in `.env`:
- `GEMINI_API_KEY` — from [aistudio.google.com](https://aistudio.google.com) 
- `KAGGLE_API_TOKEN` — from [kaggle.com](https://kaggle.com) 

### 3. Load datasets (run once)
```bash
python load_data.py
```
Downloads ~200k Jeopardy questions + OpenTriviaQA dataset via kagglehub. ~ few seconds
### 4. Start backend
```bash
uvicorn backend.server:app --reload
```
On first start, the server generates today's course randomly picking the trivia question associated with each of the 28 course obstacle. 
For each question we prompt Gemini to create 3 MC sets of incorrect distractor answers relevant as of the current day. The 3 sets are quoted as: easy, medium and hard differing based on how outlandish the distractors are compared to the correct answer. (Uses Gemini flash 3.5 — ~30s).

### 5. Start frontend
```bash
cd frontend
npm install
npm start
```

Local: App runs at `http://localhost:3000`.

Note that in stage 3 we have non-MC free-text questions meant to represnt the hardest stage of the "course". The free text responses (capped at 300 characters) are assessed by Gemini against the correct answer to account for typos/extra explanations and such.

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

- **Frontend:** Vercel 
- **Backend:** Render 
