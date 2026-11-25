"""V1 dashboard. Run with:  streamlit run dashboard/app.py

Big, high-contrast text so it reads well on a phone.
Tabs: Overview (honest real-data accuracy), Course (every pass/fail), Data (downloads), Library (sources).
"""
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import numpy as np  # noqa: E402
import streamlit as st  # noqa: E402
import yaml  # noqa: E402

from engine.config import database_path, load_region, region_is_set  # noqa: E402
from engine.db import Logbook  # noqa: E402

MODULES = {"leak": "Leak — DAS leak finder", "fluid": "Fluid — what's underground"}
STATUS_COLOR = {"idle": "#9aa0a6", "running": "#ffd400", "finished": "#00e676", "failed": "#ff5252",
                "passed": "#00e676", "stuck": "#ff5252", "in_progress": "#ffd400", "not_started": "#9aa0a6"}

st.set_page_config(page_title="V1", layout="wide")
st.markdown(
    """
    <style>
      html, body, [class*="css"], .stApp { background:#000 !important; color:#fff !important; font-size:22px; }
      header[data-testid="stHeader"] { background:#000 !important; }
      h1 { font-size:2.6rem !important; } h2 { font-size:2rem !important; } h3 { font-size:1.6rem !important; }
      p, li, label, .stMarkdown { font-size:1.3rem !important; }
      [data-testid="stMetricValue"] { font-size:2.4rem !important; color:#fff !important; }
      [data-testid="stMetricLabel"] p { font-size:1.15rem !important; color:#e0e0e0 !important; }
      button[data-baseweb="tab"] p { font-size:1.3rem !important; font-weight:700; }
      [data-testid="stExpander"] summary p { font-size:1.2rem !important; }
      [data-testid="stRadio"] p, [data-testid="stWidgetLabel"] p, [data-testid="stCheckbox"] p { color:#fff !important; opacity:1 !important; }
      .badge { display:inline-block; padding:4px 14px; border-radius:8px; font-weight:800; color:#000; }
      .card { border:2px solid #fff; border-radius:12px; padding:14px 18px; margin-bottom:14px; }
      .big { font-size:3rem; font-weight:900; }
    </style>
    """,
    unsafe_allow_html=True,
)


def badge(status):
    return f"<span class='badge' style='background:{STATUS_COLOR.get(status, '#9aa0a6')}'>{status.replace('_', ' ').upper()}</span>"


def fmt_secs(s: float) -> str:
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h {m}m" if h else f"{m}m {sec}s"


def fmt_when(t):
    return time.strftime("%b %d %H:%M:%S", time.localtime(t))


def human(n):
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024 or unit == "TB":
            return f"{n:.1f} {unit}"
        n /= 1024


@st.cache_data(ttl=300)
def library():
    srcs, notes, words = [], 0, 0
    for p in sorted((ROOT / "course" / "sources").glob("*.yaml")):
        try:
            srcs += yaml.safe_load(open(p)) or []
        except yaml.YAMLError:
            pass
    for p in (ROOT / "course" / "notes").rglob("*.md"):
        notes += 1
        words += len(p.read_text(errors="ignore").split())
    return srcs, notes, words


def plot_example(path):
    try:
        a = np.load(ROOT / path)
    except OSError:
        st.markdown("(file missing)")
        return
    if a.ndim == 1:
        st.line_chart(a, height=160)
    elif a.ndim == 2 and a.shape[0] > 3:   # DAS waterfall: channels x time
        img = np.abs(a); img = img / (np.percentile(img, 99) + 1e-9)
        st.image(np.clip(img, 0, 1), caption="waterfall (rows = cable position, across = time)",
                 use_container_width=True)
    else:
        st.line_chart({f"row {i}": r for i, r in enumerate(np.atleast_2d(a))}, height=160)


book = Logbook(database_path())
region = load_region()
st.title("V1")
tab_over, tab_course, tab_data, tab_lib = st.tabs(["Overview", "Course", "Data", "Library"])

# ====================================================================== OVERVIEW
with tab_over:
    st.header("Honest accuracy on real data")
    st.markdown("Scored once, on wells or recording blocks the model never saw.")
    cols = st.columns(len(MODULES))
    for col, (key, title) in zip(cols, MODULES.items()):
        real = [r for r in book.runs(key, data_source="real") if r["holdout_accuracy"] is not None]
        status = book.module_status(key)
        with col:
            st.markdown(f"<div class='card'><h3>{title}</h3>{badge(status)}</div>", unsafe_allow_html=True)
            if real:
                r = real[0]
                st.markdown(f"<div class='big'>{r['holdout_accuracy']:.1%}</div>", unsafe_allow_html=True)
                st.markdown(f"{r['notes']} · {fmt_when(r['finished_at'])}")
                rounds = book.rounds(r["id"])
                if rounds:
                    st.markdown("**Accuracy per round** (practice tests, not the hold-out)")
                    st.line_chart({"accuracy": [x["accuracy"] for x in rounds]}, height=220)
            else:
                st.markdown("**No real-data result yet.**")
            mistakes = book.latest_mistakes(key, limit=5)
            if mistakes:
                st.markdown("**Latest mistakes**")
                for m in mistakes:
                    st.markdown(f"- round {m['round']}, example {m['example_id']}: said **{m['pred_label']}**, was **{m['true_label']}**")

    st.header("Running now")
    running = book.running()
    if running:
        for r in running:
            st.markdown(f"- **{r['module']}** ({r['data_source']}) on **{r['machine']}** for {fmt_secs(time.time() - r['started_at'])}")
    else:
        st.markdown("Nothing running.")

    st.header("Region")
    if region_is_set(region):
        b = region["bounding_box"]
        st.markdown(f"**{region['name']}**: lat {b['min_lat']} to {b['max_lat']}, lon {b['min_lon']} to {b['max_lon']}")
    else:
        st.markdown("**Not set yet.** Fill in `config/region.yaml`.")

    st.header("Cost")
    c1, c2 = st.columns(2)
    c1.metric("Claude credits spent", f"{book.total_credits():,.2f}")
    c2.metric("Compute time", fmt_secs(book.total_compute_seconds()))
    with st.form("credits"):
        amount = st.number_input("Add credits spent", min_value=0.0, step=1.0)
        note = st.text_input("Note (optional)")
        if st.form_submit_button("Add") and amount > 0:
            book.add_credits(amount, note)
            st.rerun()

