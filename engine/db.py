"""SQLite logbook for every run.

Tables:
  runs      - one row per training job (module, machine, start/end, status, final hold-out score)
  rounds    - one row per round of the self-teaching loop (accuracy, precision, recall, model path)
  mistakes  - every example the model got wrong in a round (with a path to its saved signal)
  credits   - Claude credits you type in by hand
"""
from __future__ import annotations

import json
import sqlite3
import time
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runs (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    module        TEXT NOT NULL,
    machine       TEXT NOT NULL,
    status        TEXT NOT NULL DEFAULT 'running',   -- running | finished | failed
    started_at    REAL NOT NULL,
    finished_at   REAL,
    holdout_accuracy REAL,
    notes         TEXT
);
CREATE TABLE IF NOT EXISTS rounds (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id     INTEGER NOT NULL REFERENCES runs(id),
    round      INTEGER NOT NULL,
    accuracy   REAL,
    precision  REAL,
    recall     REAL,
    n_train    INTEGER,
    n_test     INTEGER,
    n_mistakes INTEGER,
    model_path TEXT,
    extra      TEXT,
    created_at REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS mistakes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id      INTEGER NOT NULL REFERENCES runs(id),
    round       INTEGER NOT NULL,
    example_id  TEXT,
    true_label  TEXT,
    pred_label  TEXT,
    signal_path TEXT,
    created_at  REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS course_attempts (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id        INTEGER REFERENCES runs(id),
    lesson_id     TEXT NOT NULL,
    track         TEXT,
    attempt       INTEGER NOT NULL,
    outcome       TEXT NOT NULL,          -- pass | fail
    score         REAL,
    train_score   REAL,
    threshold     REAL,
    exam_score    REAL,                   -- final hold-out, only scored after a pass
    tried         TEXT,                   -- plain-English: what it tried
    why           TEXT,                   -- plain-English: why it failed
    where_failed  TEXT,                   -- plain-English: under which conditions
    fix_next      TEXT,                   -- plain-English: what it changes next
    strategy      TEXT,                   -- JSON
    details       TEXT,                   -- JSON (confusions, per-class errors, ...)
    mistakes      TEXT,                   -- JSON list of saved example files
    started_at    REAL NOT NULL,
    finished_at   REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS course_status (
    lesson_id   TEXT PRIMARY KEY,
    track       TEXT,
    title       TEXT,
    position    INTEGER,
    status      TEXT NOT NULL,            -- not_started | in_progress | passed | stuck
    attempts    INTEGER DEFAULT 0,
    best_score  REAL,
    exam_score  REAL,
    updated_at  REAL
);
CREATE TABLE IF NOT EXISTS downloads (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    entry_id    TEXT NOT NULL,
    dataset     TEXT,
    bytes       INTEGER,
    status      TEXT,
    seconds     REAL,
    path        TEXT,
    created_at  REAL NOT NULL
);
CREATE TABLE IF NOT EXISTS credits (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    amount     REAL NOT NULL,
    note       TEXT,
    created_at REAL NOT NULL
);
"""

VALID_STATUS = {"running", "finished", "failed"}


class Logbook:
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as c:
            c.executescript(SCHEMA)
            cols = {r[1] for r in c.execute("PRAGMA table_info(runs)")}
            if "data_source" not in cols:   # 'real' | 'synthetic' | 'course'
                c.execute("ALTER TABLE runs ADD COLUMN data_source TEXT DEFAULT 'synthetic'")

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(self.path, timeout=30)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    # --- runs -------------------------------------------------------------
    def start_run(self, module: str, machine: str, notes: str = "", data_source: str = "synthetic") -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO runs (module, machine, status, started_at, notes, data_source) VALUES (?,?,?,?,?,?)",
                (module, machine, "running", time.time(), notes, data_source),
            )
            return cur.lastrowid

    def finish_run(self, run_id: int, status: str = "finished", holdout_accuracy: float | None = None):
        if status not in VALID_STATUS:
            raise ValueError(f"status must be one of {VALID_STATUS}")
        with self._conn() as c:
            c.execute(
                "UPDATE runs SET status=?, finished_at=?, holdout_accuracy=? WHERE id=?",
                (status, time.time(), holdout_accuracy, run_id),
            )

    def runs(self, module: str | None = None, data_source: str | None = None) -> list[dict]:
        q, conds, args = "SELECT * FROM runs", [], []
        if module:
            conds.append("module=?"); args.append(module)
        if data_source:
            conds.append("data_source=?"); args.append(data_source)
        if conds:
            q += " WHERE " + " AND ".join(conds)
        with self._conn() as c:
            return [dict(r) for r in c.execute(q + " ORDER BY id DESC", tuple(args))]

    def running(self) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM runs WHERE status='running' ORDER BY started_at")]

    def module_status(self, module: str) -> str:
        """idle (never run), running, finished or failed (latest run)."""
        rows = self.runs(module)
        return rows[0]["status"] if rows else "idle"

    # --- rounds -----------------------------------------------------------
    def log_round(self, run_id: int, round_no: int, accuracy: float, precision: float, recall: float,
                  n_train: int = 0, n_test: int = 0, n_mistakes: int = 0,
                  model_path: str = "", extra: dict | None = None) -> int:
        with self._conn() as c:
            cur = c.execute(
                "INSERT INTO rounds (run_id, round, accuracy, precision, recall, n_train, n_test,"
                " n_mistakes, model_path, extra, created_at) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (run_id, round_no, accuracy, precision, recall, n_train, n_test, n_mistakes,
                 model_path, json.dumps(extra or {}), time.time()),
            )
            return cur.lastrowid

    def rounds(self, run_id: int) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM rounds WHERE run_id=? ORDER BY round", (run_id,))]

    # --- mistakes ---------------------------------------------------------
    def log_mistakes(self, run_id: int, round_no: int, items: list[dict]):
        now = time.time()
        with self._conn() as c:
            c.executemany(
                "INSERT INTO mistakes (run_id, round, example_id, true_label, pred_label, signal_path, created_at)"
                " VALUES (?,?,?,?,?,?,?)",
                [(run_id, round_no, str(m.get("example_id", "")), str(m["true_label"]),
                  str(m["pred_label"]), m.get("signal_path", ""), now) for m in items],
            )

    def latest_mistakes(self, module: str, limit: int = 12) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute(
                "SELECT m.* FROM mistakes m JOIN runs r ON r.id=m.run_id WHERE r.module=?"
                " ORDER BY m.id DESC LIMIT ?", (module, limit))]

    # --- course -----------------------------------------------------------
    def sync_syllabus(self, lessons: list[dict]):
        """Register every lesson (new ones start as not_started; existing progress is kept)."""
        with self._conn() as c:
            for i, l in enumerate(lessons):
                c.execute("INSERT INTO course_status (lesson_id, track, title, position, status, updated_at)"
                          " VALUES (?,?,?,?, 'not_started', ?) ON CONFLICT(lesson_id) DO UPDATE SET"
                          " track=excluded.track, title=excluded.title, position=excluded.position",
                          (l["id"], l["track"], l["title"], i, time.time()))

    def set_lesson(self, lesson_id: str, **fields):
        fields["updated_at"] = time.time()
        cols = ", ".join(f"{k}=?" for k in fields)
        with self._conn() as c:
            c.execute(f"UPDATE course_status SET {cols} WHERE lesson_id=?", (*fields.values(), lesson_id))

    def reset_course(self):
        with self._conn() as c:
            c.execute("DELETE FROM course_attempts")
            c.execute("UPDATE course_status SET status='not_started', attempts=0, best_score=NULL, exam_score=NULL")

    def log_attempt(self, **row) -> int:
        for k in ("strategy", "details", "mistakes"):
            row[k] = json.dumps(row.get(k), default=float)
        cols = ", ".join(row)
        with self._conn() as c:
            cur = c.execute(f"INSERT INTO course_attempts ({cols}) VALUES ({','.join('?' * len(row))})",
                            tuple(row.values()))
            return cur.lastrowid

    def attempts(self, lesson_id: str | None = None, limit: int = 500) -> list[dict]:
        q, args = "SELECT * FROM course_attempts", ()
        if lesson_id:
            q, args = q + " WHERE lesson_id=?", (lesson_id,)
        with self._conn() as c:
            rows = [dict(r) for r in c.execute(q + " ORDER BY id DESC LIMIT ?", (*args, limit))]
        for r in rows:
            for k in ("strategy", "details", "mistakes"):
                r[k] = json.loads(r[k]) if r[k] else None
        return rows

    def course_status(self) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM course_status ORDER BY position")]

    # --- downloads --------------------------------------------------------
    def log_download(self, entry_id, dataset, nbytes, status, seconds, path):
        with self._conn() as c:
            c.execute("INSERT INTO downloads (entry_id, dataset, bytes, status, seconds, path, created_at)"
                      " VALUES (?,?,?,?,?,?,?)", (entry_id, dataset, nbytes, status, seconds, path, time.time()))

    def downloads(self) -> list[dict]:
        with self._conn() as c:
            return [dict(r) for r in c.execute("SELECT * FROM downloads ORDER BY id DESC")]

    # --- credits ----------------------------------------------------------
    def add_credits(self, amount: float, note: str = ""):
        with self._conn() as c:
            c.execute("INSERT INTO credits (amount, note, created_at) VALUES (?,?,?)", (amount, note, time.time()))

    def total_credits(self) -> float:
        with self._conn() as c:
            return float(c.execute("SELECT COALESCE(SUM(amount),0) FROM credits").fetchone()[0])

    def total_compute_seconds(self) -> float:
        """Sum of wall-clock time of all runs (running ones count up to now)."""
        now = time.time()
        with self._conn() as c:
            row = c.execute(
                "SELECT COALESCE(SUM(COALESCE(finished_at, ?) - started_at), 0) FROM runs", (now,)
            ).fetchone()
            return float(row[0])
