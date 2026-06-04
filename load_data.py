"""
One-time data loading script. Run once before starting the server.

Usage:
    python load_data.py

Requires KAGGLE_API_TOKEN in secrets.env (or set KAGGLE_USERNAME + KAGGLE_KEY for legacy).
Downloads both datasets via kagglehub and loads them into SQLite.
"""

import os
import glob
import json
import sqlite3
from pathlib import Path
from dotenv import load_dotenv

for env_file in ["secrets.env", ".env"]:
    if Path(env_file).exists():
        load_dotenv(env_file)
        break

# kagglehub supports KAGGLE_API_TOKEN 
# If secrets.env uses KAGGLE_API_KEY, remap it to what kagglehub expects.
if os.getenv("KAGGLE_API_KEY") and not os.getenv("KAGGLE_KEY"):
    os.environ["KAGGLE_KEY"] = os.environ["KAGGLE_API_KEY"]

import kagglehub
import pandas as pd

DB_PATH = Path("data/trivia.db")


def get_connection():
    DB_PATH.parent.mkdir(exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_schema(conn):
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS jeopardy_questions (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            category    TEXT,
            value       INTEGER,
            round       TEXT,
            question    TEXT NOT NULL,
            answer      TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS opentrivia_questions (
            id              INTEGER PRIMARY KEY AUTOINCREMENT,
            category        TEXT,
            is_kids         INTEGER DEFAULT 0,
            question        TEXT NOT NULL,
            correct_answer  TEXT NOT NULL,
            incorrect_1     TEXT NOT NULL,
            incorrect_2     TEXT NOT NULL,
            incorrect_3     TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS daily_courses (
            course_date     TEXT PRIMARY KEY,
            course_json     TEXT NOT NULL,
            generated_at    TEXT NOT NULL
        );

        CREATE INDEX IF NOT EXISTS idx_jeopardy_value ON jeopardy_questions(value);
        CREATE INDEX IF NOT EXISTS idx_jeopardy_round ON jeopardy_questions(round);
        CREATE INDEX IF NOT EXISTS idx_opentrivia_kids ON opentrivia_questions(is_kids);
    """)
    conn.commit()


def parse_value(val_str):
    """Parse '$1,200' or '$400' → integer. Returns None for unparseable."""
    if not val_str or str(val_str).strip() in ("", "None", "nan"):
        return None
    cleaned = str(val_str).replace("$", "").replace(",", "").strip()
    try:
        return int(float(cleaned))
    except (ValueError, OverflowError):
        return None


def load_jeopardy(conn):
    count = conn.execute("SELECT COUNT(*) FROM jeopardy_questions").fetchone()[0]
    if count > 0:
        print(f"  jeopardy_questions already populated ({count} rows), skipping")
        return

    print("  Downloading Jeopardy dataset via kagglehub...")
    path = kagglehub.dataset_download("ulrikthygepedersen/200000-jeopardy-questions")
    print(f"  Downloaded to: {path}")

    csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {path}")

    csv_path = csv_files[0]
    print(f"  Loading: {csv_path}")
    df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
    print(f"  Columns: {list(df.columns)}")

    # Normalize column names
    df.columns = [c.strip().lower().replace(" ", "_") for c in df.columns]
    col_map = {
        "show_number": "show_number",
        "air_date": "air_date",
        "round": "round",
        "category": "category",
        "value": "value",
        "question": "question",
        "answer": "answer",
    }

    rows = []
    for _, row in df.iterrows():
        q = str(row.get("question", "")).strip()
        a = str(row.get("answer", "")).strip()
        if not q or not a or q == "nan" or a == "nan":
            continue
        value = parse_value(row.get("value"))
        round_name = str(row.get("round", "")).strip()
        category = str(row.get("category", "")).strip()
        rows.append((category, value, round_name, q, a))

    conn.executemany(
        "INSERT INTO jeopardy_questions (category, value, round, question, answer) VALUES (?,?,?,?,?)",
        rows,
    )
    conn.commit()
    print(f"  Inserted {len(rows)} Jeopardy questions")


def load_opentrivia(conn):
    count = conn.execute("SELECT COUNT(*) FROM opentrivia_questions").fetchone()[0]
    if count > 0:
        print(f"  opentrivia_questions already populated ({count} rows), skipping")
        return

    print("  Downloading OpenTriviaQA dataset via kagglehub...")
    path = kagglehub.dataset_download("mexwell/opentriviaqa-database")
    print(f"  Downloaded to: {path}")

    csv_files = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {path}")

    print(f"  Found {len(csv_files)} category files")

    rows = []
    for csv_path in csv_files:
        filename = os.path.basename(csv_path)
        is_kids = 1 if "for-kids" in filename else 0
        category = filename.replace("category_", "").replace(".csv", "").replace("-", " ").title()

        try:
            df = pd.read_csv(csv_path, encoding="utf-8", on_bad_lines="skip")
        except Exception as e:
            print(f"  WARNING: could not read {filename}: {e}")
            continue

        df.columns = [c.strip().lower() for c in df.columns]

        # Schema: 'question', 'correct' (answer text), 'a'/'b'/'c'/'d' (all options)
        # Wrong answers = whichever of a/b/c/d don't match 'correct'
        question_col = next((c for c in df.columns if "question" in c), None)
        correct_col = next((c for c in df.columns if c == "correct"), None)
        option_cols = [c for c in df.columns if c in ("a", "b", "c", "d")]

        if not question_col or not correct_col or len(option_cols) < 4:
            print(f"  WARNING: unexpected columns in {filename}: {list(df.columns)}, skipping")
            continue

        for _, row in df.iterrows():
            q = str(row.get(question_col, "")).strip()
            correct = str(row.get(correct_col, "")).strip()

            if not q or not correct or q == "nan" or correct == "nan":
                continue

            # Skip True/False questions — they break the MC distractor framework
            if correct.lower() in ("true", "false"):
                continue

            options = [str(row.get(c, "")).strip() for c in option_cols]
            incorrect = [o for o in options if o.lower() != correct.lower() and o and o != "nan"]

            if len(incorrect) < 3:
                continue

            rows.append((category, is_kids, q, correct, incorrect[0], incorrect[1], incorrect[2]))

    conn.executemany(
        "INSERT INTO opentrivia_questions (category, is_kids, question, correct_answer, incorrect_1, incorrect_2, incorrect_3) VALUES (?,?,?,?,?,?,?)",
        rows,
    )
    conn.commit()
    print(f"  Inserted {len(rows)} OpenTriviaQA questions ({sum(1 for r in rows if r[1]==1)} kids, {sum(1 for r in rows if r[1]==0)} non-kids)")


def main():
    print("=" * 60)
    print("American Trivia Warrior — Data Loader")
    print("=" * 60)

    conn = get_connection()
    print("\n[1/3] Creating schema...")
    create_schema(conn)
    print("  Schema ready")

    print("\n[2/3] Loading Jeopardy dataset...")
    load_jeopardy(conn)

    print("\n[3/3] Loading OpenTriviaQA dataset...")
    load_opentrivia(conn)

    total_j = conn.execute("SELECT COUNT(*) FROM jeopardy_questions").fetchone()[0]
    total_o = conn.execute("SELECT COUNT(*) FROM opentrivia_questions").fetchone()[0]
    conn.close()

    print("\n" + "=" * 60)
    print(f"Done. DB at {DB_PATH}")
    print(f"  Jeopardy questions:    {total_j:,}")
    print(f"  OpenTriviaQA questions: {total_o:,}")
    print("\nNext step: python -m uvicorn backend.server:app --reload")


if __name__ == "__main__":
    main()
