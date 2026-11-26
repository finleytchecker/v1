"""Builds the picture dashboard as a static website in dashboard/site/ (index.html + images).

    python -m dashboard.site_build

Everything is drawn as pictures: progress, learning curves, the actual signals it got wrong,
real well logs, and the learning cycle. The site can be deployed as-is (e.g. to Vercel).
"""
from __future__ import annotations

import glob
import json
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import yaml  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch  # noqa: E402

from engine.config import PROJECT_ROOT, database_path  # noqa: E402
from engine.course.generators import REGISTRY  # noqa: E402
from engine.db import Logbook  # noqa: E402

SITE = PROJECT_ROOT / "dashboard" / "site"
IMG = SITE / "img"
GREEN, RED, YELLOW, BLUE, GREY = "#00e676", "#ff5252", "#ffd400", "#4fc3f7", "#777777"
LITHO_COLORS = {"sandstone": "#ffd54f", "sandstone/shale": "#c5a55a", "shale": "#4e8a3e", "marl": "#80cbc4",
                "limestone": "#64b5f6", "chalk": "#e3f2fd", "dolomite": "#ba68c8", "anhydrite": "#f48fb1",
                "halite": "#ffffff", "tuff": "#ff8a65", "coal": "#222222", "other": "#9e9e9e"}

plt.rcParams.update({"figure.facecolor": "#000", "axes.facecolor": "#0b0b0b", "savefig.facecolor": "#000",
                     "text.color": "#fff", "axes.labelcolor": "#fff", "xtick.color": "#ddd", "ytick.color": "#ddd",
                     "axes.edgecolor": "#666", "font.size": 15, "axes.titlesize": 17, "axes.titleweight": "bold"})


def save(fig, name):
    IMG.mkdir(parents=True, exist_ok=True)
    fig.savefig(IMG / name, dpi=110, bbox_inches="tight")
    plt.close(fig)
    return f"img/{name}"


SHORT = {"s01-tone-frequency": "Find a tone's pitch", "s02-signal-in-noise": "Signal or noise?",
         "s03-signal-shapes": "Tone/chirp/noise/bang", "s04-filter-the-rumble": "Tone under rumble",
         "l01-three-events": "Quiet/traffic/leak", "l02-five-events": "+ digging & wind",
         "l03-leak-in-clutter": "Weak leak in clutter", "l04-traffic-speed": "Car speed",
         "l05-leak-location": "Where's the leak?", "f01-gassmann": "Rock speed from fluid",
         "f02-fluid-from-logs": "Brine/oil/gas/dry", "f03-attenuation": "Soaks up highs?",
         "f04-avo": "Gas vs brine (AVO)", "f05-s-wave-shadow": "Liquid/gas pocket"}


# ------------------------------------------------------------------ pictures

def pic_progress(book, cat, dls, real):
    lessons = book.course_status()
    srcs = sum(len(yaml.safe_load(open(p)) or []) for p in (PROJECT_ROOT / "course/sources").glob("*.yaml"))
    done = sum(l["status"] == "passed" for l in lessons)
    ids = {e["id"] for e in cat}
    ok_dl = len({d["entry_id"] for d in dls if d["status"] == "done" and d["entry_id"] in ids})
    areas = [("Research\nlibrary", 1.0, f"{srcs} sources"),
             ("Warm-up\ncourse", done / max(1, len(lessons)), f"{done}/{len(lessons)} lessons"),
             ("Real data\ndownloaded", ok_dl / max(1, len(cat)), f"{ok_dl} of {len(cat)} found so far"),
             ("Leak on\nreal data", real["leak"] or 0, f"{real['leak']:.0%} honest" if real["leak"] else "not yet"),
             ("Fluid on\nreal data", real["fluid"] or 0, f"{real['fluid']:.0%} honest" if real["fluid"] else "running" if real.get("fluid_running") else "not yet")]
    fig, axes = plt.subplots(1, 5, figsize=(15, 3.8))
    for ax, (name, frac, lab) in zip(axes, areas):
        frac = min(1.0, max(0.0, frac))
        c = GREEN if frac >= 0.999 else (YELLOW if frac > 0 else GREY)
        ax.pie([frac, 1 - frac + 1e-9], colors=[c, "#262626"], startangle=90, counterclock=False,
               wedgeprops=dict(width=0.28))
        ax.text(0, 0, f"{frac:.0%}", ha="center", va="center", fontsize=26, fontweight="bold")
        ax.set_title(name, fontsize=17)
        ax.text(0, -1.45, lab, ha="center", fontsize=14, color="#ddd")
    return save(fig, "progress.png")


