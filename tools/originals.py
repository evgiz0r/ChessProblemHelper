"""Build docs/originals.html from knowledge/originals.json: every candidate original with its diagram,
FEN, verdict, gate result and notes.

    python tools/originals.py            # re-runs tools/blog.py check on each entry (about 2 s each)
"""
import html
import json
import subprocess
import sys
from pathlib import Path

import chess
import chess.svg

ROOT = Path(__file__).resolve().parent.parent
COLORS = {"square light": "#e9ece6", "square dark": "#93a78e", "margin": "#00000000", "coord": "#5b6b5a"}


def gate(fen):
    try:
        r = subprocess.run([sys.executable, str(ROOT / "tools/blog.py"), "check", fen + " w - - 0 1"],
                           capture_output=True, text=True, timeout=60, cwd=ROOT)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def counts(fen):
    board = fen.split()[0]
    w = sum(c.isupper() for c in board)
    b = sum(c.islower() for c in board)
    return w, b


def card(n, entry, rec, report):
    fen = entry.get("fen") or rec["fen"]
    w, b = counts(fen)
    svg = chess.svg.board(chess.Board(fen + " w - - 0 1"), size=300, coordinates=True, colors=COLORS)
    key = next((l[6:] for l in report.splitlines() if l.startswith("keys:")), "?")
    passed = "GATE: PASS" in report
    flags = [l for l in report.splitlines() if l.startswith(("FATAL", "warn", "plus"))]
    trim = '<span class="chip">trimmed</span>' if entry.get("fen") else ""
    return f"""
<article class="card" id="{rec['id']}">
  <figure class="diagram">{svg}
    <figcaption><b>No. {n}</b> · #2 · ({w}+{b})</figcaption>
  </figure>
  <div class="body">
    <header><h3>{html.escape(rec['id'])}</h3>
      <span class="chip {'ok' if passed else 'bad'}">{'gate pass' if passed else 'gate fail'}</span>{trim}</header>
    <p class="verdict">{html.escape(entry['verdict'])}</p>
    <p class="meta">Key {html.escape(key)} · {html.escape(rec['author'])}</p>
    <p class="fen"><code>{html.escape(fen)}</code></p>
    <details><summary>Solution and notes</summary><p>{html.escape(rec['note'])}</p></details>
    <details><summary>Gate report ({len(flags)} lines)</summary><ul>{''.join(f'<li>{html.escape(f)}</li>' for f in flags)}</ul></details>
  </div>
</article>"""


def main():
    data = json.loads((ROOT / "knowledge/originals.json").read_text())
    recs = {p["id"]: p for p in json.loads((ROOT / "knowledge/problems.json").read_text())["problems"]}
    sections, n = [], 0
    for tier, label in data["tiers"].items():
        entries = [e for e in data["originals"] if e["tier"] == tier]
        cards = []
        for e in entries:
            n += 1
            rec = recs[e["id"]]
            report = gate(e.get("fen") or rec["fen"])
            print(n, e["id"], "PASS" if "GATE: PASS" in report else "FAIL", flush=True)
            cards.append(card(n, e, rec, report))
        sections.append(f'<section id="tier-{tier}"><h2>{label} <span class="count">{len(entries)}</span></h2>'
                        f'<div class="grid">{"".join(cards)}</div></section>')
    nav = "".join(f'<a href="#tier-{t}">{l} ({sum(e["tier"] == t for e in data["originals"])})</a>'
                  for t, l in data["tiers"].items())
    page = (ROOT / "tools/originals_template.html").read_text()
    page = page.replace("{{NOTE}}", html.escape(data["note"])).replace("{{NAV}}", nav)
    page = page.replace("{{SECTIONS}}", "".join(sections)).replace("{{DATE}}", data["generated"])
    (ROOT / "docs/originals.html").write_text(page)
    print("wrote docs/originals.html,", n, "problems")


if __name__ == "__main__":
    main()
