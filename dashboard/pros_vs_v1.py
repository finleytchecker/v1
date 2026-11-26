"""Pictures comparing the professionals with V1 (used by dashboard/site_build.py)."""
from __future__ import annotations

import glob
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

from engine.config import PROJECT_ROOT

BENCH = PROJECT_ROOT / "benchmarks/force2020"
COMP = Path("/home/user/bolgebrygg/force-2020-machine-learning-competition/lithology_competition")
LEADERBOARD = [("Olawale Ibrahim", -0.4690), ("GIR", -0.4792), ("Lab.ICA", -0.4954), ("H3G", -0.5045),
               ("ISPL", -0.5084), ("Jiampiers C.", -0.5087), ("José Bermúdez", -0.5091),
               ("Bohdan Pavlyshenko", -0.5171), ("Jeremy Zhao", -0.5173), ("Campbell Hutcheson", -0.5221),
               ("David P.", -0.5256), ("SoftServe", -0.5263), ("Dapo Awolayo", -0.9441)]
CODES = [30000, 65030, 65000, 80000, 74000, 70000, 70032, 88000, 86000, 99000, 90000, 93000]
NAMES = ["sandstone", "sandstone/shale", "shale", "marl", "dolomite", "limestone", "chalk", "halite",
         "anhydrite", "tuff", "coal", "basement"]
COLORS = ["#ffd54f", "#c5a55a", "#4e8a3e", "#80cbc4", "#ba68c8", "#64b5f6", "#e3f2fd", "#ffffff",
          "#f48fb1", "#ff8a65", "#222222", "#d32f2f"]


def v1_results():
    out = []
    for f, label in (("result.json", "V1 (version 1)"), ("result_v3.json", "V1 (version 3)")):
        p = BENCH / f
        if p.exists():
            r = json.loads(p.read_text())
            out.append((label, r["score"], r["accuracy"]))
    return out


def pic_workflows(save):
    pros = [("Get the well logs", "download & load every curve"),
            ("Clean them by hand", "fix gaps, bad sections, units"),
            ("Read each well", "expert picks rock type,\ndepth by depth"),
            ("Check against\nneighbour wells", "make the layers line up"),
            ("Peer review", "a second expert signs off")]
    v1 = [("Download", "script pulls public data"),
          ("Clean & fill", "fills missing curves\nautomatically"),
          ("Learn from 98 wells", "1.17 million labelled depths"),
          ("Label every well", "all depths in seconds"),
          ("Grade itself", "on wells it never saw,\nwith the official score")]
    fig, ax = plt.subplots(figsize=(13, 9.5))
    ax.set_xlim(0, 13); ax.set_ylim(-1.5, 11); ax.axis("off")
    for col, (title, steps, colr, x) in enumerate((("THE PROS", pros, "#e57373", 0.4),
                                                    ("V1 SOFTWARE", v1, "#4fc3f7", 6.9))):
        ax.text(x + 2.85, 10.4, title, ha="center", fontsize=24, fontweight="bold", color=colr)
        for i, (head, sub) in enumerate(steps):
            y = 8.6 - i * 2.0
            ax.add_patch(FancyBboxPatch((x, y - 0.7), 5.7, 1.45, boxstyle="round,pad=0.05", fc="#111", ec=colr, lw=2.5))
            ax.text(x + 0.25, y + 0.25, head, fontsize=16, fontweight="bold", va="center")
            ax.text(x + 0.25, y - 0.35, sub, fontsize=12, color="#ccc", va="center")
            if i < len(steps) - 1:
                ax.add_patch(FancyArrowPatch((x + 2.85, y - 0.78), (x + 2.85, y - 1.22), arrowstyle="-|>",
                                             mutation_scale=22, color=colr, lw=2))
    ax.text(3.25, -1.1, "hours to days per well (rough estimate)", ha="center", fontsize=14, color="#e57373")
    ax.text(9.75, -1.1, "seconds per well once trained", ha="center", fontsize=14, color="#4fc3f7")
    return save(fig, "pros_workflow.png")


