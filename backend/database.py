import re
import sqlite3
from pathlib import Path


### TODO: Remove this and design a more robust topic fingerprinting system if we want to enforce topic diversity in Stage 3 and beyond.
_TOPIC_SKIP = frozenset({
    'The', 'This', 'That', 'What', 'Which', 'Who', 'Where', 'When', 'How',
    'His', 'Her', 'Its', 'Their', 'Our', 'Your', 'My', 'And', 'But', 'For',
    'Not', 'All', 'Can', 'Are', 'Was', 'Were', 'Has', 'Have', 'From', 'With',
})


def _extract_topic(text: str) -> str | None:
    """Return the first meaningful capitalized word — used as a topic fingerprint."""
    for word in re.findall(r'\b[A-Z][a-z]{2,}\b', text):
        if word not in _TOPIC_SKIP:
            return word
    return None

DB_PATH = Path("data/trivia.db")


def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def get_today_course(date_str: str):
    with get_connection() as conn:
        row = conn.execute(
            "SELECT course_json FROM daily_courses WHERE course_date = ?", (date_str,)
        ).fetchone()
    return row["course_json"] if row else None


def save_today_course(date_str: str, course_json: str):
    from datetime import datetime
    with get_connection() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO daily_courses (course_date, course_json, generated_at) VALUES (?,?,?)",
            (date_str, course_json, datetime.utcnow().isoformat()),
        )
        conn.commit()


def fetch_jeopardy_easy(n: int, exclude_ids: set) -> list[dict]:
    """$200/$400 Jeopardy or $400/$800 Double Jeopardy."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, category, value, round, question, answer FROM jeopardy_questions
            WHERE (
                (round = 'Jeopardy!' AND value IN (200, 400))
                OR (round = 'Double Jeopardy!' AND value IN (400, 800))
            )
            AND question NOT LIKE '%<a href%'
            AND LENGTH(answer) < 80
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (n * 5,),
        ).fetchall()
    return _filter_exclude([dict(r) for r in rows], exclude_ids, n, "jeopardy")


def fetch_jeopardy_medium_hard(n: int, exclude_ids: set) -> list[dict]:
    """$600+ Jeopardy or $1200+ Double Jeopardy."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT id, category, value, round, question, answer FROM jeopardy_questions
            WHERE (
                (round = 'Jeopardy!' AND value >= 600)
                OR (round = 'Double Jeopardy!' AND value >= 1200)
            )
            AND question NOT LIKE '%<a href%'
            AND LENGTH(answer) < 80
            ORDER BY RANDOM()
            LIMIT ?
            """,
            (n * 5,),
        ).fetchall()
    return _filter_exclude([dict(r) for r in rows], exclude_ids, n, "jeopardy")


def fetch_opentrivia_kids(n: int, exclude_ids: set) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, category, question, correct_answer, incorrect_1, incorrect_2, incorrect_3 FROM opentrivia_questions WHERE is_kids = 1 ORDER BY RANDOM() LIMIT ?",
            (n * 40,),  # large pool needed for topic diversity within single-category file
        ).fetchall()
    return _filter_exclude([dict(r) for r in rows], exclude_ids, n, "opentrivia", max_per_topic=1)


def fetch_opentrivia_nonkids(n: int, exclude_ids: set) -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT id, category, question, correct_answer, incorrect_1, incorrect_2, incorrect_3 FROM opentrivia_questions WHERE is_kids = 0 ORDER BY RANDOM() LIMIT ?",
            (n * 10,),
        ).fetchall()
    return _filter_exclude([dict(r) for r in rows], exclude_ids, n, "opentrivia", max_per_topic=1)


def fetch_random_any(n: int, exclude_ids: set) -> list[dict]:
    """Random questions from either dataset for Stage 4."""
    jeopardy_n = n // 2 + n % 2
    opentrivia_n = n // 2

    jeopardy = fetch_jeopardy_medium_hard(jeopardy_n * 3, exclude_ids)[:jeopardy_n]
    opentrivia = fetch_opentrivia_nonkids(opentrivia_n * 3, exclude_ids)[:opentrivia_n]
    return jeopardy + opentrivia


def _filter_exclude(rows: list[dict], exclude_ids: set, n: int, source: str, max_per_topic: int = 0) -> list[dict]:
    seen_questions = set()
    topic_counts: dict[str, int] = {}
    result = []
    for r in rows:
        key = (source, r["id"])
        q_text = r.get("question", "")
        if key in exclude_ids or q_text in seen_questions:
            continue
        if max_per_topic > 0:
            topic = _extract_topic(q_text)
            if topic and topic_counts.get(topic, 0) >= max_per_topic:
                continue
            if topic:
                topic_counts[topic] = topic_counts.get(topic, 0) + 1
        exclude_ids.add(key)
        seen_questions.add(q_text)
        result.append(r)
        if len(result) >= n:
            break
    return result
