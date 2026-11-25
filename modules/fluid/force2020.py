"""FORCE 2020 well logs (118 real North Sea wells, CC-BY 4.0) -> rock type at each depth.

Known answers: interpreters labelled the lithology (sandstone, shale, limestone...) at every depth.
This is REAL-data practice for the Fluid module: it teaches the model to read real logs.
It is rock type, not water/oil/gas. Fluid labels come later (Volve interpretation logs).

Groups = wells, so the hold-out is whole wells the model never saw.
"""
from __future__ import annotations

import glob
from pathlib import Path

import lasio
import numpy as np

from engine.config import PROJECT_ROOT

LAS_GLOB = str(PROJECT_ROOT / "data/real/force-2020/force2020-well-logs/las/*/*.las")
CACHE = PROJECT_ROOT / "data/real/force-2020/force2020_table.npz"
CURVES = ["GR", "RHOB", "NPHI", "DTC", "RDEP", "RMED", "PEF", "CALI", "SP", "DRHO"]
LOG_CURVES = {"RDEP", "RMED"}
LITHO = {30000: "sandstone", 65030: "sandstone/shale", 65000: "shale", 80000: "marl", 74000: "dolomite",
         70000: "limestone", 70032: "chalk", 88000: "anhydrite", 86000: "halite", 99000: "tuff",
         90000: "coal", 93000: "basement"}
STEP = 8          # keep every 8th depth sample (~1.2 m) so it trains in minutes


def build_table():
    rows, labels, wells, depths = [], [], [], []
    for f in sorted(glob.glob(LAS_GLOB)):
        las = lasio.read(f)
        df = las.df()
        if "FORCE_2020_LITHOFACIES_LITHOLOGY" not in df:
            continue
        df = df.iloc[::STEP]
        lab = df["FORCE_2020_LITHOFACIES_LITHOLOGY"]
        df = df[lab.notna()]
        if df.empty:
            continue
        feats = []
        for c in CURVES:
            v = df[c].to_numpy(float) if c in df else np.full(len(df), np.nan)
            feats.append(np.log10(np.clip(v, 0.01, None)) if c in LOG_CURVES else v)
        rows.append(np.column_stack(feats + [df.index.to_numpy(float)]))
        labels += [LITHO.get(int(x), "other") for x in df["FORCE_2020_LITHOFACIES_LITHOLOGY"]]
        wells += [Path(f).stem] * len(df)
        depths += list(df.index.to_numpy(float))
    X = np.vstack(rows)
    np.savez_compressed(CACHE, X=X, y=np.array(labels), wells=np.array(wells), depth=np.array(depths))


class Force2020:
    name = "force2020-lithology"
    feature_names = CURVES + ["DEPTH"]

    def load(self):
        if not CACHE.exists():
            build_table()
        d = np.load(CACHE, allow_pickle=False)
        X, y, wells = d["X"], d["y"], d["wells"]
        # missing curves: fill with the median and add a 'was missing' flag (real logs have gaps)
        miss = np.isnan(X)
        med = np.nanmedian(X, axis=0)
        Xf = np.where(miss, med, X)
        Xf = np.column_stack([Xf, miss[:, :len(CURVES)].astype(float)])
        # very rare rock types (< 0.3% of samples) are merged into 'other'
        vals, counts = np.unique(y, return_counts=True)
        rare = set(vals[counts < 0.003 * len(y)])
        y = np.array(["other" if v in rare else v for v in y])
        ids = np.array([f"{w}@{dp:.0f}m" for w, dp in zip(wells, d["depth"])])
        return dict(X=Xf, y=y, groups=wells, ids=ids, feature_names=self.feature_names,
                    description="FORCE 2020: rock type from real well logs")


if __name__ == "__main__":
    from engine import real_loop
    real_loop.run("fluid", Force2020.name, Force2020())
