"""Builds a single self-contained HTML page of the dashboard (progress + step-by-step diagrams).

    python -m dashboard.snapshot            -> writes dashboard/v1_dashboard.html

It's a snapshot: re-run it to refresh. Good for viewing on a phone or in the Claude app side panel.
"""
from __future__ import annotations

import base64
import html
import io
import time
from pathlib import Path

import numpy as np
import yaml
from PIL import Image

from engine.config import PROJECT_ROOT, database_path, load_region, load_settings, region_is_set
from engine.course.generators import REGISTRY
from engine.db import Logbook

OUT = PROJECT_ROOT / "dashboard" / "v1_dashboard.html"
E = html.escape


# ------------------------------------------------------------------ little drawing helpers

def png_b64(arr, w=220, h=140):
    from scipy.ndimage import uniform_filter1d
    a = np.sqrt(uniform_filter1d(arr.astype(float) ** 2, 24, axis=1))    # smoothed loudness, so steady things show
    a = a - np.percentile(a, 30)
    a = np.clip(a / (np.percentile(a, 99.5) + 1e-9), 0, 1)
    img = Image.fromarray((255 * (1 - a)).astype(np.uint8)).resize((w, h), Image.NEAREST)
    buf = io.BytesIO(); img.save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode()


def spark(y, w=220, h=70, color="#4fc3f7"):
    y = np.asarray(y, float)
    y = (y - y.min()) / (np.ptp(y) + 1e-12)
    xs = np.linspace(2, w - 2, len(y)); ys = h - 4 - y * (h - 8)
    pts = " ".join(f"{a:.1f},{b:.1f}" for a, b in zip(xs, ys))
    return f"<svg viewBox='0 0 {w} {h}' class='spark'><polyline points='{pts}' fill='none' stroke='{color}' stroke-width='2'/></svg>"


def bar(frac, label="", color="#00e676"):
    frac = max(0.0, min(1.0, frac))
    return (f"<div class='bar'><div class='fill' style='width:{frac*100:.0f}%;background:{color}'></div>"
            f"<span>{E(label)}</span></div>")


def score_bar(score, thr, passed):
    c = "#00e676" if passed else "#ff5252"
    return (f"<div class='bar sb'><div class='fill' style='width:{score*100:.0f}%;background:{c}'></div>"
            f"<div class='thr' style='left:{thr*100:.0f}%'></div><span>{score:.0%} (needs {thr:.0%})</span></div>")


def flow(steps):
    """Vertical step-by-step diagram. steps = [(title, text, state)] state in done/now/todo/fail/branch."""
    out = ["<div class='flow'>"]
    for i, (title, text, state) in enumerate(steps, 1):
        out.append(f"<div class='step {state}'><div class='num'>{i}</div><div><b>{E(title)}</b><p>{text}</p></div></div>")
        if i < len(steps):
            out.append("<div class='arrow'>▼</div>")
    out.append("</div>")
    return "".join(out)


def fmt_when(t):
    return time.strftime("%b %d, %H:%M:%S", time.localtime(t)) if t else ""


# ------------------------------------------------------------------ data

def library():
    out = {}
    for p in sorted((PROJECT_ROOT / "course" / "sources").glob("*.yaml")):
        try:
            out[p.stem] = yaml.safe_load(open(p)) or []
        except yaml.YAMLError:
            out[p.stem] = []
    notes = {d.name: sorted(x.name for x in d.glob("*.md")) for d in (PROJECT_ROOT / "course" / "notes").glob("*") if d.is_dir()}
    words = sum(len(p.read_text(errors="ignore").split()) for p in (PROJECT_ROOT / "course" / "notes").rglob("*.md"))
    return out, notes, words


