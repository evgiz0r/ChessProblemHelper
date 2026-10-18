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


def _moves(mvs):
    """['1.Bd3?', '1.Bg2?'] -> '1.Bd3?/Bg2?'"""
    return "/".join(m if i == 0 else m[2:] for i, m in enumerate(mvs))


def _head(ph):
    mark = "!" if ph["type"] == "key" else "?"
    head = f"1.{ph['first_move']['san']}{mark}"
    if ph.get("threat"):
        return head + f" (2.{'/'.join(c['san'] for c in ph['threat'])})"
    return head + (" (zugzwang)" if ph.get("zugzwang") else "")


def solution(fen, note, extra_tries=(), thematic=None, skip_tries=()):
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
    named_tries = [p for p in phases if p["type"] == "try" and named(p) and _strip(p["first_move"]["san"]) not in skip_tries]
    tries = [p for p in named_tries if "x" not in p["first_move"]["san"]]   # no capturing try shown (E. Bourd)
    order = list(extra_tries)                            # tries listed by hand come first, in their order
    tries.sort(key=lambda p: order.index(_strip(p["first_move"]["san"])) if _strip(p["first_move"]["san"]) in order else len(order))
    key = next((p for p in phases if p["type"] == "key"), None)
    setp = next((p for p in phases if p["type"] == "set"), None)
    km = _mates(key) if key else {}
    others = [(f"set", _mates(setp))] if setp else []
    others += [(f"1.{t['first_move']['san']}?", _mates(t)) for t in tries]
    refuters = {_strip(r["san"]) for t in named_tries for r in t["refutations"]}   # capture tries still say what is thematic
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
    # main solution: thematic play only; repeated or random tries and the key's other variations go to the by-play
    lines, extra_tries_bp, seen = [], [], {}
    if setp:
        sm = _mates(setp)
        if any(d in sm and d in km and not overlap(sm[d][1], km[d][1]) for d in them):
            lines.append(("Set", _vars(sm, them, randoms=randoms, letters=letters)))
    n_thematic = 0
    for t in tries:
        tm = _mates(t)
        changed = [d for d in them if d in tm and (d not in km or not overlap(tm[d][1], km[d][1]))]
        refs = [r["san"] for r in t["refutations"]]
        ref_text = ", ".join(f"1...{r}!" + (f" [{letters[_strip(r)]}]" if _strip(r) in letters else "") for r in refs)
        if not changed and not any(_strip(r) in letters for r in refs):
            extra_tries_bp.append((f"1.{t['first_move']['san']}?", ", ".join(f"{r}!" for r in refs)))
            continue
        play = _vars(tm, changed, randoms=randoms, letters=letters)
        sig = (tuple(c["san"] for c in t.get("threat") or []), play, ref_text)
        if sig in seen:                                  # the same try again: by-play
            seen[sig].append(f"1.{t['first_move']['san']}?")
            continue
        seen[sig] = []
        n_thematic += 1
        lines.append(("Try", f"{html.escape(_head(t))} {play + ', ' if play else ''}but {html.escape(ref_text)}"))
        lines[-1] = lines[-1] + (sig,)
    if key:
        lines.append(("Key", f"{html.escape(_head(key))} {_vars(km, them, randoms=randoms, letters=letters)}"))
    # by-play: repeated tries (as the try they repeat), other tries, the key's other variations
    bp = []
    for line in lines:
        if line[0] == "Try" and seen.get(line[2]):
            first = re.match(r"1\.(\S+)", re.sub("<[^>]+>", "", line[1])).group(1)
            bp.append(f"{_moves(seen[line[2]])} as 1.{first}")
    lines = [l[:2] for l in lines]
    groups = {}
    for mv, ref in extra_tries_bp:
        groups.setdefault(ref, []).append(mv)
    bp += [f"{_moves(mvs)} {ref}" for ref, mvs in groups.items()]
    others_key = _vars(km, [d for d in km if d not in them], merge=True)
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
    byplay = "; ".join(html.escape(x) for x in bp)
    if others_key:
        byplay += ("; " if byplay else "") + others_key
    if byplay:
        lines.append(("By-play", byplay))
    # E. Bourd, 18 Oct 2026: a single phase without tries or changes does not pass unless very complicated or pretty
    return lines, {"tries": n_thematic, "changes": len(changes)}


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
    lines, content = solution(fen, rec['note'] + ' ' + ' '.join(rec['themes']), entry.get('tries', ()), entry.get('thematic'), entry.get('skip_tries', ()))
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
    <dl class="solution">{''.join((f'<dt class="bp">{k}</dt><dd class="bp">{v}</dd>' if k == 'By-play' else f'<dt>{k}</dt><dd>{v}</dd>') for k, v in lines)}</dl>
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
