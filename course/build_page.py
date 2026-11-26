"""Turns the course (study notes + source library + graded lessons) into one web page.

    python -m course.build_page     -> course/site/course.html

Pure Python: reads course/notes/*.md, course/sources/*.yaml, course/syllabus.yaml and the logbook.
"""
from __future__ import annotations

import html
import re

import markdown
import yaml

from engine.config import PROJECT_ROOT, database_path
from engine.db import Logbook

C = PROJECT_ROOT / "course"
OUT = C / "site" / "course.html"
TRACKS = [("shared", "Foundations", "Waves, signals and how machines learn from them"),
          ("leak", "Leak", "Reading fiber-optic (DAS) vibration to find leaks"),
          ("fluid", "Fluid", "Telling water, oil, gas and dry rock apart")]
E = html.escape

CSS = """
:root{color-scheme:dark;--bg:#07090c;--panel:#10141a;--line:#263040;--fg:#f2f5f8;--mut:#b7c2cf;
--leak:#ffd24a;--fluid:#5ec8ff;--shared:#7dffb2;--ok:#3ee07f;--bad:#ff6b6b}
body{margin:0;background:var(--bg);color:var(--fg);font:19px/1.6 Inter,-apple-system,Segoe UI,Roboto,sans-serif}
.wrap{max-width:860px;margin:0 auto;padding-block:20px 60px;
padding-left:max(16px,env(safe-area-inset-left,0px));padding-right:max(16px,env(safe-area-inset-right,0px))}
h1{font:800 2.6rem/1.1 'Space Grotesk',Inter,sans-serif;margin:.3em 0 .2em;text-wrap:balance}
h2{font:700 1.9rem/1.2 'Space Grotesk',Inter,sans-serif;margin:2.2em 0 .4em;text-wrap:balance}
.lede{color:var(--mut);font-size:1.15rem;max-width:60ch}
.stats{display:flex;flex-wrap:wrap;gap:10px;margin:18px 0}
.stat{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:10px 16px;min-width:0}
.stat b{display:block;font:800 1.9rem/1.1 'Space Grotesk',sans-serif;font-variant-numeric:tabular-nums}
.stat span{color:var(--mut);font-size:.95rem}
nav{position:sticky;top:env(safe-area-inset-top,0px);z-index:5;background:var(--bg);border-bottom:1px solid var(--line);
display:flex;gap:8px;flex-wrap:wrap;padding:10px 0}
body::before{content:"";position:fixed;inset:0 0 auto;height:env(safe-area-inset-top,0px);z-index:10;background:var(--bg)}
nav a{color:var(--fg);text-decoration:none;font-weight:700;padding:6px 14px;border-radius:999px;border:1px solid var(--line)}
nav a:focus-visible,summary:focus-visible{outline:3px solid var(--fluid);outline-offset:2px}
.track{border-left:6px solid var(--c);padding-left:14px}
.track>p{color:var(--mut)}
details{background:var(--panel);border:1px solid var(--line);border-radius:12px;margin:10px 0;padding:0 16px}
summary{cursor:pointer;padding:14px 0;font-weight:700;font-size:1.1rem;list-style:none;display:flex;gap:12px;align-items:baseline}
summary::-webkit-details-marker{display:none}
.n{font-variant-numeric:tabular-nums;color:var(--c);font-weight:800;min-width:2ch}
.note{border-top:1px solid var(--line);padding:4px 0 14px;min-width:0}
.note h1{font-size:1.5rem}.note h2{font-size:1.25rem;margin:1.2em 0 .3em}.note h3{font-size:1.1rem}
.note p,.note li{color:#dde4ec;max-width:68ch}
.note table{border-collapse:collapse;font-size:.95rem;display:block;overflow-x:auto;max-width:100%}
.note td,.note th{border:1px solid var(--line);padding:5px 8px;text-align:left}
.note code{background:#1a212b;padding:1px 5px;border-radius:5px;font-size:.92em}
.note a,.lib a{color:var(--fluid)}
.lessons{display:grid;gap:8px}
.lesson{display:flex;gap:10px;align-items:center;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:10px 14px}
.lesson div{min-width:0}.lesson small{color:var(--mut);display:block}
.pill{font-weight:800;font-size:.8rem;padding:3px 10px;border-radius:999px;color:#000;white-space:nowrap}
.passed{background:var(--ok)}.stuck{background:var(--bad)}.not_started,.in_progress{background:#9aa5b1}
.lib li{margin:.4em 0;color:var(--mut)}.lib li b{color:var(--fg)}
.kind{font-size:.8rem;border:1px solid var(--line);border-radius:6px;padding:0 6px;margin-left:6px;color:var(--mut)}
@media (max-width:520px){body{font-size:17px}h1{font-size:2rem}}
"""


