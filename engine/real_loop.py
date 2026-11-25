"""The self-teaching loop on REAL labeled data (shared by Leak and Fluid).

Honesty rules (the hold-out accuracy is the number shown to customers):
  * The final hold-out is a set of whole GROUPS (wells, or blocks of recording time), picked once,
    saved to disk, and never used for training, tuning or choosing between rounds.
  * Splitting by group stops "cheating" through near-identical neighbours (two depth samples 15 cm
    apart in the same well, or two DAS windows a second apart).
  * The hold-out is scored exactly once, at the end.

An adapter (modules/<module>/<dataset>.py) supplies:
  load() -> dict(X, y, groups, ids, feature_names, description)
  synthetic(n, rng, label) -> X  (optional) synthetic examples in the same feature space,
                                   used only to warm up or to fill gaps where real data is thin.
"""
from __future__ import annotations

import json
from pathlib import Path

import joblib
import numpy as np
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from engine.config import PROJECT_ROOT, database_path, load_settings, machine_name
from engine.db import Logbook

LADDER = ["logistic", "random_forest", "gradient_boosting"]


def _model(name, seed):
    m = {"logistic": LogisticRegression(max_iter=3000, class_weight="balanced"),
         "random_forest": RandomForestClassifier(400, random_state=seed, n_jobs=-1, class_weight="balanced"),
         "gradient_boosting": HistGradientBoostingClassifier(random_state=seed, class_weight="balanced")}[name]
    return make_pipeline(StandardScaler(), m)


def _fit(model, X, y, w):
    model.fit(X, y, **{f"{model.steps[-1][0]}__sample_weight": w})
    return model


def grade(y_true, y_pred):
    return dict(accuracy=float(accuracy_score(y_true, y_pred)),
                precision=float(precision_score(y_true, y_pred, average="macro", zero_division=0)),
                recall=float(recall_score(y_true, y_pred, average="macro", zero_division=0)))


def pick_holdout(groups, fraction, seed, path: Path):
    """Choose hold-out groups once and remember them, so every later run uses the same untouched set."""
    if path.exists():
        return set(json.loads(path.read_text()))
    uniq = np.array(sorted(set(groups)))
    rng = np.random.default_rng(seed)
    k = max(1, int(round(fraction * len(uniq))))
    chosen = sorted(map(str, rng.choice(uniq, size=k, replace=False)))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(chosen))
    return set(chosen)