# ====================================================================== COURSE
with tab_course:
    lessons = book.course_status()
    attempts = book.attempts(limit=2000)
    srcs, n_notes, n_words = library()
    st.header("Course progress")
    if not lessons:
        st.markdown("The course hasn't run yet: `python -m engine.course.runner`")
    else:
        done = sum(l["status"] == "passed" for l in lessons)
        stuck = sum(l["status"] == "stuck" for l in lessons)
        left = len(lessons) - done
        st.progress(done / len(lessons), text=f"{done} of {len(lessons)} lessons passed")
        c = st.columns(3)
        c[0].metric("Lessons passed", done)
        c[1].metric("Lessons left", left)
        c[2].metric("Stuck", stuck)
        c = st.columns(3)
        c[0].metric("Attempts", len(attempts))
        c[1].metric("Fails", sum(a["outcome"] == "fail" for a in attempts))
        c[2].metric("Passes", sum(a["outcome"] == "pass" for a in attempts))
        st.markdown(f"**Course size:** {len(lessons)} graded lessons · {len(srcs)} sources · "
                    f"{n_notes} study notes ({n_words:,} words)")

        st.header("Lessons")
        for l in lessons:
            extra = f" · best {l['best_score']:.0%}" if l["best_score"] is not None else ""
            extra += f" · final exam {l['exam_score']:.0%}" if l["exam_score"] is not None else ""
            st.markdown(f"{badge(l['status'])} **{l['title']}** ({l['track']}) · {l['attempts'] or 0} attempts{extra}",
                        unsafe_allow_html=True)

        st.header("Every attempt")
        show = st.radio("Show", ["Fails", "Passes", "All"], horizontal=True)
        for a in attempts:
            if show == "Fails" and a["outcome"] != "fail" or show == "Passes" and a["outcome"] != "pass":
                continue
            icon = "✅" if a["outcome"] == "pass" else "❌"
            with st.expander(f"{icon} {a['lesson_id']} · attempt {a['attempt']} · {a['score']:.0%} (needed {a['threshold']:.0%})"):
                st.markdown(f"**When:** {fmt_when(a['started_at'])}, took {a['finished_at'] - a['started_at']:.1f}s")
                st.markdown(f"**What it tried:** {a['tried']}")
                st.markdown(f"**Practice score:** {a['train_score']:.0%} · **Quiz score:** {a['score']:.0%}")
                if a["outcome"] == "fail":
                    st.markdown(f"**Why it failed:** {a['why']}")
                    st.markdown(f"**Where:** {a['where_failed']}")
                    st.markdown(f"**What it changes next:** {a['fix_next']}")
                else:
                    st.markdown(f"**Final exam (never-seen examples):** {a['exam_score']:.0%}")
                    if a["why"]:
                        st.markdown(f"**Warning:** {a['why']}")
                conf = (a["details"] or {}).get("confusions")
                if conf:
                    st.markdown("**Mix-ups:** " + ", ".join(f"{c['true']} → {c['pred']} ×{c['count']}" for c in conf))
                ms = a["mistakes"] or []
                if ms and st.checkbox("Show the examples it got wrong", key=f"m{a['id']}"):
                    for m in ms[:3]:
                        st.markdown(f"was **{m['true']}**, it said **{m['pred']}**")
                        plot_example(m["file"])

# ====================================================================== DATA
with tab_data:
    st.header("Real data downloads")
    try:
        cat = yaml.safe_load(open(ROOT / "config" / "datasets.yaml")) or []
    except (OSError, yaml.YAMLError):
        cat = []
    dls = book.downloads()
    got = {d["entry_id"]: d for d in reversed(dls)}
    total = sum(d["bytes"] or 0 for d in got.values() if d["status"] == "done")
    st.metric("Downloaded so far", human(total))
    for e in sorted(cat, key=lambda e: (e.get("priority", 9), e["id"])):
        d = got.get(e["id"])
        state = "done" if d and d["status"] == "done" else ("failed" if d else "not downloaded")
        size = human(e["size_bytes"]) if e.get("size_bytes") else "size unknown"
        login = " · needs login" if e.get("needs_login") else ""
        st.markdown(f"**{e['id']}** ({e.get('module', '')}) · {size}{login} · **{state}**  \n{e.get('labels', '')}")

# ====================================================================== LIBRARY
with tab_lib:
    srcs, n_notes, n_words = library()
    st.header(f"Library: {len(srcs)} sources")
    kinds = {}
    for s in srcs:
        kinds[s.get("kind", "?")] = kinds.get(s.get("kind", "?"), 0) + 1
    st.markdown(" · ".join(f"{k}: {v}" for k, v in sorted(kinds.items(), key=lambda kv: -kv[1])))
    topic = st.radio("Topic", ["all", "leak", "fluid", "shared"], horizontal=True)
    for s in srcs:
        if topic != "all" and s.get("topic") != topic:
            continue
        st.markdown(f"- [{s.get('title', s.get('id'))}]({s.get('url', '')}) · {s.get('kind', '')} · {s.get('level', '')}  \n  {s.get('summary', '')}")
