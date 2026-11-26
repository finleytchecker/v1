"""Push Level 1 (even playing field) toward the winner, using only what the competition teams were allowed:
tune on the OPEN test wells, then train on train + open test and score the hidden wells ONCE.

Search: model size / learning rate / rounds, then a blend of the best few with different random seeds.

    python -m benchmarks.force2020.push_level1
"""
from __future__ import annotations

import itertools
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from benchmarks.force2020 import run_v2 as v2
from benchmarks.force2020.ladder import FIXES
from benchmarks.force2020.run import penalty_matrix
from benchmarks.force2020.run_v3 import build

HERE = Path(__file__).resolve().parent
GRID = [dict(learning_rate=lr, max_leaf_nodes=ln, max_iter=it, l2_regularization=l2, min_samples_leaf=ms)
        for lr, ln, it, l2, ms in itertools.product((0.05, 0.1), (63, 255), (400, 1000), (0.0, 1.0), (20, 200))]


def main(log=print):
    t0 = time.time()
    A = penalty_matrix()
    tr, op, hd = v2.load()
    cats = {c: {v: i for i, v in enumerate(sorted(tr[c].dropna().unique()))} for c in ("GROUP", "FORMATION")}
    fills = v2.fill_models(v2.base_features(tr, cats))
    Xtr, Xop, Xhd = (build(d, FIXES, cats, fills) for d in (tr, op, hd))
    ytr, yop, yhd = (d[v2.TARGET].astype(int).to_numpy() for d in (tr, op, hd))
    cat = np.array([c in ("GROUP", "FORMATION") for c in Xtr.columns])

    trials = []
    rng = np.random.default_rng(0)
    for kw in [GRID[i] for i in rng.choice(len(GRID), 12, replace=False)]:      # 12 random settings
        t = time.time()
        m = HistGradientBoostingClassifier(categorical_features=cat, random_state=0, **kw).fit(Xtr, ytr)
        P = m.predict_proba(Xop)
        s = v2.score(yop, v2.min_penalty_decision(P, m.classes_, A), A)
        trials.append(dict(params=kw, open_score=s))
        log(f"  {kw} -> open-test {s:.4f} ({time.time() - t:.0f}s)")
    trials.sort(key=lambda r: -r["open_score"])
    best = [t["params"] for t in trials[:3]]

    # blend the 3 best settings x 2 seeds, trained on train + open test; hidden scored once
    Xall, yall = pd.concat([Xtr, Xop]), np.concatenate([ytr, yop])
    probs, classes = [], None
    for kw in best:
        for seed in (0, 1):
            m = HistGradientBoostingClassifier(categorical_features=cat, random_state=seed, **kw).fit(Xall, yall)
            probs.append(m.predict_proba(Xhd)); classes = m.classes_
    pred = v2.min_penalty_decision(np.mean(probs, axis=0), classes, A)
    res = dict(score=v2.score(yhd, pred, A), accuracy=float(np.mean(pred == yhd)), best_open=trials[:3],
               minutes=round((time.time() - t0) / 60, 1))
    (HERE / "result_push_level1.json").write_text(json.dumps(res, indent=2))
    pd.DataFrame(dict(WELL=hd.WELL, DEPTH_MD=hd.DEPTH_MD, true=yhd, pred=pred)).to_csv(
        HERE / "hidden_predictions_v5.csv", index=False)
    log(f"HIDDEN WELLS (scored once): official score {res['score']:.4f}, accuracy {res['accuracy']:.1%} ({res['minutes']} min)")


if __name__ == "__main__":
    main()
