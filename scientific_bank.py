"""Banco local de questões científicas traduzidas, com rastreabilidade."""
import json
import sqlite3
from pathlib import Path

SOURCE_FILE = Path(__file__).parent / "data" / "astro_mcq_pt.json"

def scientific_questions():
    records = json.loads(SOURCE_FILE.read_text(encoding="utf-8"))
    with sqlite3.connect(":memory:") as db:
        db.execute("""CREATE TABLE questions (
            id INTEGER PRIMARY KEY, topic TEXT NOT NULL, question TEXT NOT NULL,
            correct TEXT NOT NULL, wrong TEXT NOT NULL, explanation TEXT NOT NULL,
            source TEXT NOT NULL, reference TEXT NOT NULL, adaptation TEXT NOT NULL
        )""")
        for r in records:
            assert len(r["wrong"]) == 3
            assert len(set([r["correct"], *r["wrong"]])) == 4
            db.execute("INSERT INTO questions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (r["id"], r["topic"], r["question"], r["correct"],
                 json.dumps(r["wrong"], ensure_ascii=False), r["explanation"],
                 r["source"], r["reference"], r["adaptation"]))
        result = db.execute("SELECT topic, question, correct, wrong, explanation, id, source FROM questions ORDER BY id").fetchall()
    return [(topic, question, correct, json.loads(wrong),
             f"{explanation} Fonte: {source}, questão {qid} (adaptada).")
            for topic, question, correct, wrong, explanation, qid, source in result]
