"""v6: targeted fix for the rocks V1 misses most vs the winner (anhydrite 33% vs 78%, limestone 57% vs 64%).

Process (every step is written to the record book as it happens):
  1. Same features as v5 (layer names, filled curves, penalty-aware answers).
  2. Give extra training weight to the under-predicted rock types. Try several strengths,
     judged ONLY on the open test wells, with the fastest good setting from v5.
  3. Take the best strength, rebuild the v5 blend (top-3 settings x 2 seeds) with those weights,
     train on train + open test, score the hidden wells ONCE.

    python -m benchmarks.force2020.push_v6
"""
from __future__ import annotations

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
from engine.records import record

HERE = Path(__file__).resolve().parent
P = "FORCE 2020 (rock type)"
RARE = {86000: "anhydrite", 70000: "limestone", 70032: "chalk", 88000: "halite", 99000: "tuff", 80000: "marl"}
NAMES = {30000: "sandstone", 65030: "sandstone/shale", 65000: "shale", 80000: "marl", 74000: "dolomite",
         70000: "limestone", 70032: "chalk", 88000: "halite", 86000: "anhydrite", 99000: "tuff", 90000: "coal", 93000: "basement"}
FAST = dict(learning_rate=0.05, max_leaf_nodes=63, max_iter=400, l2_regularization=1.0, min_samples_leaf=20)


def weights(y, strength):
    w = np.ones(len(y))
    for c in RARE:
        w[y == c] = strength
    return w


def per_class(y, p):
    return {NAMES[c]: round(float(np.mean(p[y == c] == c)), 3) for c in np.unique(y)}


def main(log=print):
    t0 = time.time()
    A = penalty_matrix()
    tr, op, hd = v2.load()
    cats = {c: {v: i for i, v in enumerate(sorted(tr[c].dropna().unique()))} for c in ("GROUP", "FORMATION")}
    fills = v2.fill_models(v2.base_features(tr, cats))
    Xtr, Xop, Xhd = (build(d, FIXES, cats, fills) for d in (tr, op, hd))
    ytr, yop, yhd = (d[v2.TARGET].astype(int).to_numpy() for d in (tr, op, hd))
    cat = np.array([c in ("GROUP", "FORMATION") for c in Xtr.columns])

    # step 2: how much extra weight on the rare rocks? (open test only)
    best = None
    for s in (1.0, 2.0, 4.0, 8.0):
        t = time.time()
        m = HistGradientBoostingClassifier(categorical_features=cat, random_state=0, **FAST)
        m.fit(Xtr, ytr, sample_weight=weights(ytr, s))
        p = v2.min_penalty_decision(m.predict_proba(Xop), m.classes_, A)
        sc, acc = v2.score(yop, p, A), float(np.mean(p == yop))
        pc = per_class(yop, p)
        log(f"  rare-rock weight x{s:g}: open-test {sc:.4f}, accuracy {acc:.1%}, "
            f"anhydrite {pc.get('anhydrite', 0):.0%}, limestone {pc.get('limestone', 0):.0%} ({time.time() - t:.0f}s)")
        record(P, f"v6 test: rare-rock weight x{s:g}", tried=f"training weight x{s:g} on {', '.join(RARE.values())}",
               why="V1 trails the winner most on anhydrite and limestone", data="training wells; judged on open test only",
               open_score=sc, open_accuracy=acc, per_class=pc,
               outcome="baseline" if s == 1.0 else None, minutes=round((time.time() - t) / 60, 1))
        if best is None or sc > best[0]:
            best = (sc, s)
    log(f"  best strength on open test: x{best[1]:g}")

    # step 3: v5 blend with the chosen weights; hidden scored once
    top = [t["params"] for t in json.loads((HERE / "result_push_level1.json").read_text())["best_open"]]
    Xall, yall = pd.concat([Xtr, Xop]), np.concatenate([ytr, yop])
    probs = []
    for kw in top:
        for seed in (0, 1):
            t = time.time()
            m = HistGradientBoostingClassifier(categorical_features=cat, random_state=seed, **kw)
            m.fit(Xall, yall, sample_weight=weights(yall, best[1]))
            probs.append(m.predict_proba(Xhd)); classes = m.classes_
            log(f"  blend model {len(probs)}/6 trained ({time.time() - t:.0f}s)")
    pred = v2.min_penalty_decision(np.mean(probs, axis=0), classes, A)
    res = dict(score=v2.score(yhd, pred, A), accuracy=float(np.mean(pred == yhd)), rare_weight=best[1],
               per_class=per_class(yhd, pred), minutes=round((time.time() - t0) / 60, 1))
    (HERE / "result_v6.json").write_text(json.dumps(res, indent=2))
    pd.DataFrame(dict(WELL=hd.WELL, DEPTH_MD=hd.DEPTH_MD, true=yhd, pred=pred)).to_csv(HERE / "hidden_predictions_v6.csv", index=False)
    prev = -0.4896
    record(P, "v6 rare-rock weighting", tried=f"v5 blend + training weight x{best[1]:g} on rare rocks",
           why="close the anhydrite / limestone gap to the winner", data="train + open test wells; hidden scored once",
           hidden_score=res["score"], hidden_accuracy=res["accuracy"], per_class=res["per_class"],
           outcome="better" if res["score"] > prev + 0.002 else ("worse" if res["score"] < prev - 0.002 else "same"),
           minutes=res["minutes"], verified=None,
           lesson=f"Hidden score {res['score']:.4f} vs v5 {prev:.4f}.")
    log(f"HIDDEN WELLS (scored once): official score {res['score']:.4f}, accuracy {res['accuracy']:.1%} ({res['minutes']} min)")


if __name__ == "__main__":
    main()
