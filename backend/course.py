"""
Daily course generation.

Selects questions for all 4 stages, generates Gemini distractors in batches,
caches the full course in SQLite. Same course for everyone on a given day.
"""

import json
import random
from datetime import date

from backend.database import (
    fetch_jeopardy_easy,
    fetch_jeopardy_medium_hard,
    fetch_opentrivia_kids,
    fetch_opentrivia_nonkids,
    fetch_random_any,
    get_today_course,
    save_today_course,
)
from backend.gemini_client import (
    generate_distractors_batch,
    generate_distractors_for_opentrivia_batch,
)

BATCH_SIZE = 5  # questions per Gemini call


def get_or_build_course() -> dict:
    today = date.today().isoformat()
    cached = get_today_course(today)
    if cached:
        return json.loads(cached)
    course = _build_course(today)
    save_today_course(today, json.dumps(course))
    return course


def _build_course(today: str) -> dict:
    seed = int(today.replace("-", ""))
    rng = random.Random(seed)
    used_ids: set = set()

    # ── Select questions ──────────────────────────────────────────────────────

    # Stage 1: 7 Jeopardy easy + 3 OpenTriviaQA kids
    j_easy = fetch_jeopardy_easy(7, used_ids)
    ot_kids = fetch_opentrivia_kids(3, used_ids)
    s1_questions = j_easy + ot_kids
    rng.shuffle(s1_questions)

    # Stage 2: 3 Jeopardy medium/hard + 3 OpenTriviaQA non-kids
    j_med = fetch_jeopardy_medium_hard(3, used_ids)
    ot_non = fetch_opentrivia_nonkids(3, used_ids)
    s2_questions = j_med + ot_non
    rng.shuffle(s2_questions)

    # Stage 3: 8 Jeopardy medium/hard
    s3_questions = fetch_jeopardy_medium_hard(8, used_ids)

    # Stage 4: 4 random from any source
    s4_questions = fetch_random_any(4, used_ids)
    rng.shuffle(s4_questions)

    # ── Generate Gemini distractors ───────────────────────────────────────────

    jeopardy_qs = [
        q for q in (s1_questions + s2_questions + s3_questions + s4_questions)
        if "value" in q  # jeopardy rows have 'value'
    ]
    opentrivia_qs = [
        q for q in (s1_questions + s2_questions + s4_questions)
        if "correct_answer" in q  # opentrivia rows
    ]

    jeopardy_distractors = _batch_generate_jeopardy(jeopardy_qs)
    opentrivia_distractors = _batch_generate_opentrivia(opentrivia_qs)

    # ── Assemble stages ───────────────────────────────────────────────────────

    return {
        "date": today,
        "stages": [
            _build_stage_1(s1_questions, jeopardy_distractors, opentrivia_distractors, rng),
            _build_stage_2(s2_questions, jeopardy_distractors, opentrivia_distractors, rng),
            _build_stage_3(s3_questions, jeopardy_distractors, rng),
            _build_stage_4(s4_questions, jeopardy_distractors, opentrivia_distractors, rng),
        ],
    }


def _batch_generate_jeopardy(questions: list[dict]) -> dict:
    if not questions:
        return {}
    results = {}
    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i: i + BATCH_SIZE]
        payload = [{"id": str(q["id"]), "question": q["question"], "answer": q["answer"]} for q in batch]
        try:
            batch_result = generate_distractors_batch(payload)
            results.update(batch_result)
        except Exception as e:
            print(f"WARNING: Gemini distractor batch failed: {e}")
    return results


def _batch_generate_opentrivia(questions: list[dict]) -> dict:
    if not questions:
        return {}
    results = {}
    for i in range(0, len(questions), BATCH_SIZE):
        batch = questions[i: i + BATCH_SIZE]
        payload = [
            {
                "id": str(q["id"]),
                "question": q["question"],
                "answer": q["correct_answer"],
                "medium_distractors": [q["incorrect_1"], q["incorrect_2"], q["incorrect_3"]],
            }
            for q in batch
        ]
        try:
            batch_result = generate_distractors_for_opentrivia_batch(payload)
            results.update(batch_result)
        except Exception as e:
            print(f"WARNING: Gemini opentrivia batch failed: {e}")
    return results


def _make_mc_question(q: dict, tier: str, j_dist: dict, ot_dist: dict, rng: random.Random, format_type: str = "mc") -> dict:
    is_jeopardy = "value" in q
    q_id = str(q["id"])
    source = "jeopardy" if is_jeopardy else "opentrivia"

    if is_jeopardy:
        correct = q["answer"]
        dist_data = j_dist.get(q_id, {})
        distractors = dist_data.get(tier, dist_data.get("medium", ["A", "B", "C"]))[:3]
    else:
        correct = q["correct_answer"]
        dist_data = ot_dist.get(q_id, {})
        if tier == "medium":
            distractors = [q["incorrect_1"], q["incorrect_2"], q["incorrect_3"]]
        else:
            distractors = dist_data.get(tier, [q["incorrect_1"], q["incorrect_2"], q["incorrect_3"]])[:3]

    if format_type == "free_text":
        return {
            "id": f"{source}_{q_id}",
            "source": source,
            "category": q.get("category", ""),
            "question": q.get("question", ""),
            "format": "free_text",
        }

    options = [correct] + distractors[:3]
    while len(options) < 4:
        options.append("—")
    rng.shuffle(options)
    correct_index = options.index(correct)

    return {
        "id": f"{source}_{q_id}",
        "source": source,
        "category": q.get("category", ""),
        "question": q.get("question", ""),
        "format": "mc",
        "options": options,
        "correct_index": correct_index,
        "distractor_tier": tier,
    }


def _build_stage_1(questions, j_dist, ot_dist, rng) -> dict:
    obstacles = [_make_mc_question(q, "easy", j_dist, ot_dist, rng) for q in questions[:10]]
    return {"stage_num": 1, "name": "Stage 1 — High-Stakes Sprint", "time_limit": 150, "questions": obstacles}


def _build_stage_2(questions, j_dist, ot_dist, rng) -> dict:
    obstacles = []
    for i, q in enumerate(questions[:6]):
        tier = "easy" if i < 3 else "medium"
        obstacles.append(_make_mc_question(q, tier, j_dist, ot_dist, rng))
    return {"stage_num": 2, "name": "Stage 2 — Technical Skills", "time_limit": 240, "questions": obstacles}


def _build_stage_3(questions, j_dist, rng) -> dict:
    obstacles = []
    for i, q in enumerate(questions[:8]):
        if i < 4:
            obstacles.append(_make_mc_question(q, "hard", j_dist, {}, rng))
        else:
            obstacles.append(_make_mc_question(q, "hard", j_dist, {}, rng, format_type="free_text"))
    return {"stage_num": 3, "name": "Stage 3 — Burnout", "time_limit": None, "questions": obstacles}


def _build_stage_4(questions, j_dist, ot_dist, rng) -> dict:
    tiers = ["easy", "medium", "hard"]
    obstacles = []
    for q in questions[:4]:
        tier = rng.choice(tiers)
        obstacles.append(_make_mc_question(q, tier, j_dist, ot_dist, rng))
    return {"stage_num": 4, "name": "Stage 4 — Mt. Midoriyama", "time_limit": 60, "questions": obstacles}
