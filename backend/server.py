import asyncio
import json
import os
from collections import defaultdict
from contextlib import asynccontextmanager
from datetime import date
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, constr

# Max Stage 3 validate calls per IP per day
_VALIDATE_LIMIT = 50
_validate_counts: dict[str, int] = defaultdict(int)
_validate_day: str = ""


def _use_gemini_validate(request: Request) -> bool:
    """Returns True if this IP still has Gemini validate calls remaining today."""
    global _validate_day, _validate_counts
    today = date.today().isoformat()
    if today != _validate_day:
        _validate_day = today
        _validate_counts.clear()
    ip = request.client.host
    if _validate_counts[ip] >= _VALIDATE_LIMIT:
        return False
    _validate_counts[ip] += 1
    return True

for _env in ["secrets.env", ".env"]:
    if Path(_env).exists():
        load_dotenv(_env)
        break

from backend.course import get_or_build_course
from backend.database import get_today_course
from backend.gemini_client import validate_free_text_answer


async def _warm_course():
    print("Building today's course (or loading from cache)...")
    try:
        await asyncio.to_thread(get_or_build_course)
        print("Course ready.")
    except Exception as e:
        print(f"WARNING: Course generation failed: {e}")


@asynccontextmanager
async def lifespan(app: FastAPI):
    if not Path("data/trivia.db").exists():
        print("WARNING: data/trivia.db not found. Run 'python load_data.py' first.")
    else:
        asyncio.create_task(_warm_course())
    yield


app = FastAPI(title="American Trivia Warrior API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://american-trivia-warrior.vercel.app"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/course/today")
def get_course():
    try:
        course = get_or_build_course()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Course generation failed: {e}")

    # Strip correct_answer from free_text questions before sending to client
    safe_course = json.loads(json.dumps(course))
    for stage in safe_course.get("stages", []):
        for q in stage.get("questions", []):
            if q.get("format") == "free_text":
                q.pop("correct_answer", None)

    return safe_course


class ValidateRequest(BaseModel):
    question_id: str
    user_answer: constr(max_length=300)
    stage_num: int
    obstacle_index: int


@app.post("/api/validate")
def validate_answer(req: ValidateRequest, request: Request):
    use_gemini = _use_gemini_validate(request)
    today = date.today().isoformat()
    cached = get_today_course(today)
    if not cached:
        raise HTTPException(status_code=503, detail="Course not ready yet")

    course = json.loads(cached)

    # Find the question in today's course
    target_stage = next(
        (s for s in course["stages"] if s["stage_num"] == req.stage_num), None
    )
    if not target_stage:
        raise HTTPException(status_code=404, detail="Stage not found")

    questions = target_stage["questions"]
    if req.obstacle_index >= len(questions):
        raise HTTPException(status_code=404, detail="Obstacle index out of range")

    question = questions[req.obstacle_index]
    if question.get("format") != "free_text":
        raise HTTPException(status_code=400, detail="This obstacle is not free-text")

    # Retrieve correct answer from full (server-side) course
    server_course = get_or_build_course()
    server_stage = next(
        (s for s in server_course["stages"] if s["stage_num"] == req.stage_num), None
    )
    server_q = server_stage["questions"][req.obstacle_index]

    # Fallback: simple string match before calling Gemini
    correct = server_q.get("answer", server_q.get("correct_answer", ""))
    if req.user_answer.strip().lower() == correct.strip().lower():
        return {"correct": True}

    if not use_gemini:
        is_correct = correct.lower() in req.user_answer.lower() or req.user_answer.lower() in correct.lower()
    else:
        try:
            is_correct = validate_free_text_answer(
                question=question["question"],
                correct_answer=correct,
                user_answer=req.user_answer,
            )
        except Exception:
            is_correct = correct.lower() in req.user_answer.lower() or req.user_answer.lower() in correct.lower()

    return {"correct": is_correct}


@app.get("/api/health")
def health():
    return {"status": "ok", "date": date.today().isoformat()}
