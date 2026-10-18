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


def _strip(san):
    return san.rstrip("+#")


def _mates(ph):
    """defence -> mate(s) for every defence answered by a mate other than the threat (king moves kept)."""
    out = {}
    for v in ph["variations"]:
        d = v["defence"]["san"]
        if v["refutes"] or not v["continuations"] or (v["threat_repeat"] and not d.startswith("K")):
            continue
        out[_strip(d)] = (d, "/".join(c["san"] for c in v["continuations"]), v["defence"]["uci"][:2])
    return out


def _vars(m, order, merge=False, randoms=(), letters=None):
    """'1...A 2.X#, 1...B/C 2.Y#' (HTML) in the given order; neighbours with one mate share it (any two with one mate
    when `merge`, for the by-play); 1...S~ for a random move. With `letters` the play is thematic: each group is
    marked [a], [b] ... and set in bold."""
    groups = []
    for d in order:
        if d not in m:
            continue
        san, mate, _ = m[d]
        tag = letters.get(d) if letters else None
        if merge:
            same = [g for g in groups if g[1] == mate]
        else:
            same = groups[-1:] if groups and groups[-1][1] == mate and groups[-1][2] == tag else []
        if same:
            same[0][0].append(san)
        else:
            groups.append(([san], mate, tag))
    def name(ds):   # 1...S~ (the by-play names the square: 1...Sb4~)
        keys = [_strip(x) for x in ds]
        named = len(ds) >= 2 and all(k in randoms for k in keys)
        if named or (len(ds) >= 4 and ds[0][0] in "QRBSK" and all(x[0] == ds[0][0] for x in ds)):
            return f"{ds[0][0]}{m[keys[0]][2] if merge else ''}~"
        return "/".join(ds)
    def one(ds, mate, tag):
        text = html.escape(f"1...{name(ds)} " + (f"[{tag}] " if tag else "") + f"2.{mate}")
        return f"<b>{text}</b>" if letters else text
    return ", ".join(one(*g) for g in groups)


def _head(ph):
    mark = "!" if ph["type"] == "key" else "?"
    head = f"1.{ph['first_move']['san']}{mark}"
    if ph.get("threat"):
        return head + f" (2.{'/'.join(c['san'] for c in ph['threat'])})"
    return head + (" (zugzwang)" if ph.get("zugzwang") else "")


