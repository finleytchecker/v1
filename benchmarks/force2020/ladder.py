"""Challenge ladder on FORCE 2020: start with the same conditions as the competition teams, then make it harder.

Level 1  Even playing field   all training data, all curves, official rules (target: beat -0.4690 / 80.5%)
Level 2  Fewer tools          only the 5 most common curves (no density/neutron/PEF), like many older wells
Level 3  Less teaching        learn from only 25 of the 98 training wells
Level 4  New territory        learn from southern wells (quadrants 15-17, 25-26) only; tested on northern hidden wells
Level 5  Messy data           hidden-well logs get 5% noise and missing chunks; the model must cope

Every level: hidden wells scored ONCE with the official penalty matrix; nothing about the hidden wells is used
to train or tune. Uses the fixes version 3 proved helpful: rock-layer names, filled-in curves, penalty-aware answers.

    python -m benchmarks.force2020.ladder            # all levels
    python -m benchmarks.force2020.ladder --level 1
"""
from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from benchmarks.force2020 import run_v2 as v2
from benchmarks.force2020.run import penalty_matrix
from benchmarks.force2020.run_v3 import build

HERE = Path(__file__).resolve().parent
OUT = HERE / "ladder_results.json"
FIXES = ["layer_names", "fill_curves", "penalty_decision"]
COMMON = ["GR", "RDEP", "RMED", "DTC", "CALI"]               # each missing in < 10% of training samples
WINNER = dict(score=-0.4690, accuracy=0.805)
LEVELS = {1: "Even playing field", 2: "Fewer tools", 3: "Less teaching", 4: "New territory", 5: "Messy data"}


def quadrant(well):
    return int(str(well).split("/")[0])


def strip_curves(df):
    df = df.copy()
    for c in v2.NUM:
        if c in df and c not in COMMON:
            df[c] = np.nan
    return df


def mess_up(df, seed=0):
    rng = np.random.default_rng(seed)
    df = df.copy()
    for c in ["GR", "RHOB", "NPHI", "DTC", "RDEP", "RMED", "PEF", "CALI", "SP"]:
        v = df[c].astype(float)
        df[c] = v * (1 + 0.05 * rng.standard_normal(len(v)))           # 5% noise
        for w in df["WELL"].unique():                                    # one missing 30 m chunk per curve per well
            idx = np.where(df["WELL"].to_numpy() == w)[0]
            if len(idx) > 400:
                s = rng.integers(idx[0], idx[-1] - 200)
                df.loc[s:s + 200, c] = np.nan
    return df


def run_level(level, tr, op, hd, A, log=print):
    t0 = time.time()
    step = 1 if level == 1 else 2
    if level == 2:
        tr, op, hd = strip_curves(tr), strip_curves(op), strip_curves(hd)
    if level == 3:
        keep = np.random.default_rng(0).choice(tr.WELL.unique(), 25, replace=False)
        tr = tr[tr.WELL.isin(keep)]
        step = 1
    if level == 4:
        south = lambda d: d[d.WELL.map(quadrant).isin([15, 16, 17, 25, 26])]
        north = lambda d: d[~d.WELL.map(quadrant).isin([15, 16, 17, 25, 26])]
        tr, op, hd = south(tr), south(op), north(hd)
    if level == 5:
        hd = mess_up(hd.reset_index(drop=True))
    tr, op, hd = (d.reset_index(drop=True) for d in (tr, op, hd))
    cats = {c: {v: i for i, v in enumerate(sorted(tr[c].dropna().unique()))} for c in ("GROUP", "FORMATION")}
    fills = v2.fill_models(v2.base_features(tr, cats))
    X = build(pd.concat([tr, op], ignore_index=True), FIXES, cats, fills)
    y = np.concatenate([tr[v2.TARGET], op[v2.TARGET]]).astype(int)
    cat = np.array([c in ("GROUP", "FORMATION") for c in X.columns])
    m = HistGradientBoostingClassifier(learning_rate=0.05, max_leaf_nodes=127, max_iter=600 if level == 1 else 400,
                                       categorical_features=cat, random_state=0)
    m.fit(X.iloc[::step], y[::step])
    yh = hd[v2.TARGET].astype(int).to_numpy()
    pred = v2.min_penalty_decision(m.predict_proba(build(hd, FIXES, cats, fills)), m.classes_, A)
    res = dict(level=level, name=LEVELS[level], score=v2.score(yh, pred, A), accuracy=float(np.mean(pred == yh)),
               train_wells=int(tr.WELL.nunique() + op.WELL.nunique()), hidden_wells=int(hd.WELL.nunique()),
               hidden_samples=int(len(yh)), minutes=round((time.time() - t0) / 60, 1),
               beats_winner=bool(v2.score(yh, pred, A) > WINNER["score"]) if level == 1 else None)
    if level == 1:
        pd.DataFrame(dict(WELL=hd.WELL, DEPTH_MD=hd.DEPTH_MD, true=yh, pred=pred)).to_csv(
            HERE / "hidden_predictions_v4.csv", index=False)
    log(f"Level {level} ({LEVELS[level]}): score {res['score']:.4f}, accuracy {res['accuracy']:.1%}, "
        f"{res['train_wells']} training wells, {res['hidden_wells']} hidden wells, {res['minutes']} min")
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--level", type=int, choices=list(LEVELS))
    a = ap.parse_args()
    A = penalty_matrix()
    tr, op, hd = v2.load()
    results = json.loads(OUT.read_text()) if OUT.exists() else {}
    for lv in ([a.level] if a.level else list(LEVELS)):
        results[str(lv)] = run_level(lv, tr, op, hd, A)
        OUT.write_text(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
