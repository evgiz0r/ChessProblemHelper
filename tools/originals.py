"""Build docs/originals.html from knowledge/originals.json: every candidate original with its diagram,
FEN, verdict, gate result and notes.

    python tools/originals.py            # re-runs tools/blog.py check on each entry (about 2 s each)
"""
import html
import json
import re
import subprocess
import sys
from pathlib import Path

import chess
import chess.svg

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
COLORS = {"square light": "#e9ece6", "square dark": "#93a78e", "margin": "#00000000", "coord": "#5b6b5a"}


def gate(fen):
    try:
        r = subprocess.run([sys.executable, str(ROOT / "tools/blog.py"), "check", fen + " w - - 0 1"],
                           capture_output=True, text=True, timeout=60, cwd=ROOT)
        return (r.stdout + r.stderr).strip()
    except subprocess.TimeoutExpired:
        return "TIMEOUT"


def _play(ph, only=None):
    """'1...A/B 2.X#, 1...C 2.Y#' for the variations worth printing: not a threat repeat (king moves kept),
    and, when `only` is given, a defence in it."""
    groups = {}
    for v in ph["variations"]:
        if v["refutes"] or not v["continuations"]:
            continue
        d = v["defence"]["san"]
        if v["threat_repeat"] and not d.startswith("K"):
            continue
        if only is not None and d.rstrip("+#") not in only:
            continue
        groups.setdefault("/".join(c["san"] for c in v["continuations"]), []).append(d)
    def name(ds):   # a random move of one piece: 1...S~
        return f"{ds[0][0]}~" if len(ds) >= 4 and ds[0][0] in "QRBSK" and all(d[0] == ds[0][0] for d in ds) else "/".join(ds)
    return ", ".join(f"1...{name(ds)} 2.{m}" for m, ds in groups.items())


def _mates(ph):
    return {v["defence"]["san"].rstrip("+#"): set(c["san"] for c in v["continuations"]) for v in ph["variations"]
            if not v["refutes"] and v["continuations"] and not v["threat_repeat"]}


def _head(ph):
    mark = "!" if ph["type"] == "key" else "?"
    head = f"1.{ph['first_move']['san']}{mark}"
    if ph.get("threat"):
        return head + f" (2.{'/'.join(c['san'] for c in ph['threat'])})"
    return head + (" (zugzwang)" if ph.get("zugzwang") else "")


def solution(fen, note, extra_tries=()):
    """Album-style solution: set play only for defences that recur after a first move, only the tries the
    composer's note names (1.X?), the key with its threat and grouped variations."""
    from chesscomp.analysis import analyse
    from chesscomp.core import Problem
    res = analyse(Problem.from_fen(fen + " w - - 0 1", "#2"), max_refutations=1, include_tries=True,
                  include_set=True, time_limit=60)
    phases = res.get("phases", [])
    def named(p):
        san = p["first_move"]["san"].rstrip("+#")
        return san in extra_tries or re.search(r"(?<![A-Za-z0-9])" + re.escape(san) + r"\?", note)
    tries = [p for p in phases if p["type"] == "try" and named(p)]
    keys = [p for p in phases if p["type"] == "key"]
    shown = {v["defence"]["san"].rstrip("+#") for p in tries + keys for v in p["variations"]
             if not v["refutes"] and v["continuations"] and (not v["threat_repeat"] or v["defence"]["san"].startswith("K"))}
    lines = []
    setp = next((p for p in phases if p["type"] == "set"), None)
    if setp:
        s = _play(setp, None if keys and keys[0].get("zugzwang") else shown)
        if s:
            lines.append(("Set", s))
    for t in tries:
        play = _play(t)
        refs = ", ".join(f"1...{r['san']}!" for r in t["refutations"])
        lines.append(("Try", f"{_head(t)} {play + ', ' if play else ''}but {refs}"))
    for k in keys:
        lines.append(("Key", f"{_head(k)} {_play(k)}".strip()))
    # E. Bourd, 18 Oct 2026: a single phase without tries or changes does not pass unless very complicated or pretty
    km = _mates(keys[0]) if keys else {}
    changed = {d for p in ([setp] if setp else []) + tries for d, m in _mates(p).items() if d in km and m != km[d]}
    return lines, {"tries": len(tries), "changes": len(changed)}


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
    lines, content = solution(fen, rec['note'] + ' ' + ' '.join(rec['themes']), entry.get('tries', ()))
    phases = f'<span class="chip">{content["tries"]} tries · {content["changes"]} changed</span>'
    return f"""
<article class="card" id="{rec['id']}">
  <figure class="diagram">{svg}
    <figcaption><b>No. {n}</b> · #2 · ({w}+{b})</figcaption>
  </figure>
  <div class="body">
    <header><h3>{html.escape(rec['id'])}</h3>
      <span class="chip {'ok' if passed else 'bad'}">{'gate pass' if passed else 'gate fail'}</span>{trim}{phases}</header>
    <p class="verdict">{html.escape(entry['verdict'])}</p>
    <p class="meta">Key {html.escape(key)} · {html.escape(rec['author'])}</p>
    <p class="fen"><code>{html.escape(fen)}</code></p>
    <dl class="solution">{''.join(f'<dt>{k}</dt><dd>{html.escape(v)}</dd>' for k, v in lines)}</dl>
    <details><summary>Explanation</summary><p>{html.escape(rec['note'])}</p></details>
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
