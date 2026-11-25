"""V1 dashboard. Run with:  streamlit run dashboard/app.py

Big, high-contrast text so it reads well on a phone.
Phase 1: the layout and live data from the SQLite logbook. Charts and mistake plots fill in from Phase 4.
"""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st  # noqa: E402

from engine.config import database_path, load_region, region_is_set  # noqa: E402
from engine.db import Logbook  # noqa: E402

MODULES = {"leak": "Leak — DAS leak finder", "fluid": "Fluid — what's underground"}
STATUS_COLOR = {"idle": "#9aa0a6", "running": "#ffd400", "finished": "#00e676", "failed": "#ff5252"}

st.set_page_config(page_title="V1", layout="wide")
st.markdown(
    """
    <style>
      html, body, [class*="css"], .stApp { background:#000 !important; color:#fff !important; font-size:22px; }
      header[data-testid="stHeader"] { background:#000 !important; }
      h1 { font-size:2.6rem !important; } h2 { font-size:2rem !important; } h3 { font-size:1.6rem !important; }
      p, li, label, .stMarkdown, .stMetric { font-size:1.35rem !important; }
      [data-testid="stMetricValue"] { font-size:2.4rem !important; color:#fff !important; }
      [data-testid="stMetricLabel"] p { font-size:1.2rem !important; color:#e0e0e0 !important; }
      .badge { display:inline-block; padding:4px 14px; border-radius:8px; font-weight:800; color:#000; }
      .card { border:2px solid #fff; border-radius:12px; padding:14px 18px; margin-bottom:14px; }
    </style>
    """,
    unsafe_allow_html=True,
)


def fmt_secs(s: float) -> str:
    s = int(s)
    h, rem = divmod(s, 3600)
    m, sec = divmod(rem, 60)
    return f"{h}h {m}m" if h else f"{m}m {sec}s"


book = Logbook(database_path())
region = load_region()

st.title("V1")

# --- Region ---------------------------------------------------------------
st.header("Region")
if region_is_set(region):
    b = region["bounding_box"]
    st.markdown(f"**{region['name']}**  \nLat {b['min_lat']} to {b['max_lat']}, Lon {b['min_lon']} to {b['max_lon']}")
    st.markdown(f"Data sources: {len(region['data_sources'])}")
else:
    st.markdown("**Not set yet.** Fill in `config/region.yaml`.")

# --- Modules --------------------------------------------------------------
st.header("Modules")
cols = st.columns(len(MODULES))
for col, (key, title) in zip(cols, MODULES.items()):
    status = book.module_status(key)
    runs = book.runs(key)
    with col:
        st.markdown(
            f"<div class='card'><h3>{title}</h3>"
            f"<span class='badge' style='background:{STATUS_COLOR[status]}'>{status.upper()}</span></div>",
            unsafe_allow_html=True,
        )
        if runs:
            latest = runs[0]
            rounds = book.rounds(latest["id"])
            if rounds:
                st.line_chart({"accuracy": [r["accuracy"] for r in rounds]}, height=220)
            if latest["holdout_accuracy"] is not None:
                st.metric("Honest hold-out accuracy", f"{latest['holdout_accuracy']:.1%}")
            mistakes = book.latest_mistakes(key, limit=5)
            if mistakes:
                st.markdown("**Latest mistakes**")
                for m in mistakes:
                    st.markdown(f"- round {m['round']}: said **{m['pred_label']}**, was **{m['true_label']}**")
        else:
            st.markdown("No runs yet.")

# --- Running now ----------------------------------------------------------
st.header("Running now")
running = book.running()
if running:
    for r in running:
        st.markdown(f"- **{r['module']}** on **{r['machine']}** for {fmt_secs(time.time() - r['started_at'])}")
else:
    st.markdown("Nothing running.")

# --- Cost -----------------------------------------------------------------
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
