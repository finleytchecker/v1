"""Head-to-head with the pros: the FORCE 2020 lithology competition (~330 teams).

Same rules as the competition:
  * train only on the 98 training wells (+ may tune on the 10 open test wells, which teams also had)
  * predict every depth sample (15 cm) of the 10 hidden wells
  * score once with the official penalty matrix:  score = -mean(A[true, predicted])   (0 is perfect)
The hidden wells are never used for training or for choosing settings.

    python -m benchmarks.force2020.run
"""
from __future__ import annotations

import json
import time
from pathlib import Path

import lasio
import numpy as np
import openpyxl
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import accuracy_score

from engine.config import PROJECT_ROOT

HERE = Path(__file__).resolve().parent
LAS_DIR = PROJECT_ROOT / "data/real/force-2020/force2020-well-logs/las/Force_2020_all_wells_train_test_blind_hidden_final"
CLASSES = [30000, 65030, 65000, 80000, 74000, 70000, 70032, 88000, 86000, 99000, 90000, 93000]  # matrix order
CURVES = ["GR", "RHOB", "NPHI", "DTC", "RDEP", "RMED", "RSHA", "PEF", "CALI", "SP", "DRHO", "BS", "ROP", "DTS", "RXO"]
LOGC = {"RDEP", "RMED", "RSHA", "RXO"}


def penalty_matrix():
    ws = openpyxl.load_workbook(HERE / "scoring_matrix.xlsx", data_only=True).active
    rows = [r for r in ws.iter_rows(values_only=True)]
    start = next(i for i, r in enumerate(rows) if r[2] == "Sandstone")
    return np.array([[float(v) for v in r[3:15]] for r in rows[start:start + 12]])


def official_score(y_true, y_pred, A):
    idx = {c: i for i, c in enumerate(CLASSES)}
    return -float(np.mean([A[idx[t], idx[p]] for t, p in zip(y_true, y_pred)]))


def well_file(name):
    return LAS_DIR / (name.replace("/", "_") + ".las")


def load_well(name):
    df = lasio.read(well_file(name)).df()
    df = df[df["FORCE_2020_LITHOFACIES_LITHOLOGY"].notna()]
    cols = []
    for c in CURVES:
        v = df[c].to_numpy(float) if c in df else np.full(len(df), np.nan)
        cols.append(np.log10(np.clip(v, 0.01, None)) if c in LOGC else v)
    base = np.column_stack(cols)
    depth = df.index.to_numpy(float)
    # context: what the logs look like just above and below (geologists read logs this way too)
    feats = [base, depth[:, None]]
    for c in (0, 1, 2, 3, 4):                    # GR, RHOB, NPHI, DTC, RDEP
        x = base[:, c]
        feats += [np.gradient(np.nan_to_num(x))[:, None]]
        for w in (5, 21):
            k = np.ones(w) / w
            pad = np.pad(np.nan_to_num(x, nan=np.nanmedian(x) if np.isfinite(x).any() else 0), w // 2, mode="edge")
            feats.append(np.convolve(pad, k, mode="valid")[:, None])
    for xy in ("X_LOC", "Y_LOC"):
        feats.append((df[xy].to_numpy(float) if xy in df else np.full(len(df), np.nan))[:, None])
    y = df["FORCE_2020_LITHOFACIES_LITHOLOGY"].astype(int).to_numpy()
    return np.hstack(feats), y


def load_split(names, step=1):
    X, y = [], []
    for n in names:
        a, b = load_well(n)
        X.append(a[::step]); y.append(b[::step])
    return np.vstack(X), np.concatenate(y)


def main(log=print):
    splits = json.loads((HERE / "splits.json").read_text())
    A = penalty_matrix()
    t0 = time.time()
    Xtr, ytr = load_split(splits["train"], step=2)
    Xop, yop = load_split(splits["open_test"])
    log(f"train: {len(splits['train'])} wells, {len(ytr):,} samples; open test: {len(yop):,} samples")

    # tune on the open test wells only (allowed in the competition); hidden wells untouched
    best = None
    for lr, leaves in ((0.1, 31), (0.08, 63), (0.05, 127)):
        m = HistGradientBoostingClassifier(learning_rate=lr, max_leaf_nodes=leaves, max_iter=400, random_state=0)
        m.fit(Xtr, ytr)
        s = official_score(yop, m.predict(Xop), A)
        log(f"  setting lr={lr} leaves={leaves}: open-test score {s:.4f}, accuracy {accuracy_score(yop, m.predict(Xop)):.1%}")
        if best is None or s > best[0]:
            best = (s, lr, leaves)

    # final: retrain the chosen setting on train + open test, then score the hidden wells ONCE
    _, lr, leaves = best
    final = HistGradientBoostingClassifier(learning_rate=lr, max_leaf_nodes=leaves, max_iter=400, random_state=0)
    final.fit(np.vstack([Xtr, Xop]), np.concatenate([ytr, yop]))
    Xh, yh = load_split(splits["hidden_test"])
    ph = final.predict(Xh)
    result = dict(score=official_score(yh, ph, A), accuracy=float(accuracy_score(yh, ph)), n_samples=int(len(yh)),
                  setting=dict(learning_rate=lr, max_leaf_nodes=leaves), minutes=round((time.time() - t0) / 60, 1))
    (HERE / "result.json").write_text(json.dumps(result, indent=2))
    log(f"HIDDEN WELLS (scored once): official score {result['score']:.4f}, accuracy {result['accuracy']:.1%}")
    return result


if __name__ == "__main__":
    main()
