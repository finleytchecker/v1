"""FORCE 2020 head-to-head, version 3: test each fix on its own, keep only the ones that help.

Reads the competition's own CSV files (so every official hidden row gets a prediction).
Step 1 (ablation, fast): train on every 4th training sample, score on the open test wells:
    baseline (version-1 style features) and baseline + each single fix.
Step 2: combine the fixes that improved the open-test score, train on train + open test,
    score the 10 hidden wells ONCE.

    python -m benchmarks.force2020.run_v3
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier

from benchmarks.force2020 import run_v2 as v2
from benchmarks.force2020.run import penalty_matrix

HERE = Path(__file__).resolve().parent
BASE_CURVES = ["GR", "RHOB", "NPHI", "DTC", "RDEP", "RMED", "RSHA", "PEF", "CALI", "SP", "DRHO", "BS", "ROP", "DTS", "RXO"]
FIXES = ["layer_names", "fill_curves", "wide_context", "penalty_decision"]


def baseline(df):
    """Version-1 style: raw curves, depth, location, a short gradient and 2 rolling averages for 5 curves."""
    X = pd.DataFrame(index=df.index)
    for c in BASE_CURVES:
        v = df[c].astype(float)
        X[c] = np.log10(np.clip(v, 0.01, None)) if c in v2.LOGC + ["RXO"] else v
    for c in ("DEPTH_MD", "X_LOC", "Y_LOC"):
        X[c] = df[c]
    g = X[["GR", "RHOB", "NPHI", "DTC", "RDEP"]].groupby(df["WELL"].values)
    X = pd.concat([X, g.transform(lambda s: s.diff()).add_suffix("_grad"),
                   g.transform(lambda s: s.rolling(5, center=True, min_periods=1).mean()).add_suffix("_m5"),
                   g.transform(lambda s: s.rolling(21, center=True, min_periods=1).mean()).add_suffix("_m21")], axis=1)
    return X


def build(df, fixes, cats, fills):
    X = baseline(df)
    if "layer_names" in fixes:
        for c in ("GROUP", "FORMATION"):
            X[c] = df[c].map(cats[c]).astype(float)        # unknown names -> NaN
    if "fill_curves" in fixes:
        b = v2.apply_fill(v2.base_features(df, cats), fills)
        for c in v2.FILL:
            X[c + "_filled"] = b[c]; X[c + "_missing"] = b[c + "_missing"]
    if "wide_context" in fixes:
        ctx = v2.context(v2.base_features(df, cats), df["WELL"])
        new = [c for c in ctx.columns if c not in X.columns and any(s in c for s in ("_s", "_up", "_dn", "_wellnorm", "_m51", "_m15"))]
        X = pd.concat([X, ctx[new]], axis=1)
    return X.astype(np.float32)


def fit(X, y, step):
    cat = np.array([c in ("GROUP", "FORMATION") for c in X.columns])
    m = HistGradientBoostingClassifier(learning_rate=0.05, max_leaf_nodes=127, max_iter=400,
                                       categorical_features=cat if cat.any() else None, random_state=0)
    return m.fit(X.iloc[::step], y[::step])


def decide(m, X, fixes, A):
    P = m.predict_proba(X)
    if "penalty_decision" in fixes:
        return v2.min_penalty_decision(P, m.classes_, A)
    return m.classes_[np.argmax(P, axis=1)]


def main(log=print):
    t0 = time.time()
    A = penalty_matrix()
    tr, op, hd = v2.load()
    cats = {c: {v: i for i, v in enumerate(sorted(tr[c].dropna().unique()))} for c in ("GROUP", "FORMATION")}
    fills = v2.fill_models(v2.base_features(tr, cats))
    ytr, yop, yhd = (d[v2.TARGET].astype(int).to_numpy() for d in (tr, op, hd))

    # step 1: one fix at a time, judged on the open test wells only
    results = {}
    for name, fixes in [("baseline", [])] + [(f, [f]) for f in FIXES]:
        t = time.time()
        if name == "penalty_decision" and "baseline_model" in results:
            m = results["baseline_model"]                     # same model, only the decision rule changes
        else:
            m = fit(build(tr, fixes, cats, fills), ytr, step=4)
        p = decide(m, build(op, fixes, cats, fills), fixes, A)
        s = v2.score(yop, p, A)
        results[name] = dict(open_score=s, open_acc=float(np.mean(p == yop)))
        if name == "baseline":
            results["baseline_model"] = m
        log(f"  {name:17s} open-test score {s:.4f}  accuracy {np.mean(p == yop):.1%}  ({time.time() - t:.0f}s)")
    results.pop("baseline_model")
    keep = [f for f in FIXES if results[f]["open_score"] > results["baseline"]["open_score"] + 0.002]
    log(f"  keeping: {keep or 'none (baseline only)'}")

    # step 2: final model with the kept fixes, scored once on the hidden wells
    Xall = build(pd.concat([tr, op], ignore_index=True), keep, cats, fills)
    m = fit(Xall, np.concatenate([ytr, yop]), step=2)
    pred = decide(m, build(hd, keep, cats, fills), keep, A)
    res = dict(version=3, kept_fixes=keep, ablation=results, score=v2.score(yhd, pred, A),
               accuracy=float(np.mean(pred == yhd)), n_samples=int(len(yhd)), minutes=round((time.time() - t0) / 60, 1))
    (HERE / "result_v3.json").write_text(json.dumps(res, indent=2))
    pd.DataFrame(dict(WELL=hd.WELL, DEPTH_MD=hd.DEPTH_MD, true=yhd, pred=pred)).to_csv(HERE / "hidden_predictions_v3.csv", index=False)
    log(f"HIDDEN WELLS (scored once): official score {res['score']:.4f}, accuracy {res['accuracy']:.1%} ({res['minutes']} min)")


if __name__ == "__main__":
    main()
