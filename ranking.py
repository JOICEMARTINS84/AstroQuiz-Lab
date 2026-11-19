"""Ranking compartilhado entre sessões da mesma instância do AstroQuiz."""
import os
import sqlite3
import unicodedata
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.environ.get("ASTROQUIZ_RANKING_DB", str(Path(__file__).resolve().parent / ".astroquiz-ranking.sqlite3")))
MODES = ("Treino comentado", "Simulado")
DURATIONS = (0, 30, 45, 60, 90, 120)

@contextmanager
def database():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    db = sqlite3.connect(DB_PATH, timeout=10)
    db.row_factory = sqlite3.Row
    try:
        db.execute("""CREATE TABLE IF NOT EXISTS scores (
            mission TEXT PRIMARY KEY,
            nickname TEXT NOT NULL,
            nickname_key TEXT NOT NULL,
            level INTEGER NOT NULL CHECK(level BETWEEN 1 AND 5),
            mode TEXT NOT NULL,
            duration INTEGER NOT NULL,
            hits INTEGER NOT NULL CHECK(hits BETWEEN 0 AND 10),
            elapsed INTEGER NOT NULL CHECK(elapsed >= 0),
            created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")
        db.execute("""CREATE INDEX IF NOT EXISTS scores_category
            ON scores(level, mode, duration, hits DESC, elapsed ASC)""")
        yield db
        db.commit()
    finally:
        db.close()

def clean_nickname(value):
    nickname = " ".join(unicodedata.normalize("NFKC", str(value)).split())
    if not 2 <= len(nickname) <= 24:
        raise ValueError("Escolha um apelido de 2 a 24 caracteres.")
    if not all(c.isalnum() or c in " _-." for c in nickname):
        raise ValueError("Use apenas letras, números, espaços, pontos, hífens ou sublinhados.")
    return nickname

def save_score(mission, nickname, level, mode, duration, hits, elapsed):
    nickname = clean_nickname(nickname)
    if level not in range(1, 6) or mode not in MODES or duration not in DURATIONS:
        raise ValueError("Categoria de ranking inválida.")
    if not isinstance(hits, int) or not 0 <= hits <= 10 or not isinstance(elapsed, int) or elapsed < 0:
        raise ValueError("Resultado inválido.")
    with database() as db:
        cursor = db.execute("""INSERT INTO scores
            (mission, nickname, nickname_key, level, mode, duration, hits, elapsed)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(mission) DO NOTHING""",
            (mission, nickname, nickname.casefold(), level, mode, duration, hits, elapsed))
        return cursor.rowcount == 1

def leaderboard(level, mode, duration, limit=20):
    # One best attempt per nickname in each category; faster time breaks ties.
    with database() as db:
        rows = db.execute("""WITH best AS (
            SELECT nickname, hits, elapsed, created_at, mission,
            ROW_NUMBER() OVER (
                PARTITION BY nickname_key
                ORDER BY hits DESC, elapsed ASC, created_at ASC, mission ASC
            ) AS attempt
            FROM scores WHERE level=? AND mode=? AND duration=?
        )
        SELECT nickname, hits, elapsed FROM best
        WHERE attempt=1
        ORDER BY hits DESC, elapsed ASC, created_at ASC, mission ASC
        LIMIT ?""", (level, mode, duration, limit)).fetchall()
        return [dict(row) for row in rows]
