"""Outreach tracker page: progress toward the 500-email goal, sends per day and per group, and replies.

    python -m outreach.build_tracker   -> outreach/site/tracker.html (+ chart images)
"""
from __future__ import annotations

import html
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import pandas as pd  # noqa: E402

HERE = Path(__file__).resolve().parent
SITE = HERE / "site"
GOAL = 500
E = html.escape


def replies():
    rows = []
    for line in (HERE / "replies.md").read_text().splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) == 4 and not set(cells[0]) <= set("-") and cells[0] != "Date (UTC)":
            text = (cells[2] + " " + cells[3]).lower()
            kind = ("bounced" if "bounce" in text else "auto-reply" if "auto" in text
                    else "declined" if any(w in text for w in ("can't share", "cannot share", "not something", "closed"))
                    else "positive")
            rows.append(dict(date=cells[0], who=cells[1], reply=cells[2], next=cells[3], kind=kind))
    return rows


def main():
    sent = pd.read_csv(HERE / "sent_log.csv")
    sent = sent[sent.status == "sent"]
    rep = replies()
    n = len(sent)
    plt.rcParams.update({"figure.facecolor": "#000", "axes.facecolor": "#0b0b0b", "text.color": "#fff",
                         "axes.labelcolor": "#fff", "xtick.color": "#ddd", "ytick.color": "#ddd", "font.size": 14})
    SITE.mkdir(parents=True, exist_ok=True)

    fig, axes = plt.subplots(1, 3, figsize=(16, 4.6))
    a = axes[0]
    a.pie([n, max(GOAL - n, 0)], colors=["#4fc3f7", "#262626"], startangle=90, counterclock=False, wedgeprops=dict(width=0.3))
    a.text(0, 0.1, f"{n}", ha="center", fontsize=34, fontweight="bold"); a.text(0, -0.25, f"of {GOAL} sent", ha="center", fontsize=14)
    a.set_title("Goal")
    by_day = sent.groupby("date_utc").size().cumsum()
    axes[1].plot(range(len(by_day)), by_day.values, "o-", color="#4fc3f7", lw=3, ms=9)
    axes[1].axhline(GOAL, color="#ffd54f", ls="--"); axes[1].set_xticks(range(len(by_day)))
    axes[1].set_xticklabels([d[5:] for d in by_day.index], rotation=0); axes[1].set_ylim(0, GOAL * 1.05)
    axes[1].set_title("Total sent over time")
    g = sent.groupby("group").size().sort_values()
    axes[2].barh(g.index, g.values, color="#90a4ae"); axes[2].set_title("Sent by group")
    for i, v in enumerate(g.values):
        axes[2].text(v + 0.5, i, str(v), va="center")
    fig.tight_layout(); fig.savefig(SITE / "progress.png", dpi=110, bbox_inches="tight"); plt.close(fig)

    kinds = pd.Series([r["kind"] for r in rep]).value_counts() if rep else pd.Series(dtype=int)
    fig, ax = plt.subplots(figsize=(10, 3.2))
    order = ["positive", "declined", "auto-reply", "bounced"]
    cols = {"positive": "#00e676", "declined": "#ff8a65", "auto-reply": "#90a4ae", "bounced": "#ff5252"}
    vals = [int(kinds.get(k, 0)) for k in order] + [max(n - len(rep), 0)]
    labels = order + ["no reply yet"]
    left = 0
    for v, lab in zip(vals, labels):
        ax.barh([0], [v], left=left, color=cols.get(lab, "#333"))
        if v:
            ax.text(left + v / 2, 0, f"{lab}\n{v}", ha="center", va="center", fontsize=12, color="#000" if lab != "no reply yet" else "#fff")
        left += v
    ax.set_yticks([]); ax.set_xlim(0, max(n, 1)); ax.set_title("What came back")
    fig.tight_layout(); fig.savefig(SITE / "replies.png", dpi=110, bbox_inches="tight"); plt.close(fig)

    css = """:root{color-scheme:dark}body{margin:0;background:#000;color:#f3f6f9;font:18px/1.5 -apple-system,Segoe UI,Roboto,sans-serif}
    main{max-width:1000px;margin:0 auto;padding-block:16px 50px;padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
    h1{font-size:2.2rem;margin:.2em 0}h2{font-size:1.4rem;margin:1.6em 0 .4em}p{color:#b9c3cf}img{max-width:100%;border-radius:12px;border:1px solid #2a3340}
    .t{overflow-x:auto}table{border-collapse:collapse;width:100%;font-size:.95rem}td,th{border-bottom:1px solid #2a3340;padding:6px;text-align:left;vertical-align:top}
    .k{font-weight:800;border-radius:6px;padding:1px 8px;color:#000}.positive{background:#00e676}.declined{background:#ff8a65}.auto-reply{background:#90a4ae}.bounced{background:#ff5252}"""
    h = ["<title>V1 Outreach Tracker</title>", "<meta name='claude:viewport-fit-sides' content='cover'>", f"<style>{css}</style><main>",
         "<h1>Outreach tracker</h1>",
         f"<p>{n} of {GOAL} emails sent from tobiasmaxlee48@gmail.com, about 35 a day. Each one is personal and "
         "mentions the person's own work; anyone who asks not to be contacted is never emailed again.</p>",
         "<img src='progress.png' alt='Progress toward 500'>", "<h2>Replies</h2>", "<img src='replies.png' alt='Replies'>",
         "<div class='t'><table><tr><th>When</th><th>Who</th><th>Reply</th><th>Next</th></tr>"]
    for r in rep:
        h.append(f"<tr><td>{E(r['date'])}</td><td>{E(r['who'])}</td><td><span class='k {r['kind']}'>{r['kind']}</span> "
                 f"{E(r['reply'])}</td><td>{E(r['next'])}</td></tr>")
    h.append("</table></div><h2>Everyone emailed</h2><div class='t'><table><tr><th>Date</th><th>Group</th><th>Organization</th><th>Name</th></tr>")
    for _, r in sent.sort_values(["date_utc", "group"], ascending=[False, True]).iterrows():
        h.append(f"<tr><td>{E(str(r.date_utc))}</td><td>{E(str(r.group))}</td><td>{E(str(r.organization))}</td>"
                 f"<td>{E(str(r['name']) if pd.notna(r['name']) else '')}</td></tr>")
    h.append("</table></div></main>")
    (SITE / "tracker.html").write_text("\n".join(h))
    print(SITE / "tracker.html", n, "sent")


if __name__ == "__main__":
    main()