def pic_learning_curves(book):
    lessons = book.course_status()
    att = {}
    for a in reversed(book.attempts(limit=5000)):
        att.setdefault(a["lesson_id"], []).append(a)
    n = len(lessons)
    cols = 2
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(12, 2.3 * rows))
    for ax, l in zip(axes.ravel(), lessons):
        a = att.get(l["lesson_id"], [])
        if a:
            xs = [x["attempt"] for x in a]
            ys = [x["score"] for x in a]
            ax.bar(xs, ys, color=[GREEN if x["outcome"] == "pass" else RED for x in a], width=0.7)
            ax.axhline(a[0]["threshold"], color="#fff", ls="--", lw=2)
            ax.set_xticks(range(1, 9))
        ax.set_ylim(0, 1.05); ax.set_xlim(0.4, 8.6)
        ax.set_yticks([0, .5, 1]); ax.set_yticklabels(["0", "50%", "100%"])
        icon = {"passed": "PASS", "stuck": "STUCK", "in_progress": "...", "not_started": "-"}[l["status"]]
        ax.set_title(f"{SHORT.get(l['lesson_id'], l['title'])}  [{icon}]", fontsize=14, loc="left",
                     color=GREEN if l["status"] == "passed" else (RED if l["status"] == "stuck" else "#fff"))
    for ax in axes.ravel()[n:]:
        ax.axis("off")
    fig.suptitle("Every lesson: red = failed try, green = passed, dashed line = pass mark", fontsize=16, y=1.0)
    fig.tight_layout()
    return save(fig, "learning_curves.png")


def _draw_example(ax, arr):
    a = np.asarray(arr, float)
    if a.ndim == 2 and a.shape[0] > 3:
        from scipy.ndimage import uniform_filter1d
        e = np.sqrt(uniform_filter1d(a ** 2, 24, axis=1))
        ax.imshow(e, aspect="auto", cmap="inferno", vmin=np.percentile(e, 20), vmax=np.percentile(e, 99.5))
        ax.set_xlabel("time →", fontsize=11); ax.set_ylabel("cable position", fontsize=11)
    elif a.ndim == 2:
        for row, c, lab in zip(a, [BLUE, RED, YELLOW], ["P strength", "S strength", "P delay"]):
            ax.plot(row, color=c, lw=2, label=lab)
        ax.legend(fontsize=9, loc="lower left")
        ax.set_xlabel("sensor along surface →", fontsize=11)
    elif a.size <= 12:
        ax.plot(np.arange(a.size), a, "o-", color=BLUE, lw=2)
        ax.set_xlabel("angle →", fontsize=11)
    else:
        ax.plot(a[:500], color=BLUE, lw=1)
        ax.set_xlabel("time →", fontsize=11)
    ax.set_xticks([]); ax.set_yticks([])


def pic_mistakes(book, limit=12):
    """The actual signals it got wrong (latest failed try of each lesson)."""
    seen, picks = set(), []
    for a in book.attempts(limit=5000):
        if a["outcome"] != "fail" or a["lesson_id"] in seen or not a["mistakes"]:
            continue
        seen.add(a["lesson_id"])
        m = a["mistakes"][0]
        p = PROJECT_ROOT / m["file"]
        if p.exists():
            picks.append((a, m, np.load(p)))
    picks = picks[:limit]
    if not picks:
        return None
    cols = 3
    rows = (len(picks) + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(14, 3.4 * rows))
    for ax, (a, m, arr) in zip(np.atleast_1d(axes).ravel(), picks):
        _draw_example(ax, arr)
        t, p = m["true"], m["pred"]
        try:
            t, p = f"{float(t):.1f}", f"{float(p):.1f}"
        except ValueError:
            pass
        ax.set_title(f"{SHORT.get(a['lesson_id'], a['lesson_id'])}\nsaid {p}, really {t}  (try {a['attempt']})",
                     fontsize=13, color=RED)
    for ax in np.atleast_1d(axes).ravel()[len(picks):]:
        ax.axis("off")
    fig.tight_layout()
    return save(fig, "mistakes.png")


