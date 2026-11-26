"""Render the record book: RECORD_BOOK.md (for GitHub) + records/site/record_book.html (web page) + a progress chart.

    python -m records.build
"""
from __future__ import annotations

import datetime as dt
import html
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from engine.config import PROJECT_ROOT  # noqa: E402
from engine.records import all_records  # noqa: E402

SITE = PROJECT_ROOT / "records" / "site"
E = html.escape
ICON = {"better": "✅", "worse": "❌", "same": "➖", "stopped": "⏹", "failed": "💥", "baseline": "📍"}
WINNER = dict(score=-0.4690, accuracy=0.805)


def when(ts):
    return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%b %d %H:%M UTC")


def pct(x):
    return f"{x:.1%}" if x is not None else "—"


def num(x):
    return f"{x:.4f}" if x is not None else "—"


def chart(rows):
    f = [r for r in rows if r["project"].startswith("FORCE") and r["hidden_accuracy"] is not None
         and not r["name"].startswith("ladder L") or r["name"].startswith("ladder L1")]
    f = [r for r in f if r["project"].startswith("FORCE") and r["hidden_accuracy"] is not None]
    if not f:
        return None
    plt.rcParams.update({"figure.facecolor": "#000", "axes.facecolor": "#0b0b0b", "text.color": "#fff",
                         "axes.labelcolor": "#fff", "xtick.color": "#ddd", "ytick.color": "#ddd", "font.size": 14})
    fig, ax = plt.subplots(figsize=(11, 4.5))
    xs = range(len(f))
    ax.plot(xs, [r["hidden_accuracy"] * 100 for r in f], "o-", color="#4fc3f7", lw=3, ms=10)
    for i, r in enumerate(f):
        ax.annotate(f"{r['name']}\n{r['hidden_accuracy']:.1%}", (i, r["hidden_accuracy"] * 100),
                    textcoords="offset points", xytext=(0, 12), ha="center", fontsize=11)
    ax.axhline(WINNER["accuracy"] * 100, color="#ffd54f", ls="--", lw=2.5)
    ax.text(len(f) - 1, WINNER["accuracy"] * 100 + 0.4, "competition winner 80.5%", ha="right", color="#ffd54f")
    ax.set_xticks([]); ax.set_ylabel("accuracy on locked wells (%)"); ax.set_ylim(65, 85)
    ax.set_title("FORCE 2020: every scored attempt, in order", color="#fff")
    SITE.mkdir(parents=True, exist_ok=True)
    fig.savefig(SITE / "progress.png", dpi=110, bbox_inches="tight"); plt.close(fig)
    return "progress.png"


