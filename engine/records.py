"""The record book: one permanent entry per experiment, good or bad.

Each entry says what was tried, why, the scores (practice / open test / hidden-once), which rock types or
event types it got right and wrong, whether it beat the best so far, and notes. Stored in the SQLite logbook
(table `records`) and rendered to RECORD_BOOK.md and a web page by `python -m records.build`.

Use from any experiment:
    from engine.records import record
    record(project="FORCE 2020", name="v3", tried="...", why="...", hidden_score=-0.61, ...)
"""
from __future__ import annotations

import json
import sqlite3
import time

from engine.config import database_path

SCHEMA = """
CREATE TABLE IF NOT EXISTS records (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    created_at    REAL NOT NULL,
    project       TEXT NOT NULL,      -- e.g. 'FORCE 2020 (rock type)', 'FORGE DAS (earthquakes)'
    name          TEXT NOT NULL,      -- short id, e.g. 'v3' or 'ladder L2'
    tried         TEXT,               -- what changed, in plain words
    why           TEXT,               -- the reason / hypothesis
    data          TEXT,               -- what data, how much
    open_score    REAL,               -- score on the tuning set (allowed to look at)
    open_accuracy REAL,
    hidden_score  REAL,               -- score on the locked set, scored once (the honest number)
    hidden_accuracy REAL,
    verified      TEXT,               -- how the number was independently checked, if it was
    per_class     TEXT,               -- JSON {class: fraction right}
    outcome       TEXT,               -- 'better' | 'worse' | 'same' | 'stopped' | 'failed' | 'baseline'
    lesson        TEXT,               -- what we learned
    minutes       REAL,
    UNIQUE(project, name)
);
"""


def _conn():
    c = sqlite3.connect(database_path(), timeout=30)
    c.row_factory = sqlite3.Row
    c.executescript(SCHEMA)
    return c


def record(project, name, **fields):
    """Add or update one entry (re-recording the same project+name replaces it)."""
    if "per_class" in fields and not isinstance(fields["per_class"], (str, type(None))):
        fields["per_class"] = json.dumps(fields["per_class"])
    fields.setdefault("created_at", time.time())
    cols = ["project", "name"] + list(fields)
    with _conn() as c:
        c.execute(f"INSERT OR REPLACE INTO records ({','.join(cols)}) VALUES ({','.join('?' * len(cols))})",
                  [project, name] + list(fields.values()))


def all_records(project=None):
    with _conn() as c:
        q, a = "SELECT * FROM records", ()
        if project:
            q, a = q + " WHERE project=?", (project,)
        rows = [dict(r) for r in c.execute(q + " ORDER BY created_at, id", a)]
    for r in rows:
        r["per_class"] = json.loads(r["per_class"]) if r["per_class"] else None
    return rows
