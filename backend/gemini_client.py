import json
import os
import time
from pathlib import Path
from google import genai
from google.genai import types
from dotenv import load_dotenv

for _env in ["secrets.env", ".env"]:
    if Path(_env).exists():
        load_dotenv(_env)
        break

_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
_MODEL = "gemini-3.5-flash"
_JSON_CONFIG = types.GenerateContentConfig(response_mime_type="application/json")


def _call(prompt: str, retries: int = 5) -> str:
    for attempt in range(retries):
        try:
            response = _client.models.generate_content(
                model=_MODEL,
                contents=prompt,
                config=_JSON_CONFIG,
            )
            return response.text
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(5 * (2 ** attempt))  # 5s, 10s, 20s, 40s
            else:
                raise e


def generate_distractors_batch(questions: list[dict]) -> dict:
    """
    questions: list of {id, question, answer}
    Returns: {id: {easy: [...3], medium: [...3], hard: [...3]}}
    """
    formatted = [
        {"id": str(q["id"]), "question": q["question"], "answer": q["answer"]}
        for q in questions
    ]

    prompt = f"""
You are generating wrong answer options for a trivia game.
For each question, generate 3 incorrect answers at 3 difficulty levels:
- easy: clearly wrong, plausible but different domain
- medium: plausible, same general topic, but incorrect
- hard: very similar to correct answer, same sub-category or era, easily confused

Rules:
- Never include the correct answer as a distractor
- Keep distractors concise (similar length to correct answer)
- Distractors should be factually wrong but not nonsensical

Questions:
{json.dumps(formatted, indent=2)}

Return ONLY valid JSON in this exact format:
{{
  "results": [
    {{
      "id": "question_id",
      "easy": ["wrong1", "wrong2", "wrong3"],
      "medium": ["wrong1", "wrong2", "wrong3"],
      "hard": ["wrong1", "wrong2", "wrong3"]
    }}
  ]
}}
"""
    raw = _call(prompt)
    data = json.loads(raw)
    return {item["id"]: item for item in data["results"]}


def generate_distractors_for_opentrivia_batch(questions: list[dict]) -> dict:
    """
    questions: list of {id, question, answer, medium_distractors: [3 strings]}
    Generates only easy and hard tiers (medium already exists from dataset).
    Returns: {id: {easy: [...3], hard: [...3]}}
    """
    formatted = [
        {
            "id": str(q["id"]),
            "question": q["question"],
            "answer": q["answer"],
            "existing_medium_distractors": q["medium_distractors"],
        }
        for q in questions
    ]

    prompt = f"""
You are generating additional wrong answer options for a trivia game.
Each question already has 3 medium-difficulty distractors. Generate 2 more sets:
- easy: clearly wrong, plausible but different domain (easier to eliminate than medium)
- hard: very similar to correct answer, same sub-category or era, harder to eliminate than medium

Questions:
{json.dumps(formatted, indent=2)}

Return ONLY valid JSON:
{{
  "results": [
    {{
      "id": "question_id",
      "easy": ["wrong1", "wrong2", "wrong3"],
      "hard": ["wrong1", "wrong2", "wrong3"]
    }}
  ]
}}
"""
    raw = _call(prompt)
    data = json.loads(raw)
    return {item["id"]: item for item in data["results"]}


def validate_free_text_answer(question: str, correct_answer: str, user_answer: str) -> bool:
    """Returns True if user_answer is an acceptable match for correct_answer."""
    prompt = f"""
You are a trivia judge. Determine if the user's answer is correct or an acceptable variant.

Question: {question}
Correct answer: {correct_answer}
User answered: {user_answer}

Rules:
- Accept common abbreviations, alternate spellings, partial names if unambiguous
- Accept if the core fact is correct even if phrasing differs
- Reject if factually wrong or refers to a different entity

Return ONLY this JSON: {{"correct": true}} or {{"correct": false}}
"""
    raw = _call(prompt)
    data = json.loads(raw)
    return bool(data.get("correct", False))