def main():
    rows = all_records()
    projects = list(dict.fromkeys(r["project"] for r in rows))
    img = chart(rows)

    # ---- markdown for GitHub
    md = ["# V1 Record Book", "", "Every experiment, good or bad. Newest at the bottom of each section. "
          "\"Hidden\" = scored once on data the model never trained or tuned on.", "",
          "Legend: ✅ better than before · ❌ worse · ➖ no real change · ⏹ stopped · 📍 starting point", ""]
    for p in projects:
        md += [f"## {p}", "", "| | Experiment | What was tried | Open test | Hidden (honest) | Verified |",
               "|---|---|---|---|---|---|"]
        for r in [r for r in rows if r["project"] == p]:
            md.append(f"| {ICON.get(r['outcome'], '')} | {r['name']} | {r['tried'] or ''} | "
                      f"{num(r['open_score'])} / {pct(r['open_accuracy'])} | {num(r['hidden_score'])} / "
                      f"{pct(r['hidden_accuracy'])} | {'yes' if r['verified'] else ''} |")
        md.append("")
        for r in [r for r in rows if r["project"] == p and r["lesson"]]:
            md.append(f"- **{r['name']}** ({when(r['created_at'])}): {r['lesson']}")
        md.append("")
    (PROJECT_ROOT / "RECORD_BOOK.md").write_text("\n".join(md))

    # ---- web page (artifact format: no html/head/body wrapper)
    css = """
    :root{color-scheme:dark;--bg:#000;--card:#101418;--line:#2a3340;--fg:#f3f6f9;--mut:#b9c3cf;--ok:#3ee07f;--bad:#ff6b6b;--acc:#4fc3f7}
    body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
    main{max-width:980px;margin:0 auto;padding-block:18px 60px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
    h1{font-size:2.3rem;margin:.2em 0}h2{font-size:1.5rem;margin:1.8em 0 .5em}p{color:var(--mut)}
    img{max-width:100%;border-radius:12px;border:1px solid var(--line)}
    .e{background:var(--card);border:1px solid var(--line);border-left:6px solid var(--c,#666);border-radius:12px;padding:12px 16px;margin:10px 0}
    .better{--c:var(--ok)}.worse,.failed{--c:var(--bad)}.stopped{--c:#ffb74d}.baseline{--c:var(--acc)}.same{--c:#888}
    .top{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline}.top b{font-size:1.15rem}.when{color:var(--mut);font-size:.9rem}
    .nums{display:flex;flex-wrap:wrap;gap:8px;margin:8px 0}.n{background:#000;border:1px solid var(--line);border-radius:8px;padding:4px 10px;font-variant-numeric:tabular-nums}
    .n small{color:var(--mut);display:block;font-size:.75rem}.row{margin:4px 0}.row span{color:var(--mut)}
    .pc{display:flex;flex-wrap:wrap;gap:6px;margin-top:6px}.pc span{font-size:.85rem;border-radius:6px;padding:2px 8px;color:#000}
    """
    h = ["<title>V1 Record Book</title>", "<meta name='claude:viewport-fit-sides' content='cover'>", f"<style>{css}</style><main>",
         "<h1>V1 Record Book</h1>",
         f"<p>{len(rows)} experiments logged, good and bad. \"Hidden\" means scored once on data the model never trained "
         "or tuned on. That's the honest number.</p>"]
    if img:
        h.append(f"<img src='{img}' alt='FORCE 2020 accuracy over time'>")
    for p in projects:
        h.append(f"<h2>{E(p)}</h2>")
        for r in [r for r in rows if r["project"] == p]:
            h.append(f"<div class='e {E(r['outcome'] or '')}'><div class='top'><b>{ICON.get(r['outcome'], '')} {E(r['name'])}</b>"
                     f"<span class='when'>{when(r['created_at'])}</span></div>")
            for lab, key in (("Tried", "tried"), ("Why", "why"), ("Data", "data")):
                if r[key]:
                    h.append(f"<div class='row'><span>{lab}:</span> {E(r[key])}</div>")
            nums = []
            if r["open_score"] is not None or r["open_accuracy"] is not None:
                nums.append(("open test", f"{num(r['open_score'])} · {pct(r['open_accuracy'])}"))
            if r["hidden_score"] is not None or r["hidden_accuracy"] is not None:
                nums.append(("HIDDEN (honest)", f"{num(r['hidden_score'])} · {pct(r['hidden_accuracy'])}"))
            if r["minutes"]:
                nums.append(("time", f"{r['minutes']:.1f} min"))
            if nums:
                h.append("<div class='nums'>" + "".join(f"<div class='n'><small>{a}</small>{b}</div>" for a, b in nums) + "</div>")
            if r["verified"]:
                h.append(f"<div class='row'><span>Verified:</span> {E(r['verified'])}</div>")
            if r["per_class"]:
                chips = "".join(
                    f"<span style='background:hsl({int(120 * v)},70%,55%)'>{E(k)} {v:.0%}</span>"
                    for k, v in sorted(r["per_class"].items(), key=lambda kv: -kv[1]))
                h.append(f"<div class='row'><span>Right per rock type:</span></div><div class='pc'>{chips}</div>")
            if r["lesson"]:
                h.append(f"<div class='row'><span>Learned:</span> {E(r['lesson'])}</div>")
            h.append("</div>")
    h.append("</main>")
    SITE.mkdir(parents=True, exist_ok=True)
    (SITE / "record_book.html").write_text("\n".join(h))
    print(SITE / "record_book.html")


if __name__ == "__main__":
    main()