def pic_das_examples():
    rng = np.random.default_rng(7)
    X, y, _ = REGISTRY["das_five_events"]["fn"](10, rng)
    ex = {}
    for xi, yi in zip(X, y):
        ex.setdefault(str(yi), xi)
    fig, axes = plt.subplots(1, 5, figsize=(16, 3.6))
    for ax, k in zip(axes, ["quiet", "traffic", "leak", "digging", "wind"]):
        _draw_example(ax, ex[k]); ax.set_title(k.upper(), fontsize=17, color=YELLOW if k == "leak" else "#fff")
    fig.suptitle("What the fiber-optic cable 'sees' (bright = shaking)", fontsize=16)
    fig.tight_layout()
    return save(fig, "das_examples.png")


def pic_fluid_examples():
    rng = np.random.default_rng(3)
    fig, axes = plt.subplots(1, 3, figsize=(16, 3.8))
    X, y, _ = REGISTRY["s_wave_shadow"]["fn"](6, rng)
    for k, c in (("none", "#aaa"), ("liquid", BLUE), ("gas", RED)):
        i = list(y).index(k)
        axes[0].plot(X[i][1], color=c, lw=2.5, label=f"{k} pocket")
    axes[0].set_title("S-waves die above liquid"); axes[0].legend(fontsize=11); axes[0].set_xlabel("sensor along surface")
    X, y, _ = REGISTRY["attenuation_q"]["fn"](4, rng)
    for k, c, lab in (("high_q", "#aaa", "tight rock"), ("low_q", BLUE, "fluid-filled rock")):
        i = list(y).index(k)
        axes[1].plot(X[i][350:650], color=c, lw=2, label=lab)
    axes[1].set_title("Fluids blur the pulse"); axes[1].legend(fontsize=11); axes[1].set_xlabel("time")
    X, y, _ = REGISTRY["fluid_from_logs"]["fn"](800, rng)
    for k, c in (("brine", BLUE), ("oil", "#8d6e63"), ("gas", RED), ("dry", "#aaa")):
        s = X[y == k]
        axes[2].scatter(s[:, 0] * s[:, 2], s[:, 0] / s[:, 1], s=8, color=c, label=k, alpha=.7)
    axes[2].set_xlabel("acoustic impedance"); axes[2].set_ylabel("Vp/Vs")
    axes[2].set_title("Each fluid sits in its own patch"); axes[2].legend(fontsize=11, markerscale=3)
    for ax in axes[:2]:
        ax.set_yticks([])
    fig.tight_layout()
    return save(fig, "fluid_examples.png")


