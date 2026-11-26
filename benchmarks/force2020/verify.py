"""Independent fact-check of every FORCE 2020 number V1 reports.

Uses ONLY the competition organizers' own files and scoring code
(github.com/bolgebrygg/Force-2020-Machine-Learning-competition, lithology_competition/):
  * data/hidden_test.csv        - the true answers for the 10 hidden wells
  * data/penalty_matrix.npy     - the official penalty matrix
  * the score() loop copied verbatim from data/test_code.py
None of V1's own scoring code is used.

It re-scores:
  1. every finalist's stored hidden-well predictions (final_scoring/<team>/*.csv) -> compare with the
     published leaderboard;
  2. V1's saved hidden-well predictions (hidden_predictions_v*.csv), matched to the organizers' rows by
     well name + depth.

    git clone https://github.com/bolgebrygg/Force-2020-Machine-Learning-competition
    python benchmarks/force2020/verify.py --comp Force-2020-Machine-Learning-competition/lithology_competition
"""
from __future__ import annotations

import argparse
import glob
import json
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
PUBLISHED = {"Olawale": -0.4690, "GIR": -0.4792, "ICA": -0.4954, "H3G": -0.5045, "ISPL": -0.5084,
             "Jiampiers": -0.5087, "Jose": -0.5091, "Bohdan": -0.5171, "Jeremy": -0.5173,
             "Campbell": -0.5221, "David": -0.5256, "SoftServe": -0.5263, "Dapo": -0.9441}
lithology_numbers = {30000: 0, 65030: 1, 65000: 2, 80000: 3, 74000: 4, 70000: 5, 70032: 6,
                     88000: 7, 86000: 8, 99000: 9, 90000: 10, 93000: 11}   # from test_code.py


def make_score(A):
    def score(y_true, y_pred):                     # verbatim logic from the organizers' test_code.py
        S = 0.0
        y_true = y_true.astype(int)
        y_pred = y_pred.astype(int)
        for i in range(0, y_true.shape[0]):
            S -= A[y_true[i], y_pred[i]]
        return S / y_true.shape[0]
    return score


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--comp", default="/home/user/bolgebrygg/force-2020-machine-learning-competition/lithology_competition")
    a = ap.parse_args()
    comp = Path(a.comp)
    A = np.load(comp / "data/penalty_matrix.npy")
    score = make_score(A)
    truth = pd.read_csv(comp / "data/hidden_test.csv", sep=";")[["WELL", "DEPTH_MD", "FORCE_2020_LITHOFACIES_LITHOLOGY"]]
    truth["y"] = truth["FORCE_2020_LITHOFACIES_LITHOLOGY"].map(lithology_numbers)
    report = {"finalists": {}, "v1": {}}

    print("1) Finalists, re-scored from their stored predictions:")
    for d in sorted((comp / "final_scoring").iterdir()):
        files = sorted(d.glob("*.csv"))
        if not files:
            continue
        p = pd.concat([pd.read_csv(f) for f in files])
        s = score(p["FORCE_2020_LITHOFACIES_LITHOLOGY"].to_numpy(), p["prediction"].to_numpy())
        pub = next((v for k, v in PUBLISHED.items() if d.name.lower().startswith(k.lower()[:5])), None)
        acc = float(np.mean(p["FORCE_2020_LITHOFACIES_LITHOLOGY"].to_numpy() == p["prediction"].to_numpy()))
        report["finalists"][d.name] = dict(rescored=round(s, 4), published=pub, accuracy=round(acc, 4), rows=len(p))
        print(f"   {d.name:22s} re-scored {s:.4f}   published {pub if pub is not None else '   ?  '}   accuracy {acc:.1%}")

    print("2) V1, re-scored on the organizers' rows (matched by well + depth):")
    for f in sorted(HERE.glob("hidden_predictions_v*.csv")):
        v = pd.read_csv(f)
        v["DEPTH_MD"] = v["DEPTH_MD"].round(3)
        t = truth.assign(DEPTH_MD=truth["DEPTH_MD"].round(3))
        m = t.merge(v[["WELL", "DEPTH_MD", "pred"]], on=["WELL", "DEPTH_MD"], how="left")
        covered = m["pred"].notna().mean()
        m = m[m["pred"].notna()]
        yp = m["pred"].astype(int).map(lithology_numbers).to_numpy()
        s = score(m["y"].to_numpy(), yp)
        acc = float(np.mean(m["y"].to_numpy() == yp))
        report["v1"][f.stem] = dict(score=round(s, 4), accuracy=round(acc, 4), rows_matched=int(len(m)),
                                     rows_total=int(len(t)), coverage=round(float(covered), 4))
        print(f"   {f.stem:22s} score {s:.4f}   accuracy {acc:.1%}   rows matched {len(m):,}/{len(t):,}")
    (HERE / "verification.json").write_text(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
