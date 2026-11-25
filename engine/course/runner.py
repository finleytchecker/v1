"""Runs the V1 course: every lesson in course/syllabus.yaml, in order.

For each lesson:
  1. make fresh practice examples and a fresh hidden quiz (answers hidden from the student)
  2. train, answer the quiz, grade it
  3. if it fails: work out why and where, log it, pick a fix, try again
  4. if it passes: sit a final exam on examples it has never seen (the honest score)

Every attempt (pass or fail) goes into the SQLite logbook for the dashboard.
No Claude or paid API is called anywhere here.

Usage:
    python -m engine.course.runner              # continue where it left off
    python -m engine.course.runner --reset      # start the course over
    python -m engine.course.runner --track leak # only one track
"""
from __future__ import annotations

import argparse
import hashlib
import time
from pathlib import Path

import numpy as np
import yaml

from engine.config import PROJECT_ROOT, database_path, load_settings, machine_name
from engine.db import Logbook

from . import features as F
from .diagnose import choose_fix, diagnose
from .generators import REGISTRY
from .learner import MODEL_LADDER, Strategy, correct_mask, fit_predict, score

SYLLABUS = PROJECT_ROOT / "course" / "syllabus.yaml"
MISTAKE_DIR = PROJECT_ROOT / "runs" / "course"


def load_syllabus(path=SYLLABUS) -> list[dict]:
    data = yaml.safe_load(open(path))
    lessons = []
    for track in data["tracks"]:
        for lesson in track["lessons"]:
            lesson = dict(lesson)
            lesson["track"] = track["id"]
            lessons.append(lesson)
    return lessons


def _seed(*parts) -> int:
    return int(hashlib.sha256("|".join(map(str, parts)).encode()).hexdigest()[:8], 16)