def pic_cycle(book):
    """The learning cycle as a picture, with live counts."""
    atts = book.attempts(limit=5000)
    fails = sum(a["outcome"] == "fail" for a in atts)
    passes = sum(a["outcome"] == "pass" for a in atts)
    steps = [("MAKE\nEXAMPLES", "#1e88e5"), ("HIDE THE\nANSWERS", "#1e88e5"), ("STUDY", "#1e88e5"),
             ("TAKE THE\nQUIZ", "#1e88e5"), ("GRADE\nITSELF", "#fbc02d"),
             (f"FAIL ({fails})\nfind WHY\n& WHERE", "#e53935"), ("FIX IT\n& re-study\nmistakes", "#e53935")]
    fig, ax = plt.subplots(figsize=(10, 10))
    ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.axis("off")
    n = len(steps)
    pos = [(np.cos(np.pi / 2 - 2 * np.pi * i / n), np.sin(np.pi / 2 - 2 * np.pi * i / n)) for i in range(n)]
    for i, ((txt, c), (x, y)) in enumerate(zip(steps, pos)):
        ax.add_patch(FancyBboxPatch((x - .33, y - .2), .66, .4, boxstyle="round,pad=0.03", fc=c, ec="#fff", lw=2))
        ax.text(x, y, txt, ha="center", va="center", fontsize=15, fontweight="bold", color="#000" if c == "#fbc02d" else "#fff")
        x2, y2 = pos[(i + 1) % n]
        ax.add_patch(FancyArrowPatch((x * .78, y * .78), (x2 * .78, y2 * .78), connectionstyle="arc3,rad=-0.25",
                                     arrowstyle="-|>", mutation_scale=28, color="#fff", lw=2.5))
    ax.add_patch(FancyBboxPatch((-.55, -.25), 1.1, .5, boxstyle="round,pad=0.03", fc="#00c853", ec="#fff", lw=2))
    ax.text(0, 0, f"PASS ({passes})\n→ final exam\n→ next lesson", ha="center", va="center", fontsize=16,
            fontweight="bold", color="#000")
    ax.annotate("", xy=(-.45, -.29), xytext=(pos[4][0] + .1, pos[4][1] + .22), arrowprops=dict(arrowstyle="-|>", color="#00e676", lw=3))
    ax.set_title("How V1 teaches itself", fontsize=22)
    return save(fig, "cycle.png")


def pic_pipeline(state):
    """The big picture as a picture: research → warm-up → download → label → lock exam → rounds → honest score."""
    steps = ["RESEARCH\nweb courses\n& papers", "WARM UP\non simulated\nphysics", "DOWNLOAD\nreal public\ndata",
             "LABEL\nfrom known\nanswers", "LOCK AWAY\nfinal-exam\nwells", "PRACTICE\nin rounds", "HONEST\nSCORE"]
    colors = {"done": "#00c853", "now": "#fbc02d", "todo": "#555"}
    fig, ax = plt.subplots(figsize=(16, 3.4))
    ax.set_xlim(0, len(steps)); ax.set_ylim(0, 1); ax.axis("off")
    for i, (txt, st) in enumerate(zip(steps, state)):
        ax.add_patch(FancyBboxPatch((i + .06, .12), .8, .76, boxstyle="round,pad=0.02", fc=colors[st], ec="#fff", lw=2))
        ax.text(i + .46, .5, txt, ha="center", va="center", fontsize=13, fontweight="bold",
                color="#000" if st != "todo" else "#fff")
        if i < len(steps) - 1:
            ax.annotate("", xy=(i + 1.05, .5), xytext=(i + .87, .5), arrowprops=dict(arrowstyle="-|>", color="#fff", lw=2.5))
    ax.set_title("Green = done · Yellow = happening now · Grey = next", fontsize=15)
    return save(fig, "pipeline.png")


def pic_library():
    data = {}
    for p in (PROJECT_ROOT / "course/sources").glob("*.yaml"):
        for s in yaml.safe_load(open(p)) or []:
            data.setdefault(p.stem, {}).setdefault(s.get("kind", "?"), 0)
            data[p.stem][s.get("kind", "?")] += 1
    kinds = sorted({k for v in data.values() for k in v}, key=lambda k: -sum(v.get(k, 0) for v in data.values()))
    fig, ax = plt.subplots(figsize=(12, 4.2))
    left = np.zeros(len(kinds))
    for topic, c in (("shared", BLUE), ("leak", YELLOW), ("fluid", RED)):
        vals = np.array([data.get(topic, {}).get(k, 0) for k in kinds])
        ax.barh(kinds, vals, left=left, color=c, label=topic)
        left += vals
    ax.invert_yaxis(); ax.legend(fontsize=13); ax.set_xlabel("number of free sources found")
    ax.set_title(f"Research library: {int(left.sum())} free sources")
    return save(fig, "library.png")


