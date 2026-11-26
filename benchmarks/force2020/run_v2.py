"""FORCE 2020 head-to-head, version 2: the five fixes, under the same competition rules.

Fixes vs version 1:
  1. Rock-layer names (GROUP, FORMATION) as features, exactly as the competition files provide them.
  2. Missing curves filled in: models trained on the training wells predict RHOB, NPHI, DTC, PEF from the
     curves that are present (plus a 'was missing' flag).
  3. Context: what the logs look like above and below each depth (rolling averages, spreads, gradients,
     values 1-20 m away) and each curve compared with its own well's typical value.
  4. Official penalty table used when deciding: pick the rock type with the lowest EXPECTED penalty
     given the model's probabilities, not just the single most likely one.
  5. A blend of several models (averaged probabilities).
Tuning uses only the open test wells. The hidden wells are scored once, at the end.

    python -m benchmarks.force2020.run_v2
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import HistGradientBoostingClassifier, HistGradientBoostingRegressor

from benchmarks.force2020.run import CLASSES, penalty_matrix
from engine.config import PROJECT_ROOT

HERE = Path(__file__).resolve().parent
D = PROJECT_ROOT / "data/real/force-2020/competition"
TARGET = "FORCE_2020_LITHOFACIES_LITHOLOGY"
NUM = ["CALI", "RSHA", "RMED", "RDEP", "RHOB", "GR", "NPHI", "PEF", "DTC", "SP", "BS", "ROP", "DRHO", "DCAL", "MUDWEIGHT", "RXO"]
LOGC = ["RSHA", "RMED", "RDEP", "RXO"]
CONTEXT = ["GR", "RHOB", "NPHI", "DTC", "RDEP", "RMED", "PEF", "SP", "CALI"]
FILL = ["RHOB", "NPHI", "DTC", "PEF"]
CIDX = {c: i for i, c in enumerate(CLASSES)}


def load():
    tr = pd.read_csv(D / "train.csv", sep=";")
    op = pd.read_csv(D / "leaderboard_test_features.csv", sep=";")
    op = op.merge(pd.read_csv(D / "leaderboard_test_target.csv", sep=";"), on=["WELL", "DEPTH_MD"], how="left")
    hd = pd.read_csv(D / "hidden_test.csv", sep=";")
    return tr, op, hd


def base_features(df, cats):
    out = pd.DataFrame(index=df.index)
    for c in NUM:
        v = df[c].astype(float) if c in df else np.nan
        out[c] = np.log10(np.clip(v, 0.01, None)) if c in LOGC else v
    for c in ("DEPTH_MD", "X_LOC", "Y_LOC", "Z_LOC"):
        out[c] = df[c]
    for c in ("GROUP", "FORMATION"):                      # fix 1: rock-layer names -> codes shared by all splits
        out[c] = df[c].map(cats[c]).fillna(-1).astype(float)
    return out


def fill_models(Xtr):
    """Fix 2: learn to predict each often-missing curve from the others (training wells only)."""
    models = {}
    for c in FILL:
        ok = Xtr[c].notna()
        cols = [x for x in Xtr.columns if x != c]
        m = HistGradientBoostingRegressor(max_iter=200, random_state=0)
        m.fit(Xtr.loc[ok, cols].iloc[::4], Xtr.loc[ok, c].iloc[::4])
        models[c] = (m, cols)
    return models


def apply_fill(X, models):
    X = X.copy()
    for c, (m, cols) in models.items():
        miss = X[c].isna()
        X[c + "_missing"] = miss.astype(float)
        if miss.any():
            X.loc[miss, c] = m.predict(X.loc[miss, cols])
    return X


def context(X, wells):
    """Fix 3: what's above and below, and each curve against its own well's usual level."""
    parts = [X]
    g = X[CONTEXT].groupby(wells.values)
    for w in (5, 15, 51):
        parts.append(g.transform(lambda s: s.rolling(w, center=True, min_periods=1).mean()).add_suffix(f"_m{w}"))
        parts.append(g.transform(lambda s: s.rolling(w, center=True, min_periods=1).std()).add_suffix(f"_s{w}"))
    for k in (5, 20, 60):                                  # ~0.75 m, 3 m, 9 m away
        parts.append(g.shift(k).add_suffix(f"_up{k}"))
        parts.append(g.shift(-k).add_suffix(f"_dn{k}"))
    parts.append(g.transform(lambda s: s.diff()).add_suffix("_grad"))
    med = g.transform("median")
    iqr = g.transform(lambda s: s.quantile(0.75) - s.quantile(0.25)).replace(0, np.nan)
    parts.append(((X[CONTEXT] - med) / iqr).add_suffix("_wellnorm"))
    return pd.concat(parts, axis=1)


def features(df, cats, fills):
    X = apply_fill(base_features(df, cats), fills)
    return context(X, df["WELL"]).astype(np.float32)


def min_penalty_decision(P, classes, A):
    """Fix 4: choose the class with the smallest expected official penalty."""
    sub = A[np.ix_([CIDX[c] for c in classes], [CIDX[c] for c in classes])]
    return np.asarray(classes)[np.argmin(P @ sub, axis=1)]


def score(y, p, A):
    return -float(np.mean(A[[CIDX[t] for t in y], [CIDX[q] for q in p]]))


MODELS = [  # fix 5: a small blend
    dict(learning_rate=0.05, max_leaf_nodes=127, max_iter=600, l2_regularization=1.0, random_state=0),
    dict(learning_rate=0.05, max_leaf_nodes=63, max_iter=800, max_features=0.5, random_state=1),
    dict(learning_rate=0.08, max_leaf_nodes=255, max_iter=400, min_samples_leaf=100, random_state=2),
]


def fit_blend(X, y, cat_mask, step=1, log=print):
    ms = []
    for i, kw in enumerate(MODELS):
        t = time.time()
        m = HistGradientBoostingClassifier(categorical_features=cat_mask, early_stopping=False, **kw)
        m.fit(X.iloc[::step], y[::step])
        ms.append(m)
        log(f"    model {i + 1}/{len(MODELS)} trained in {time.time() - t:.0f}s")
    return ms


def blend_proba(ms, X):
    return np.mean([m.predict_proba(X) for m in ms], axis=0), ms[0].classes_


def main(log=print):
    t0 = time.time()
    A = penalty_matrix()
    tr, op, hd = load()
    cats = {c: {v: i for i, v in enumerate(sorted(tr[c].dropna().unique()))} for c in ("GROUP", "FORMATION")}
    fills = fill_models(base_features(tr, cats))
    Xtr, Xop, Xhd = (features(d, cats, fills) for d in (tr, op, hd))
    ytr, yop, yhd = (d[TARGET].astype(int).to_numpy() for d in (tr, op, hd))
    cat_mask = np.array([c in ("GROUP", "FORMATION") for c in Xtr.columns])
    # unknown layer names (-1) are treated as missing so the categorical encoder accepts them
    for X in (Xtr, Xop, Xhd):
        X.loc[:, ["GROUP", "FORMATION"]] = X[["GROUP", "FORMATION"]].replace(-1, np.nan)
    log(f"features: {Xtr.shape[1]}; train {len(ytr):,}, open test {len(yop):,}, hidden {len(yhd):,} samples")

    # tune on the open test wells only
    log("  training blend on the training wells (tuning on open test)")
    ms = fit_blend(Xtr, ytr, cat_mask, step=2, log=log)
    P, cls = blend_proba(ms, Xop)
    plain = cls[np.argmax(P, axis=1)]
    smart = min_penalty_decision(P, cls, A)
    s_plain, s_smart = score(yop, plain, A), score(yop, smart, A)
    log(f"  open test: blend {s_plain:.4f} (acc {np.mean(plain == yop):.1%}), "
        f"with penalty-aware decisions {s_smart:.4f} (acc {np.mean(smart == yop):.1%})")
    use_penalty = s_smart > s_plain

    # final: retrain on train + open test, score the hidden wells ONCE
    log("  final training on train + open test wells")
    ms = fit_blend(pd.concat([Xtr, Xop]), np.concatenate([ytr, yop]), cat_mask, step=2, log=log)
    P, cls = blend_proba(ms, Xhd)
    pred = min_penalty_decision(P, cls, A) if use_penalty else cls[np.argmax(P, axis=1)]
    res = dict(version=2, score=score(yhd, pred, A), accuracy=float(np.mean(pred == yhd)), n_samples=int(len(yhd)),
               open_test=dict(blend=s_plain, penalty_aware=s_smart), penalty_aware_used=bool(use_penalty),
               n_features=int(Xtr.shape[1]), minutes=round((time.time() - t0) / 60, 1))
    (HERE / "result_v2.json").write_text(json.dumps(res, indent=2))
    pd.DataFrame(dict(WELL=hd.WELL, DEPTH_MD=hd.DEPTH_MD, true=yhd, pred=pred)).to_csv(HERE / "hidden_predictions_v2.csv", index=False)
    log(f"HIDDEN WELLS (scored once): official score {res['score']:.4f}, accuracy {res['accuracy']:.1%} "
        f"({res['minutes']} min total)")
    return res


if __name__ == "__main__":
    main()