def solution(fen, note, extra_tries=(), thematic=None):
    """A publication solution (HTML): set play, the tries the composer names (1.X? in the notes, or `extra_tries`), the key;
    the thematic defences in one order in every phase, by-play in brackets after the key's thematic play, and a
    last line saying which mates change and which transfer. Thematic = key defences that also have a mate in the
    set play or a try, or that refute a try (or the `thematic` list); with none, all of the key's play."""
    from chesscomp.analysis import analyse
    from chesscomp.core import Problem
    res = analyse(Problem.from_fen(fen + " w - - 0 1", "#2"), max_refutations=1, include_tries=True,
                  include_set=True, time_limit=60)
    phases = res.get("phases", [])
    def named(p):
        san = _strip(p["first_move"]["san"])
        return san in extra_tries or re.search(r"(?<![A-Za-z0-9])" + re.escape(san) + r"\?", note)
    tries = [p for p in phases if p["type"] == "try" and named(p) and "x" not in p["first_move"]["san"]]
    key = next((p for p in phases if p["type"] == "key"), None)
    setp = next((p for p in phases if p["type"] == "set"), None)
    km = _mates(key) if key else {}
    others = [(f"set", _mates(setp))] if setp else []
    others += [(f"1.{t['first_move']['san']}?", _mates(t)) for t in tries]
    refuters = {_strip(r["san"]) for t in tries for r in t["refutations"]}
    def overlap(a, b):   # one mate shared (a dual counts as the same mate)
        return bool(set(a.split("/")) & set(b.split("/")))
    changing = {d for d in km for _, m in others if d in m and not overlap(m[d][1], km[d][1])}
    if thematic:   # the composer's order; 'Sf5~' = every move of the f5 unit not named on its own
        allm = [km] + [m for _, m in others]
        them, randoms = [], set()
        for d in thematic:
            if d.endswith("~"):
                sq = d[1:-1]
                for m in allm:
                    new = [x for x, v in m.items() if v[2] == sq and x not in thematic and x not in them]
                    them += new
                    randoms.update(new)
            else:
                them.append(d)
    else:
        randoms = set()
        them = [d for d in km if not d.startswith("K") and (d in refuters or d in changing)]
        if not them:
            them = [d for d in km if not d.startswith("K")] or list(km)
    # one letter per thematic variation: a random group shares one, and so do defences with one mate in every phase
    phases_m = [km] + [m for _, m in others]
    def twin_of(d):
        return next((x for x in them if x != d and x.replace("x", "") == d.replace("x", "")), None)
    letters, prev = {}, None
    for d in them:
        if d in randoms and any(x in letters for x in randoms):
            letters[d] = letters[next(x for x in randoms if x in letters)]
        elif twin_of(d) in letters:
            letters[d] = letters[twin_of(d)]
        elif prev and prev not in randoms and d not in randoms and all(
                (prev in m) == (d in m) and (prev not in m or m[prev][1] == m[d][1]) for m in phases_m):
            letters[d] = letters[prev]
        else:
            letters[d] = "abcdefghijklmnopqrstuvwxyz"[len(set(letters.values()))]
        prev = d
    lines = []
    if setp:
        s = _vars(_mates(setp), them, randoms=randoms, letters=letters)
        if s:
            lines.append(("Set", s))
    for t in tries:
        play = _vars(_mates(t), them, randoms=randoms, letters=letters)
        refs = ", ".join(f"1...{r['san']}!" + (f" [{letters[_strip(r['san'])]}]" if _strip(r["san"]) in letters else "")
                         for r in t["refutations"])
        lines.append(("Try", f"{html.escape(_head(t))} {play + ', ' if play else ''}but {html.escape(refs)}"))
    if key:
        byplay = _vars(km, [d for d in km if d not in them], merge=True)
        play = _vars(km, them, randoms=randoms, letters=letters)
        lines.append(("Key", f"{html.escape(_head(key))} {play}" + (f" ({byplay})" if byplay else "")))
    # which mates change, which transfer (thematic defences only; the key's mate last)
    changes, transfers = [], []
    for d in them:
        if d not in km:
            continue
        seq = []                                         # [(labels, mate)] of the phases where the mate differs
        for lab, m in others:
            twin = next((x for x in m if x != d and x.replace("x", "") == d.replace("x", "")), None)
            if d not in m and twin in them:              # 1...Rxe6 in a try, 1...Re6 after the key
                m = {**m, d: m[twin]}
            if d in m and not overlap(m[d][1], km[d][1]):
                if seq and seq[-1][1] == m[d][1]:
                    seq[-1][0].append(lab)
                else:
                    seq.append(([lab], m[d][1]))
        if seq:
            text = " → ".join(f"2.{mt} ({', '.join(labs)})" for labs, mt in seq) + f" → 2.{km[d][1]}"
            same = [c for c in changes if c[1] == text]
            if same:
                same[0][0].append(km[d][0])
            else:
                changes.append(([km[d][0]], text))
        for lab, m in others:                            # the key's mate after d stood after another defence d2
            for d2 in them:
                if (d2 != d and d2 in m and overlap(m[d2][1], km[d][1]) and not (d in m and overlap(m[d][1], km[d][1]))
                        and not (d2 in km and overlap(km[d2][1], km[d][1]))):
                    entry = f"2.{km[d][1]}: 1...{m[d2][0]} ({lab}) → 1...{km[d][0]}"
                    if entry not in transfers:
                        transfers.append(entry)
    if changes:
        lines.append(("Changed", html.escape("; ".join(f"1...{'/'.join(ds)} [{letters[_strip(ds[0])]}] {text}"
                                                       for ds, text in changes))))
    if transfers:
        lines.append(("Transferred", html.escape("; ".join(transfers))))
    # E. Bourd, 18 Oct 2026: a single phase without tries or changes does not pass unless very complicated or pretty
    return lines, {"tries": len(tries), "changes": len(changes)}


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
    lines, content = solution(fen, rec['note'] + ' ' + ' '.join(rec['themes']), entry.get('tries', ()), entry.get('thematic'))
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
    <dl class="solution">{''.join(f'<dt>{k}</dt><dd>{v}</dd>' for k, v in lines)}</dl>
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