def pic_leaderboard(save):
    rows = [(n, s, None) for n, s in LEADERBOARD] + v1_results()
    rows.sort(key=lambda r: -r[1])
    fig, ax = plt.subplots(figsize=(12, 0.5 * len(rows) + 1.5))
    names = [r[0] for r in rows]
    vals = [-r[1] for r in rows]                       # show penalty as a positive "mistake cost"
    cols = ["#4fc3f7" if r[0].startswith("V1") else ("#ffd54f" if i == 0 else "#777") for i, r in enumerate(rows)]
    ax.barh(names, vals, color=cols)
    for i, r in enumerate(rows):
        lab = f"{r[1]:.4f}" + (f"  ({r[2]:.1%} right)" if r[2] else "")
        ax.text(vals[i] + 0.01, i, lab, va="center", fontsize=12, color="#fff")
    ax.invert_yaxis(); ax.set_xlim(0, max(vals) * 1.35)
    ax.set_xlabel("official mistake cost on the 10 hidden wells  (shorter bar = better)")
    ax.set_title("FORCE 2020 final leaderboard, with V1 added (same wells, same scoring)")
    return save(fig, "pros_leaderboard.png")


def pic_well(save):
    """One hidden well: real answer vs the winning team vs V1."""
    hidden = COMP / "data/hidden_test.csv"
    win_dir = COMP / "final_scoring/Olawale"
    v1p = max(BENCH.glob("hidden_predictions_v*.csv"), default=BENCH / "none.csv")
    if not hidden.exists() or not win_dir.exists():
        return None
    well = "16/2-7" if (win_dir / "16_2-7.csv").exists() else sorted(p.stem for p in win_dir.glob("*.csv"))[0].replace("_", "/")
    w = pd.read_csv(win_dir / f"{well.replace('/', '_')}.csv")
    depth = w["DEPTH_MD"].to_numpy()
    cols = [("real answer", w["FORCE_2020_LITHOFACIES_LITHOLOGY"].astype(int).to_numpy(), True),
            ("winning team", w["prediction"].astype(int).to_numpy(), True)]
    if v1p.exists():
        v = pd.read_csv(v1p)
        v = v[v.WELL == well].assign(DEPTH_MD=lambda d: d.DEPTH_MD.round(3)).set_index("DEPTH_MD").reindex(depth.round(3))
        cols.append(("V1", v["pred"].map({c: i for i, c in enumerate(CODES)}).to_numpy(), True))
    fig, axes = plt.subplots(1, len(cols), figsize=(3.2 * len(cols) + 2, 10), sharey=True)
    for ax, (title, idx, _) in zip(axes, cols):
        img = np.array([COLORS[int(i)] if not np.isnan(i) else "#000" for i in np.asarray(idx, float)])
        rgb = np.array([[int(c[k:k + 2], 16) / 255 for k in (1, 3, 5)] for c in img])[:, None, :]
        ax.imshow(rgb, aspect="auto", extent=(0, 1, depth[-1], depth[0]))
        ax.set_xticks([]); ax.set_title(title, fontsize=17, color="#4fc3f7" if title == "V1" else "#fff")
        if title != "real answer":
            right = np.mean(np.asarray(idx, float) == cols[0][1])
            ax.set_xlabel(f"{right:.0%} match", fontsize=15)
    axes[0].set_ylabel("depth (m)")
    present = sorted(set(cols[0][1]))
    handles = [plt.Rectangle((0, 0), 1, 1, color=COLORS[i]) for i in present]
    fig.legend(handles, [NAMES[i] for i in present], loc="center right", fontsize=12)
    fig.suptitle(f"Hidden well {well}: nobody trained on it", fontsize=18)
    fig.tight_layout(rect=(0, 0, 0.8, 0.96))
    return save(fig, "pros_well.png")