def examples():
    """Real pictures from the simulators, so the diagrams show what the machine actually sees."""
    rng = np.random.default_rng(7)
    das = {}
    X, y, _ = REGISTRY["das_five_events"]["fn"](10, rng)
    for xi, yi in zip(X, y):
        das.setdefault(str(yi), xi)
    tr = {}
    X, y, _ = REGISTRY["signal_shapes"]["fn"](8, rng)
    for xi, yi in zip(X, y):
        tr.setdefault(str(yi), xi[:400])
    att = {}
    X, y, _ = REGISTRY["attenuation_q"]["fn"](4, rng)
    for xi, yi in zip(X, y):
        att.setdefault(str(yi), xi[300:700])
    sh = {}
    X, y, _ = REGISTRY["s_wave_shadow"]["fn"](6, np.random.default_rng(3))
    for xi, yi in zip(X, y):
        sh.setdefault(str(yi), xi)
    return das, tr, att, sh


# ------------------------------------------------------------------ page

CSS = """
:root{--bg:#000;--fg:#fff;--mut:#cfcfcf;--card:#111;--line:#fff;--ok:#00e676;--bad:#ff5252;--now:#ffd400;--info:#4fc3f7}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:20px/1.45 -apple-system,Segoe UI,Roboto,sans-serif}
main{max-width:980px;margin:0 auto;padding:16px}
h1{font-size:2.2rem;margin:.2em 0}h2{font-size:1.6rem;margin:1.6em 0 .4em;border-bottom:2px solid #444;padding-bottom:.2em}
h3{font-size:1.25rem;margin:.6em 0 .3em}p{margin:.3em 0}.mut{color:var(--mut)}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:12px}
.card{background:var(--card);border:2px solid #555;border-radius:12px;padding:12px 14px}
.big{font-size:2.4rem;font-weight:900;line-height:1.1}
.bar{position:relative;height:30px;background:#333;border-radius:8px;overflow:hidden;margin:6px 0}
.bar .fill{height:100%}.bar span{position:absolute;left:10px;top:2px;font-weight:800;color:#fff;text-shadow:0 0 3px #000,0 0 3px #000;font-size:1rem}
.thr{position:absolute;top:0;bottom:0;width:3px;background:#fff}
.badge{display:inline-block;padding:2px 10px;border-radius:7px;font-weight:900;color:#000;font-size:.9rem}
.passed,.done{--c:var(--ok)}.stuck,.fail{--c:var(--bad)}.in_progress,.now{--c:var(--now)}.not_started,.todo{--c:#9aa0a6}.branch{--c:var(--info)}
.badge{background:var(--c)}
.flow{display:flex;flex-direction:column;align-items:stretch}
.step{display:flex;gap:12px;align-items:flex-start;border:2px solid var(--c);border-left-width:8px;border-radius:10px;padding:10px 12px;background:#0b0b0b}
.step p{color:var(--mut);font-size:1rem}.num{min-width:34px;height:34px;border-radius:50%;background:var(--c);color:#000;font-weight:900;display:flex;align-items:center;justify-content:center}
.arrow{text-align:center;color:#888;font-size:1.1rem;line-height:1.2}
.legend span{margin-right:12px;font-size:.95rem}
.pics{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px}
.pics figure{margin:0;background:#fff;border-radius:8px;padding:4px;color:#000;text-align:center;font-weight:800;font-size:.95rem}
.pics img,.pics svg{width:100%;display:block;border-radius:4px}
.spark{background:#0b0b0b}
details{border:1px solid #555;border-radius:10px;padding:8px 12px;margin:6px 0;background:#0b0b0b}
summary{cursor:pointer;font-weight:700;font-size:1.05rem}
details p{font-size:1rem;color:var(--mut)}details b{color:#fff}
table{border-collapse:collapse;width:100%;font-size:1rem}td,th{border-bottom:1px solid #333;padding:6px 4px;text-align:left}
a{color:var(--info)}
.split{display:grid;grid-template-columns:1fr 1fr;gap:12px}@media(max-width:640px){.split{grid-template-columns:1fr}body{font-size:18px}}
"""