def run(module: str, dataset: str, adapter, log=print, book: Logbook | None = None):
    settings = load_settings()
    L = settings["loop"]
    seed = L.get("seed", 42)
    book = book or Logbook(database_path(settings))
    data = adapter.load()
    X, y = np.asarray(data["X"], float), np.asarray(data["y"]).astype(str)
    groups = np.asarray(data["groups"]).astype(str)
    ids = np.asarray(data.get("ids", np.arange(len(y)))).astype(str)
    out_dir = PROJECT_ROOT / "runs" / module / dataset
    hold = pick_holdout(groups, L.get("holdout_fraction", 0.15), seed, out_dir / "holdout_groups.json")
    in_hold = np.isin(groups, list(hold))
    log(f"{module}/{dataset}: {len(y)} examples, {len(set(groups))} groups; "
        f"hold-out = {sorted(hold)} ({in_hold.sum()} examples, locked away)")
    if len(set(y[in_hold])) < 2:
        log("  warning: the hold-out has only one class, so its accuracy will flatter the model.")

    Xp, yp, gp, idp = X[~in_hold], y[~in_hold], groups[~in_hold], ids[~in_hold]
    w = np.ones(len(yp))
    syn_X = np.empty((0, X.shape[1])); syn_y = np.empty(0, dtype=str)
    run_id = book.start_run(module, machine_name(settings), notes=f"dataset={dataset}", data_source="real")
    run_dir = out_dir / f"run_{run_id:04d}"; run_dir.mkdir(parents=True, exist_ok=True)

    # warm-up: if the adapter can make synthetic examples, start with a few per class
    if hasattr(adapter, "synthetic"):
        rng = np.random.default_rng(seed)
        parts = [(adapter.synthetic(50, rng, c), c) for c in sorted(set(yp))]
        parts = [(a, c) for a, c in parts if a is not None and len(a)]
        if parts:
            syn_X = np.concatenate([a for a, _ in parts]); syn_y = np.concatenate([[c] * len(a) for a, c in parts])
            log(f"  warm-up: {len(syn_y)} synthetic examples added")

    best, best_acc, stale, model_i = None, -1.0, 0, 0
    try:
        uniq = np.array(sorted(set(gp)))
        for r in range(1, L.get("max_rounds", 10) + 1):
            rng = np.random.default_rng(seed + r)
            n_test = max(1, int(round(L.get("test_fraction", 0.2) * len(uniq))))
            test_g = set(rng.choice(uniq, size=n_test, replace=False))
            te = np.isin(gp, list(test_g))
            Xtr = np.concatenate([Xp[~te], syn_X]); ytr = np.concatenate([yp[~te], syn_y])
            wtr = np.concatenate([w[~te], np.full(len(syn_y), 0.5)])   # synthetic counts half
            name = LADDER[model_i]
            model = _fit(_model(name, seed), Xtr, ytr, wtr)
            pred = model.predict(Xp[te])
            g = grade(yp[te], pred)
            wrong = np.where(pred != yp[te])[0]
            mpath = run_dir / f"round_{r:02d}.joblib"
            joblib.dump(model, mpath)
            book.log_round(run_id, r, g["accuracy"], g["precision"], g["recall"], n_train=len(ytr),
                           n_test=int(te.sum()), n_mistakes=len(wrong), model_path=str(mpath.relative_to(PROJECT_ROOT)),
                           extra=dict(model=name, test_groups=sorted(map(str, test_g)), n_synthetic=len(syn_y)))
            te_idx = np.where(te)[0]
            book.log_mistakes(run_id, r, [dict(example_id=idp[te_idx[i]], true_label=yp[te_idx[i]],
                                                pred_label=pred[i]) for i in wrong[:500]])
            log(f"  round {r}: {name:17s} accuracy {g['accuracy']:.1%}  precision {g['precision']:.1%}  "
                f"recall {g['recall']:.1%}  mistakes {len(wrong)}")

            # learn from mistakes: weight them up, and add synthetic look-alikes for the classes it missed
            w[te_idx[wrong]] *= L.get("mistake_weight", 2.0)
            if hasattr(adapter, "synthetic") and len(wrong):
                for c in sorted(set(yp[te][wrong])):
                    extra = adapter.synthetic(L.get("synth_per_mistake", 3) * int((yp[te][wrong] == c).sum()), rng, c)
                    if extra is not None and len(extra):
                        syn_X = np.concatenate([syn_X, extra]); syn_y = np.concatenate([syn_y, [c] * len(extra)])

            if g["accuracy"] > best_acc + L.get("min_improvement", 0.002):
                best_acc, best, stale = g["accuracy"], name, 0
            else:
                stale += 1
                if model_i + 1 < len(LADDER):
                    model_i += 1          # stuck: try a more flexible model
                if stale >= L.get("patience", 3):
                    log("  no improvement for a while: stopping")
                    break

        # final: retrain the best set-up on everything except the hold-out, then score the hold-out ONCE
        final = _fit(_model(best, seed), np.concatenate([Xp, syn_X]), np.concatenate([yp, syn_y]),
                     np.concatenate([w, np.full(len(syn_y), 0.5)]))
        joblib.dump(final, run_dir / "final.joblib")
        hg = grade(y[in_hold], final.predict(X[in_hold]))
        (run_dir / "holdout.json").write_text(json.dumps(dict(hg, groups=sorted(hold), n=int(in_hold.sum()))))
        book.finish_run(run_id, "finished", holdout_accuracy=hg["accuracy"])
        log(f"  HONEST HOLD-OUT ({sorted(hold)}): accuracy {hg['accuracy']:.1%}, precision {hg['precision']:.1%}, "
            f"recall {hg['recall']:.1%}")
        return hg
    except BaseException:
        book.finish_run(run_id, "failed")
        raise