def pic_real_rounds(book):
    runs = [r for r in book.runs(data_source="real")]
    if not runs:
        return None
    r = runs[0]
    rounds = book.rounds(r["id"])
    if not rounds:
        return None
    fig, ax = plt.subplots(figsize=(12, 4.4))
    xs = [x["round"] for x in rounds]
    ax.plot(xs, [x["accuracy"] for x in rounds], "o-", color=BLUE, lw=3, ms=10, label="practice quiz (other wells)")
    if r["holdout_accuracy"] is not None:
        ax.axhline(r["holdout_accuracy"], color=GREEN, lw=4, label=f"HONEST final exam: {r['holdout_accuracy']:.1%}")
    for x in rounds:
        m = json.loads(x["extra"] or "{}").get("model", "")
        ax.annotate(m.replace("_", " "), (x["round"], x["accuracy"]), textcoords="offset points", xytext=(0, 12),
                    ha="center", fontsize=10, color="#ccc")
    ax.set_ylim(0, 1); ax.set_xlabel("round"); ax.set_ylabel("accuracy"); ax.legend(fontsize=12, loc="lower right")
    ax.set_title(f"Real data ({r['notes']}): {r['status']}")
    return save(fig, "real_rounds.png")


def pic_well(well_pred=None):
    """A real well from FORCE 2020: log curves vs depth, the interpreter's answer, and V1's answer."""
    from modules.fluid.force2020 import CACHE, CURVES
    if not CACHE.exists():
        return None
    d = np.load(CACHE)
    hold_path = PROJECT_ROOT / "runs/fluid/force2020-lithology/holdout_groups.json"
    wells = json.loads(hold_path.read_text()) if hold_path.exists() else sorted(set(d["wells"]))
    w = wells[0]
    sel = d["wells"] == w
    X, y, dep = d["X"][sel], d["y"][sel], d["depth"][sel]
    tracks = [("GR", "gamma ray", "#66bb6a"), ("RHOB", "density", "#ef5350"), ("NPHI", "neutron", "#42a5f5"),
              ("DTC", "sonic", "#ffca28")]
    ncols = len(tracks) + 1 + (well_pred is not None)
    fig, axes = plt.subplots(1, ncols, figsize=(2.6 * ncols, 9), sharey=True)
    for ax, (c, lab, col) in zip(axes, tracks):
        ax.plot(X[:, CURVES.index(c)], dep, color=col, lw=1)
        ax.set_title(lab, fontsize=14)
    def litho_col(ax, labels, title):
        for i in range(len(dep) - 1):
            ax.axhspan(dep[i], dep[i + 1], color=LITHO_COLORS.get(labels[i], "#999"))
        ax.set_xticks([]); ax.set_title(title, fontsize=14)
    litho_col(axes[len(tracks)], y, "real answer")
    if well_pred is not None:
        litho_col(axes[-1], well_pred, "V1's answer")
    axes[0].invert_yaxis(); axes[0].set_ylabel("depth (m)")
    handles = [plt.Rectangle((0, 0), 1, 1, color=LITHO_COLORS[k]) for k in LITHO_COLORS if k in set(y)]
    fig.legend(handles, [k for k in LITHO_COLORS if k in set(y)], loc="lower center", ncol=5, fontsize=12)
    fig.suptitle(f"Real well {w} (North Sea){' · never seen in training' if hold_path.exists() else ''}", fontsize=17)
    fig.tight_layout(rect=(0, .07, 1, 1))
    return save(fig, "well.png")


def well_prediction():
    """V1's final model predicting a hold-out well, if a finished run exists."""
    import joblib
    from modules.fluid.force2020 import Force2020
    runs = sorted(glob.glob(str(PROJECT_ROOT / "runs/fluid/force2020-lithology/run_*/final.joblib")))
    hold_path = PROJECT_ROOT / "runs/fluid/force2020-lithology/holdout_groups.json"
    if not runs or not hold_path.exists():
        return None
    model = joblib.load(runs[-1])
    d = Force2020().load()
    w = json.loads(hold_path.read_text())[0]
    return model.predict(d["X"][d["groups"] == w])


# ------------------------------------------------------------------ page