def build():
    settings = load_settings()
    book = Logbook(database_path(settings))
    lessons = book.course_status()
    attempts = book.attempts(limit=5000)
    srcs, notes, words = library()
    das, tr, att, sh = examples()
    running = book.running()
    region = load_region()
    try:
        cat = yaml.safe_load(open(PROJECT_ROOT / "config" / "datasets.yaml")) or []
    except OSError:
        cat = []
    dls = book.downloads()
    real = {m: [r for r in book.runs(m, data_source="real") if r["holdout_accuracy"] is not None] for m in ("leak", "fluid")}

    tracks = {"shared": "Foundations", "leak": "Leak (DAS)", "fluid": "Fluid (rock)"}
    by_track = {t: [l for l in lessons if l["track"] == t] for t in tracks}
    att_by_lesson = {}
    for a in reversed(attempts):
        att_by_lesson.setdefault(a["lesson_id"], []).append(a)
    n_src = sum(len(v) for v in srcs.values())
    n_notes = sum(len(v) for v in notes.values())
    done = sum(l["status"] == "passed" for l in lessons)
    current = next((l for l in lessons if l["status"] == "in_progress"), None)

    h = [f"<!doctype html><html lang='en'><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'>"
         f"<title>V1 Dashboard</title><style>{CSS}</style></head><body><main>"]
    h.append(f"<h1>V1</h1><p class='mut'>Snapshot taken {fmt_when(time.time())}. "
             f"Re-run <code>python -m dashboard.snapshot</code> to refresh.</p>")

    # ---------------- right now
    h.append("<h2>Right now</h2><div class='card'>")
    if running:
        for r in running:
            what = f"lesson: <b>{E(current['title'])}</b>" if (r["module"] == "course" and current) else ""
            h.append(f"<p><span class='badge now'>RUNNING</span> <b>{E(r['module'])}</b> ({E(r['data_source'] or '')}) on "
                     f"{E(r['machine'])} for {int(time.time() - r['started_at'])}s {what}</p>")
    else:
        h.append("<p>Nothing running.</p>")
    h.append(f"<p class='mut'>Region: {E(region['name']) if region_is_set(region) else 'not set yet (config/region.yaml)'}</p></div>")

    # ---------------- progress by area
    h.append("<h2>Progress by area</h2><div class='grid'>")
    h.append(f"<div class='card'><h3>1 · Research library</h3><div class='big'>{n_src}</div><p>sources found</p>"
             + "".join(f"<p class='mut'>{E(k)}: {len(v)} sources, {len(notes.get(k, []))} notes</p>" for k, v in srcs.items())
             + f"<p class='mut'>{n_notes} study notes, {words:,} words</p></div>")
    h.append(f"<div class='card'><h3>2 · Warm-up course</h3><div class='big'>{done}/{len(lessons)}</div><p>lessons passed</p>"
             + bar(done / max(1, len(lessons)), f"{len(lessons) - done} left")
             + "".join(bar(sum(l['status'] == 'passed' for l in ls) / max(1, len(ls)),
                           f"{tracks[t]}: {sum(l['status'] == 'passed' for l in ls)}/{len(ls)}", "#4fc3f7")
                       for t, ls in by_track.items())
             + f"<p class='mut'>{len(attempts)} attempts · {sum(a['outcome'] == 'fail' for a in attempts)} fails · "
               f"{sum(a['outcome'] == 'pass' for a in attempts)} passes</p></div>")
    ok_dl = {d["entry_id"] for d in dls if d["status"] == "done"}
    h.append(f"<div class='card'><h3>3 · Real data downloads</h3><div class='big'>{len(ok_dl)}/{len(cat)}</div>"
             f"<p>pieces downloaded</p>{bar(len(ok_dl) / max(1, len(cat)), 'downloaded') if cat else ''}"
             f"<p class='mut'>{'Dataset map not built yet (config/datasets.yaml).' if not cat else ''}</p>"
             "<p class='mut'>Anything over 5 GB waits for your OK.</p></div>")
    for m, title in (("leak", "4 · Leak on real data"), ("fluid", "5 · Fluid on real data")):
        r = real[m]
        val = f"{r[0]['holdout_accuracy']:.1%}" if r else "—"
        h.append(f"<div class='card'><h3>{title}</h3><div class='big'>{val}</div><p>honest hold-out accuracy</p>"
                 f"<p class='mut'>{'Scored once on wells/time blocks it never saw.' if r else 'Not run yet: needs real data first.'}</p></div>")
    h.append("</div>")

    # ---------------- big picture diagram
    st_lib = "done" if n_src else "todo"
    st_course = "done" if lessons and done == len(lessons) else ("now" if any(l["status"] != "not_started" for l in lessons) else "todo")
    st_dl = "done" if cat and len(ok_dl) == len(cat) else ("now" if ok_dl else "todo")
    st_real = "done" if real["leak"] or real["fluid"] else "todo"
    h.append("<h2>How V1 works: the big picture</h2>")
    h.append("<p class='legend'><span class='badge done'>DONE</span><span class='badge now'>IN PROGRESS</span>"
             "<span class='badge todo'>NOT YET</span></p>")
    h.append(flow([
        ("Gather the knowledge", f"Free courses, textbooks, papers, datasets and code from the web are catalogued, and each topic "
         f"is turned into a plain-English study note with 'checkable facts'. <b>{n_src} sources, {n_notes} notes.</b>", st_lib),
        ("Warm up on synthetic data", "Each idea in the notes becomes a graded lesson. A physics simulator makes unlimited practice "
         f"examples with known answers. The machine has to pass each lesson before it moves on. <b>{done}/{len(lessons)} passed.</b>", st_course),
        ("Download real data", "Equinor Volve, F3 Netherlands, PubDAS and Utah FORGE DAS. Size is checked first: "
         "anything over 5 GB waits for your OK.", st_dl),
        ("Label it from known answers", "Wells say where oil/water/gas really is (fluid). FORGE event catalogues say when the "
         "ground really shook (DAS). Those become the answer key.", st_real),
        ("Lock away the final exam", "Whole wells / whole time blocks are set aside and never trained on. This is the honest number.", st_real),
        ("Teach itself in rounds", "Train → hide answers → predict → grade itself → study its mistakes harder → retrain. "
         "Stops when it stops improving.", st_real),
        ("Report the honest score", "The locked-away exam is scored once and shown at the top of this page.", st_real),
    ]))

    # ---------------- lesson loop diagram
    h.append("<h2>How one lesson works, step by step</h2>")
    cur_txt = f" Right now: <b>{E(current['title'])}</b>." if current else ""
    h.append(f"<p class='mut'>Every lesson in the course runs this loop.{cur_txt}</p>")
    h.append(flow([
        ("Make practice examples", "The simulator generates ~300 examples with answers (e.g. 'this waterfall has a leak at channel 14').", "branch"),
        ("Make a quiz and hide the answers", "300 fresh examples it has never seen. Answers are kept from the student.", "branch"),
        ("Study", "It turns each signal into numbers (features), then fits a model. It starts with the crudest way of looking "
         "(raw statistics) and the simplest model (a straight line), on purpose.", "branch"),
        ("Take the quiz and grade itself", "Accuracy, precision, recall. Every wrong answer is saved, with the signal itself.", "branch"),
        ("PASS? → final exam", "If it beats the pass mark, it sits a final exam on a third set it has never seen. That score is the honest one.", "done"),
        ("FAIL? → work out WHY", "<b>Can't even get practice right</b> = it's looking at the wrong things (underfit). "
         "<b>Practice good, quiz bad</b> = it memorised (overfit). <b>Close</b> = it needs precision.", "fail"),
        ("…and WHERE", "It slices the quiz by condition (noise level, wind, speed, porosity…) and finds where it fails most, "
         "e.g. 'fails 62% when SNR is below −12 dB'.", "fail"),
        ("Pick a fix", "Underfit → unlock a new way of looking (spectrum, spatial, moveout…) or a smarter model. "
         "Overfit → more examples. Weak spot → extra practice in exactly that condition.", "fail"),
        ("Re-study its mistakes", "Every quiz question it got wrong goes back into practice with 2–3× weight. Then back to step 1.", "fail"),
        ("Give up after 8 tries", "Marked STUCK and logged, so you can see it. The course moves on.", "todo"),
    ]))

    # ---------------- leak explainer
    h.append("<h2>Leak module: what it's looking at</h2>")
    h.append("<p class='mut'>A fiber-optic cable buried along a pipe acts like thousands of microphones. "
             "A <b>waterfall</b> plot shows every spot on the cable (rows) over time (across). Dark = shaking.</p><div class='pics'>")
    for k in ("quiet", "traffic", "leak", "digging", "wind"):
        if k in das:
            h.append(f"<figure><img src='{png_b64(das[k])}' alt='{k} waterfall'>{k}</figure>")
    h.append("</div>")
    h.append(flow([
        ("Traffic", "A diagonal streak. The car moves along the cable, so its slope = its speed.", "branch"),
        ("Leak", "A thin, steady horizontal line in one spot: a narrow-band hiss that never stops.", "branch"),
        ("Digging", "Short, sharp bursts in one place.", "branch"),
        ("Wind", "Gentle low-frequency shaking all along the cable at once.", "branch"),
        ("How it tells them apart", "Spectrum (which pitches?), spatial (where?), stationarity (steady or bursty?), "
         "moveout (does it travel?), local spectrum (is one spot humming?).", "done"),
    ]))

    # ---------------- fluid explainer
    h.append("<h2>Fluid module: what it's looking at</h2>")
    h.append("<p class='mut'>Rock is a sponge of mineral grains with pores. The pores hold brine, oil, gas or air, "
             "and each changes how sound travels.</p><div class='pics'>")
    for k, v in att.items():
        h.append(f"<figure>{spark(v)}{'sharp pulse: high Q (tight rock)' if k == 'high_q' else 'dull pulse: low Q (fluid soaks up highs)'}</figure>")
    for k in ("none", "liquid", "gas"):
        if k in sh:
            h.append(f"<figure>{spark(sh[k][1], color='#e53935')}S-wave strength along surface: {k} pocket</figure>")
    h.append("</div>")
    h.append(flow([
        ("P-waves (push-pull)", "Travel through rock AND fluid. They slow down a lot in gas.", "branch"),
        ("S-waves (side-to-side)", "Can't travel through liquid. Sensors above a fluid pocket see an S-wave 'shadow'.", "branch"),
        ("Gassmann's equation", "Predicts how much faster the rock gets when you swap gas for brine in the pores.", "branch"),
        ("AVO", "How strongly a layer reflects at wider angles. Gas sands get dimmer or brighter in a telltale way.", "branch"),
        ("Attenuation (Q)", "Fluids soak up high frequencies, so the pulse arrives duller.", "branch"),
        ("Real answer key", "Wells drilled into the field measured what's really there. Those depths are the labels.", "done"),
    ]))

    # ---------------- real data loop
    h.append("<h2>Real-data loop and the honest score</h2>")
    h.append(flow([
        ("Check size before downloading", "HTTP/S3 size check. ≤ 5 GB: download (resumes if cut off). > 5 GB: stop and ask you.", "branch"),
        ("Build the answer key", "Fluid: well-log interpretation (water saturation) → water/hydrocarbon at each depth. "
         "DAS: published event catalogues → 'event' / 'no event' for each time window.", "branch"),
        ("Lock away whole wells / time blocks", "Saved to disk once. Never trained on, never used to pick settings.", "fail"),
        ("Warm up", "A few synthetic examples per class help it start; they count half as much as real ones.", "branch"),
        ("Rounds", "Different wells play 'quiz' each round. Mistakes get double weight next round; "
         "if it plateaus it tries a smarter model.", "branch"),
        ("Stop", "After 3 rounds with no improvement, or 10 rounds.", "branch"),
        ("Score the locked set once", "That number goes on the dashboard as the honest accuracy.", "done"),
    ]))

    # ---------------- every lesson, every attempt
    h.append("<h2>Every lesson, every attempt</h2>")
    for t, ls in by_track.items():
        h.append(f"<h3>{tracks[t]}</h3>")
        for l in ls:
            atts = att_by_lesson.get(l["lesson_id"], [])
            extra = f" · final exam {l['exam_score']:.0%}" if l["exam_score"] is not None else ""
            h.append(f"<details {'open' if l['status'] in ('stuck', 'in_progress') else ''}><summary>"
                     f"<span class='badge {l['status']}'>{l['status'].replace('_', ' ').upper()}</span> {E(l['title'])} "
                     f"· {len(atts)} attempt(s){extra}</summary>")
            for a in atts:
                ok = a["outcome"] == "pass"
                h.append(f"<p><b>{'✅' if ok else '❌'} Attempt {a['attempt']}</b> · {fmt_when(a['started_at'])} · "
                         f"{a['finished_at'] - a['started_at']:.1f}s</p>{score_bar(a['score'], a['threshold'], ok)}"
                         f"<p><b>Tried:</b> {E(a['tried'])}</p><p><b>Practice:</b> {a['train_score']:.0%} · <b>Quiz:</b> {a['score']:.0%}</p>")
                if ok:
                    h.append(f"<p><b>Final exam (never seen):</b> {a['exam_score']:.0%}</p>")
                    if a["why"]:
                        h.append(f"<p><b>Warning:</b> {E(a['why'])}</p>")
                else:
                    h.append(f"<p><b>Why:</b> {E(a['why'])}</p><p><b>Where:</b> {E(a['where_failed'])}</p>"
                             f"<p><b>Next:</b> {E(a['fix_next'])}</p>")
                conf = (a["details"] or {}).get("confusions")
                if conf:
                    h.append("<p><b>Mix-ups:</b> " + E(", ".join(f"{c['true']} → {c['pred']} ×{c['count']}" for c in conf)) + "</p>")
                h.append("<hr style='border-color:#333'>")
            h.append("</details>")

    # ---------------- downloads
    h.append("<h2>Real datasets</h2>")
    if cat:
        h.append("<table><tr><th>Piece</th><th>Size</th><th>Labels</th><th>Status</th></tr>")
        for e in sorted(cat, key=lambda e: (e.get("priority", 9), e["id"])):
            sz = f"{e['size_bytes'] / 1e9:.2f} GB" if e.get("size_bytes") else "?"
            st = "downloaded" if e["id"] in ok_dl else ("needs login" if e.get("needs_login") else "waiting")
            h.append(f"<tr><td>{E(e['id'])}</td><td>{sz}</td><td>{E(str(e.get('labels', ''))[:90])}</td><td>{st}</td></tr>")
        h.append("</table>")
    else:
        h.append("<p class='mut'>Dataset map (config/datasets.yaml) not built yet. Known so far: Utah FORGE DAS is "
                 "downloadable from here; Volve now requires registration (Databricks Marketplace); "
                 "F3 Netherlands 1.7 GB; FORCE 2020 well logs 170 MB.</p>")

    h.append("<h2>Cost</h2><div class='grid'>"
             f"<div class='card'><p>Claude credits (entered by you)</p><div class='big'>{book.total_credits():,.2f}</div></div>"
             f"<div class='card'><p>Compute time</p><div class='big'>{int(book.total_compute_seconds() // 60)} min</div></div></div>")
    h.append("</main></body></html>")
    OUT.write_text("".join(h))
    return OUT


if __name__ == "__main__":
    print(build())