def _generate(gen, n, rng, focus=None):
    X, y, meta = gen(n, rng)
    if not focus:
        return X, y, meta
    # extra practice: over-generate and keep the examples in the weak condition
    Xc, yc, mc = gen(n * 4, rng)
    v = np.array([m.get(focus["key"], np.nan) for m in mc], float)
    keep = np.where((v >= focus["lo"]) & (v <= focus["hi"]))[0][: n // 2]
    if len(keep):
        X = np.concatenate([X, Xc[keep]])
        y = np.concatenate([y, yc[keep]])
        meta = list(meta) + [mc[i] for i in keep]
    return X, y, meta


def _save_mistakes(lesson_id, attempt, X, y_true, y_pred, correct, task, limit=6):
    idx = np.where(~correct)[0]
    if task == "regress":
        err = np.abs(np.asarray(y_pred, float) - np.asarray(y_true, float))
        idx = idx[np.argsort(-err[idx])]
    out = []
    d = MISTAKE_DIR / lesson_id / f"attempt_{attempt:02d}"
    d.mkdir(parents=True, exist_ok=True)
    for k, i in enumerate(idx[:limit]):
        p = d / f"mistake_{k}.npy"
        np.save(p, X[i].astype(np.float32))
        out.append(dict(file=str(p.relative_to(PROJECT_ROOT)), true=str(y_true[i]), pred=str(y_pred[i])))
    return out


def _where_text(details):
    w = details.get("where")
    if not w:
        return "Spread evenly across all conditions."
    return f"{w['key']} between {w['lo']:.3g} and {w['hi']:.3g}: {w['error_rate']:.0%} wrong ({w['n']} examples)"


def run_lesson(book: Logbook, lesson: dict, run_id: int, settings: dict, log=print) -> bool:
    cs = settings.get("course", {})
    max_attempts = cs.get("max_attempts", 8)
    lid, ex = lesson["id"], lesson["exercise"]
    gen = REGISTRY[ex["generator"]]["fn"]
    kind = REGISTRY[ex["generator"]]["kind"]
    task, thr = ex["task"], ex["threshold"]
    tol_rel, tol_abs = ex.get("tol_rel", 0.0), ex.get("tol_abs", 0.0)
    base_n, n_test = ex.get("n_train", 300), ex.get("n_test", 300)

    strat = Strategy(features=[F.feature_names(kind)[0]], model=MODEL_LADDER[task][0], n_train=base_n)
    extra_X = extra_y = None
    extra_w = None
    best = 0.0
    book.set_lesson(lid, status="in_progress")
    log(f"\n=== {lesson['track']} / {lesson['title']} (need {thr:.0%}) ===")

    for attempt in range(1, max_attempts + 1):
        t0 = time.time()
        rng_tr = np.random.default_rng(_seed(lid, attempt, "train"))
        rng_te = np.random.default_rng(_seed(lid, attempt, "quiz"))
        Xtr, ytr, _ = _generate(gen, strat.n_train, rng_tr, strat.focus)
        wtr = np.ones(len(ytr))
        if extra_X is not None:
            Xtr = np.concatenate([Xtr, extra_X]); ytr = np.concatenate([ytr, extra_y])
            wtr = np.concatenate([wtr, extra_w])
        Xte, yte, mte = gen(n_test, rng_te)

        model, p_tr, p_te = fit_predict(task, kind, strat, Xtr, ytr, wtr, Xte, seed=attempt)
        s_tr = score(task, ytr, p_tr, tol_rel, tol_abs)["score"]
        sc = score(task, yte, p_te, tol_rel, tol_abs)
        ok = correct_mask(task, yte, p_te, tol_rel, tol_abs)
        best = max(best, sc["score"])
        passed = sc["score"] >= thr
        reasons, why, details = diagnose(task, s_tr, sc["score"], thr, mte, yte, p_te, ok)
        details.update({k: v for k, v in sc.items() if k != "score"})
        mistakes = _save_mistakes(lid, attempt, Xte, yte, p_te, ok, task)
        tried = strat.plain()

        exam = None
        fix = ""
        if passed:
            rng_ex = np.random.default_rng(_seed(lid, "final-exam"))   # never used for training
            Xex, yex, _ = gen(ex.get("n_exam", 600), rng_ex)
            Fex = F.extract(kind, Xex, strat.features)
            exam = score(task, yex, model.predict(Fex), tol_rel, tol_abs)["score"]
            why = "" if exam >= thr - 0.03 else (
                f"Passed the quiz but scored {exam:.0%} on the final exam. It may have tuned itself to the quiz.")
        else:
            new_strat, fix = choose_fix(task, kind, strat, reasons, details, base_n)

        book.log_attempt(run_id=run_id, lesson_id=lid, track=lesson["track"], attempt=attempt,
                         outcome="pass" if passed else "fail", score=sc["score"], train_score=s_tr,
                         threshold=thr, exam_score=exam, tried=tried, why=why,
                         where_failed="" if passed else _where_text(details), fix_next=fix,
                         strategy=strat.as_dict(), details=details, mistakes=mistakes,
                         started_at=t0, finished_at=time.time())
        book.set_lesson(lid, attempts=attempt, best_score=best)
        mark = "PASS" if passed else "FAIL"
        log(f"  attempt {attempt}: {mark} {sc['score']:.1%} (practice {s_tr:.0%}) — tried: {tried}")
        if passed:
            log(f"  final exam (never seen): {exam:.1%}")
            book.set_lesson(lid, status="passed", exam_score=exam)
            return True
        log(f"    why: {why}")
        log(f"    next: {fix}")

        # learn from mistakes: carry the wrong quiz examples into the next practice set
        wrong = ~ok
        if wrong.any():
            extra_X = Xte[wrong] if extra_X is None else np.concatenate([extra_X, Xte[wrong]])[-2000:]
            extra_y = yte[wrong] if extra_y is None else np.concatenate([extra_y, yte[wrong]])[-2000:]
            extra_w = np.full(len(extra_y), new_strat.mistake_weight)
        strat = new_strat

    book.set_lesson(lid, status="stuck")
    log(f"  STUCK after {max_attempts} attempts (best {best:.1%}). Moving on.")
    return False


def run_course(track=None, reset=False, log=print):
    settings = load_settings()
    book = Logbook(database_path(settings))
    lessons = load_syllabus()
    book.sync_syllabus(lessons)
    if reset:
        book.reset_course()
    status = {r["lesson_id"]: r["status"] for r in book.course_status()}
    todo = [l for l in lessons if (track is None or l["track"] == track) and status.get(l["id"]) != "passed"]
    run_id = book.start_run("course", machine_name(settings), notes=f"track={track or 'all'}", data_source="course")
    try:
        results = {l["id"]: run_lesson(book, l, run_id, settings, log) for l in todo}
        book.finish_run(run_id, "finished")
    except BaseException:
        book.finish_run(run_id, "failed")
        raise
    log(f"\nDone: {sum(results.values())}/{len(results)} lessons passed this run.")
    return results


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--track", choices=["shared", "leak", "fluid"])
    ap.add_argument("--reset", action="store_true")
    a = ap.parse_args()
    run_course(a.track, a.reset)