def main():
    srcs = {}
    for p in sorted((C / "sources").glob("*.yaml")):
        for s in yaml.safe_load(open(p)) or []:
            srcs[s["id"]] = s
    syl = yaml.safe_load(open(C / "syllabus.yaml"))
    status = {r["lesson_id"]: r for r in Logbook(database_path()).course_status()}

    notes, words = {}, 0
    for t, _, _ in TRACKS:
        notes[t] = sorted((C / "notes" / t).glob("*.md"))
        words += sum(len(p.read_text().split()) for p in notes[t])

    def link_sources(text):
        # [source: some-id] and bare ids in the Sources list become links
        def rep(m):
            parts = [x.strip() for x in re.split(r"[;,]", m.group(1))]
            out = []
            for sid in parts:
                s = srcs.get(sid)
                out.append(f"[{sid}]({s['url']})" if s and s.get("url") else sid)
            return "[source: " + ", ".join(out) + "]"
        text = re.sub(r"\[source:\s*([^\]]+)\]", rep, text)
        lines = []
        in_src = False
        for line in text.splitlines():
            if line.startswith("## Sources"):
                in_src = True
            elif line.startswith("## "):
                in_src = False
            if in_src:
                for sid, s in srcs.items():
                    if re.search(rf"(?<![\w-]){re.escape(sid)}(?![\w-])", line) and s.get("url") and "](" not in line:
                        line = re.sub(rf"(?<![\w\[-]){re.escape(sid)}(?![\w-])", f"[{s.get('title', sid)}]({s['url']})", line, count=1)
            lines.append(line)
        return "\n".join(lines)

    h = ["<title>V1 Course</title>",
         "<meta name='claude:viewport-fit-sides' content='cover'>",
         "<link rel='stylesheet' href='https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700;800&family=Space+Grotesk:wght@700;800&display=swap'>",
         f"<style>{CSS}</style><div class='wrap'>",
         "<h1>The V1 Course</h1>",
         "<p class='lede'>Everything V1 studies, gathered from free courses, textbooks, papers and open datasets on the web, "
         "rewritten in plain English. Each topic ends with checkable facts, and each lesson is graded automatically.</p>",
         "<div class='stats'>"
         f"<div class='stat'><b>{sum(len(v) for v in notes.values())}</b><span>study notes</span></div>"
         f"<div class='stat'><b>{words:,}</b><span>words</span></div>"
         f"<div class='stat'><b>{len(srcs)}</b><span>free sources</span></div>"
         f"<div class='stat'><b>{sum(len(t['lessons']) for t in syl['tracks'])}</b><span>graded lessons</span></div></div>",
         "<nav>" + "".join(f"<a href='#{t}'>{name}</a>" for t, name, _ in TRACKS) + "<a href='#lessons'>Lessons</a><a href='#library'>Library</a></nav>"]

    for t, name, blurb in TRACKS:
        h.append(f"<section id='{t}' class='track' style='--c:var(--{t})'><h2>{name}</h2><p>{blurb}</p>")
        for i, p in enumerate(notes[t], 1):
            text = p.read_text()
            title = text.splitlines()[0].lstrip("# ").split("—", 1)[-1].split(" - ", 1)[-1].strip()
            body = markdown.markdown(link_sources(text), extensions=["tables"])
            h.append(f"<details><summary><span class='n'>{i:02d}</span>{E(title)}</summary><div class='note'>{body}</div></details>")
        h.append("</section>")

    h.append("<section id='lessons'><h2>Graded lessons</h2><p class='lede'>What V1 must pass, and how it did.</p><div class='lessons'>")
    for tr in syl["tracks"]:
        for l in tr["lessons"]:
            s = status.get(l["id"], {})
            st = s.get("status", "not_started")
            extra = f" · {s['attempts']} tries · final exam {s['exam_score']:.0%}" if s.get("exam_score") is not None else ""
            h.append(f"<div class='lesson'><span class='pill {st}'>{st.replace('_', ' ').upper()}</span><div><b>{E(l['title'])}</b>"
                     f"<small>{E(tr['title'])}{extra}</small><small>{E(l.get('teaches', ''))}</small></div></div>")
    h.append("</div></section>")

    h.append(f"<section id='library' class='lib'><h2>Library: {len(srcs)} free sources</h2>")
    for t, name, _ in TRACKS:
        items = [s for s in srcs.values() if s.get("topic") == t or (t == "shared" and s.get("topic") not in ("leak", "fluid"))]
        h.append(f"<details><summary>{name} ({len(items)})</summary><ul>")
        for s in sorted(items, key=lambda s: (s.get("kind", ""), s.get("title", ""))):
            h.append(f"<li><b><a href='{E(s.get('url', ''))}'>{E(s.get('title', s['id']))}</a></b>"
                     f"<span class='kind'>{E(s.get('kind', ''))}</span><br>{E(s.get('summary', ''))}</li>")
        h.append("</ul></details>")
    h.append("</section></div>")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(h))
    return OUT


if __name__ == "__main__":
    print(main())
