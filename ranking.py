"""Ranking persistente no PostgreSQL; SQLite apenas sem configuração externa."""
import os
import sqlite3
import threading
import streamlit as st
import unicodedata
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(os.environ.get("ASTROQUIZ_RANKING_DB", str(Path(__file__).resolve().parent / ".astroquiz-ranking.sqlite3")))
MODES = ("Treino comentado", "Simulado")
DURATIONS = (0, 30, 45, 60, 90, 120)

class RankingStorageError(OSError):
    """Falha de armazenamento sem expor credenciais."""

_migration_lock = threading.Lock()
_migrated = set()

def settings():
    try:
        return st.secrets.get("ranking_db")
    except FileNotFoundError:
        return None

def persistent_enabled():
    return settings() is not None

def migrate_existing(db, destination):
    # Idempotent import of any old local file that still exists.
    with _migration_lock:
        if destination in _migrated:
            return
        if DB_PATH.is_file():
            with sqlite3.connect(str(DB_PATH), timeout=10) as old:
                rows = old.execute("""SELECT mission, nickname, nickname_key, level,
                    mode, duration, hits, elapsed, created_at FROM scores""").fetchall()
            if rows:
                with db.cursor() as cursor:
                    cursor.executemany("""INSERT INTO public.scores
                        (mission,nickname,nickname_key,level,mode,duration,hits,elapsed,created_at)
                        VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)
                        ON CONFLICT(mission) DO NOTHING""", rows)
        db.commit()
        _migrated.add(destination)

@contextmanager
def database():
    config = settings()
    if config is not None:
        try:
            import psycopg
            from psycopg.rows import dict_row
        except ImportError:
            raise RankingStorageError("Driver PostgreSQL indisponível.") from None
        try:
            conninfo = str(config["connection"]).replace("[YOUR-PASSWORD]", "placeholder").replace("[YOUR-DATABASE-PASSWORD]", "placeholder")
            password = str(config["password"])
            if not password:
                raise RankingStorageError("Senha não configurada.")
            with psycopg.connect(conninfo, password=password, sslmode="require",
                                 connect_timeout=10, row_factory=dict_row) as db:
                migrate_existing(db, conninfo)
                yield db, "%s", "public.scores"
        except (psycopg.Error, sqlite3.Error, KeyError, TypeError, ValueError):
            raise RankingStorageError("Banco externo indisponível.") from None
        return
    with local_database() as db:
        yield db, "?", "scores"

@contextmanager
def local_database():
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
    with database() as (db, placeholder, table):
        cursor = db.execute(f"""INSERT INTO {table}
            (mission, nickname, nickname_key, level, mode, duration, hits, elapsed)
            VALUES ({", ".join([placeholder]*8)})
            ON CONFLICT(mission) DO NOTHING""",
            (mission, nickname, nickname.casefold(), level, mode, duration, hits, elapsed))
        return cursor.rowcount == 1

def leaderboard(level, mode, duration, limit=20):
    # One best attempt per nickname in each category; faster time breaks ties.
    with database() as (db, placeholder, table):
        rows = db.execute(f"""WITH best AS (
            SELECT nickname, hits, elapsed, created_at, mission,
            ROW_NUMBER() OVER (
                PARTITION BY nickname_key
                ORDER BY hits DESC, elapsed ASC, created_at ASC, mission ASC
            ) AS attempt
            FROM {table} WHERE level={placeholder} AND mode={placeholder} AND duration={placeholder}
        )
        SELECT nickname, hits, elapsed FROM best
        WHERE attempt=1
        ORDER BY hits DESC, elapsed ASC, created_at ASC, mission ASC
        LIMIT {placeholder}""", (level, mode, duration, limit)).fetchall()
        return [dict(row) for row in rows]