PAGE = """<!doctype html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>V1 Dashboard</title>
<style>
body{{margin:0;background:#000;color:#fff;font:20px/1.4 -apple-system,Segoe UI,Roboto,sans-serif}}
main{{max-width:1100px;margin:0 auto;padding:16px}}
h1{{font-size:2.4rem;margin:.2em 0}} h2{{font-size:1.6rem;margin:1.4em 0 .3em}}
p{{color:#ccc;margin:.2em 0 .6em}} img{{width:100%;border-radius:12px;border:1px solid #333;display:block}}
.now{{background:#fbc02d;color:#000;font-weight:800;border-radius:10px;padding:10px 14px;display:inline-block}}
</style></head><body><main>
<h1>V1</h1><p>Updated {when}</p>
{running}
{blocks}
</main></body></html>"""


def build():
    book = Logbook(database_path())
    try:
        cat = yaml.safe_load(open(PROJECT_ROOT / "config/datasets.yaml")) or []
    except OSError:
        cat = []
    dls = book.downloads()
    real = {}
    for m in ("leak", "fluid"):
        rs = [r for r in book.runs(m, data_source="real") if r["holdout_accuracy"] is not None]
        real[m] = rs[0]["holdout_accuracy"] if rs else None
    running_runs = book.running()
    real["fluid_running"] = any(r["module"] == "fluid" for r in running_runs)
    lessons = book.course_status()
    done = sum(l["status"] == "passed" for l in lessons)
    has_dl = any(d["status"] == "done" for d in dls)
    has_real = real["leak"] is not None or real["fluid"] is not None
    state = ["done", "done" if lessons and done == len(lessons) else "now",
             "now" if has_dl else "todo", "now" if has_dl else "todo",
             "done" if (PROJECT_ROOT / "runs/fluid/force2020-lithology/holdout_groups.json").exists() else "todo",
             "done" if has_real else ("now" if real["fluid_running"] else "todo"),
             "done" if has_real else "todo"]

    blocks = []
    def add(title, img, caption=""):
        if img:
            blocks.append(f"<h2>{title}</h2>{f'<p>{caption}</p>' if caption else ''}<img src='{img}' alt='{title}'>")

    add("Progress", pic_progress(book, cat, dls, real))
    add("The plan", pic_pipeline(state))
    add("Real data: practice rounds and the honest score", pic_real_rounds(book),
        "Each dot is a round practising on some real wells and being quizzed on others. "
        "The green line is the final exam on wells it never saw.")
    pred = well_prediction()
    add("A real well: the answer vs V1's answer", pic_well(pred),
        "Left: the real measurements down the borehole. Right: the rock type at each depth.")
    add("How it teaches itself", pic_cycle(book))
    add("Every lesson, every try", pic_learning_curves(book))
    add("Things it got wrong (the actual signals)", pic_mistakes(book))
    add("Leak: what the cable sees", pic_das_examples())
    add("Fluid: what the rock tells us", pic_fluid_examples())
    add("Research library", pic_library())

    running = ""
    if running_runs:
        r = running_runs[0]
        running = (f"<div class='now'>RUNNING NOW: {r['module']} on {r['data_source']} data "
                   f"({r['notes']}) for {int((time.time() - r['started_at']) // 60)} min</div>")
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "index.html").write_text(PAGE.format(when=time.strftime("%b %d %H:%M"), running=running,
                                                 blocks="\n".join(blocks)))
    # artifact version: same page without the document wrapper (the host adds it)
    body = PAGE.format(when=time.strftime("%b %d %H:%M"), running=running, blocks="\n".join(blocks))
    style = body[body.index("<style>"):body.index("</style>") + 8].replace(
        "body{{", "body{{").replace("main{max-width:1100px;margin:0 auto;padding:16px}",
        "main{max-width:1100px;margin:0 auto;padding-block:16px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}")
    style = style.replace("<style>", "<style>:root{color-scheme:dark;background:#000}")
    main = body[body.index("<main>"):body.index("</main>") + 7]
    (SITE / "artifact.html").write_text("<title>V1 Progress</title>\n<meta name='claude:viewport-fit-sides' content='cover'>\n"
                                        + style + "\n" + main)
    return SITE


if __name__ == "__main__":
    print(build())
