"""Thematic table: only the play that carries the theme, phase against phase.

E. Bourd, session 29: "the solution is so cluttered it's hard to figure actually if the thematic play is there".
The full report lists every Black move of every phase. This prints one row per thematic defence and one column
per phase (set play, the tries that change the thematic play, the key), and folds everything else into a short
summary. A defence is thematic when its mate differs between two phases, or when it is a random move or a
correction of a correcting piece (the solver's S~ groups).

    python -m chesscomp.thematic "2Q1N3/8/3PPpP1/1B1knn1R/8/K3p3/4N1PB/8"
    python -m chesscomp.thematic FEN --defs Sxd6,Sd4      (choose the rows yourself)
"""
from __future__ import annotations
import argparse
from .core import Problem
from .analysis import analyse


def _cells(ph):
    """defence SAN -> cell text for one phase."""
    out = {}
    for v in ph['variations']:
        san = v['defence']['san']
        if v.get('threat_repeat'):
            out[san] = '(threat)'
        elif v['continuations']:
            ms = [c['san'] for c in v['continuations']]
            out[san] = '/'.join(ms) + (' DUAL' if len(ms) > 1 else '')
        else:
            out[san] = '-'
    return out


def table(fen: str, defs: list[str] | None = None, max_tries: int = 3):
    p = Problem.from_fen(fen if ' ' in fen else fen + ' w - - 0 1', '#2')
    res = analyse(p, max_refutations=1, include_tries=True, include_set=True)
    return res, build(res, defs, max_tries)


def build(res, defs=None, max_tries: int = 3):
    """The table from an existing analysis (None when there is no unique key)."""
    if res.get('cooked'):
        return None
    phases = res['phases']
    key = next((ph for ph in phases if ph['type'] == 'key'), None)
    setp = next((ph for ph in phases if ph['type'] == 'set'), None)
    if key is None:
        return None
    cells = {id(ph): _cells(ph) for ph in phases if ph['type'] in ('set', 'try', 'key')}
    # correction groups (from the key, else the set play)
    groups = []
    for c in (key.get('corrections') or (setp or {}).get('corrections') or []):
        groups.append((c['piece'], c['random']['moves'], [x['move'] for x in c['corrections']]))
    grouped = {m for _, rnd, cor in groups for m in rnd + cor}
    # thematic defences: chosen, or changed between set and key, or in a correction group
    real = lambda c: c is not None and c not in ('-', '(threat)', '?') and 'DUAL' not in c
    cand = ([setp] if setp else []) + [ph for ph in phases if ph['type'] == 'try' and len(ph.get('refutations') or []) == 1]
    if defs:
        rows = list(defs)
    else:
        rows = []
        for san, cell in cells[id(key)].items():
            if san in grouped or not real(cell):
                continue
            if any(real(cells[id(ph)].get(san)) and cells[id(ph)].get(san) != cell for ph in cand):
                rows.append(san)
    # tries worth a column: refuted once and changing at least one thematic cell against the key
    cols = []
    if setp:
        cols.append(('set', setp))
    def thematic_sans():
        out = list(rows)
        for _, rnd, cor in groups:
            out += cor + rnd[:1]
        return out
    ts = thematic_sans()
    def single(c):
        return c is not None and c not in ('-', '(threat)', '?') and 'DUAL' not in c
    def worth(t):
        tc, kc = cells[id(t)], cells[id(key)]
        if any(tc.get(s) is None for s in ts):
            return False                      # the try does not even meet a thematic defence
        diff_key = any(single(tc.get(s)) and tc.get(s) != kc.get(s) for s in ts)
        same_as_set = setp is not None and all(not single(tc.get(s)) or tc.get(s) == cells[id(setp)].get(s) for s in ts)
        return diff_key and not same_as_set
    tries = [ph for ph in phases if ph['type'] == 'try' and len(ph.get('refutations') or []) == 1]
    tries = [t for t in tries if worth(t)]
    for t in tries[:max_tries]:
        cols.append((f"1.{t['first_move']['san']}? {t['refutations'][0]['san']}!", t))
    cols.append((f"1.{key['first_move']['san']}!", key))
    return {'groups': groups, 'rows': rows, 'cols': cols, 'cells': cells, 'key': key,
                 'hidden_tries': [ph for ph in phases if ph['type'] == 'try' and ph not in [c[1] for c in cols]]}


def format_table(res, t) -> str:
    if t is None:
        return f"#2 {res['fen']}: no unique key, no thematic table"
    cols, cells, key = t['cols'], t['cells'], t['key']
    lines = []
    head = ['']
    for name, ph in cols:
        thr = ph.get('threat') or []
        tag = ' (zz)' if ph['type'] != 'set' and not thr else (f" ({'/'.join(x['san'] for x in thr)})" if thr else '')
        head.append(name + tag)
    grid = [head]
    shown = set()
    def row(label, san):
        vals = [cells[id(ph)].get(san, '?') for _, ph in cols]
        changed = len({v for v in vals if v not in ('-', '?', '(threat)')}) > 1
        grid.append([label + ('  *' if changed else '')] + vals)
        shown.add(san)
    for piece, rnd, cor in t['groups']:
        row(f"{piece[0]}~ ({len(rnd)}: {'/'.join(rnd)})", rnd[0])
        shown.update(rnd)
        for m in cor:
            row(f"  {m}", m)
    merged = {}
    for san in t['rows']:
        if san in shown:
            continue
        vec = tuple(cells[id(ph)].get(san, '?') for _, ph in cols)
        merged.setdefault(vec, []).append(san)
    for vec, sans in merged.items():
        row('/'.join(sans), sans[0]); shown.update(sans)
    w = [max(len(r[i]) for r in grid) for i in range(len(head))]
    for r in grid:
        lines.append('  '.join(x.ljust(w[i]) for i, x in enumerate(r)).rstrip())
    lines.append('(* = mate changes between phases; DUAL = more than one mate; - = no mate)')
    # the rest, folded
    kc = cells[id(key)]
    rest = [s for s in kc if s not in shown]
    duals = [s for s in rest if 'DUAL' in kc[s]]
    holes = [s for s in rest if kc[s] == '-']
    kings = [s for s in rest if s.startswith('K')]
    summ = f"Other Black play after the key: {len(rest)} moves"
    if duals: summ += f"; duals after {', '.join(duals)}"
    if holes: summ += f"; NO MATE after {', '.join(holes)}"
    if kings: summ += f"; king moves {', '.join(kings)} ({', '.join(kc[k].strip('()') for k in kings)})"
    lines.append(summ)
    hid = t['hidden_tries']
    if hid:
        from collections import Counter
        refs = Counter(r['san'] for ph in hid for r in (ph.get('refutations') or [])[:1])
        lines.append(f"Other tries: {len(hid)}; refuted by " + ', '.join(f"{k} ({v})" for k, v in refs.most_common(4)))
    return '\n'.join(lines)


def format_album(res, t) -> str:
    """FIDE Album style, as E. Bourd asked (session 30):
    Set: 1...S~ 2.Qc4#, 1...Sxd6! [a] 2.Sxf6#, 1...Sd4! [b] 2.Sc3#
    Solution: 1.Qc2! zz, 1...S~ 2.Qc4#, 1...Sxd6! [a] 2.Sc7#, 1...Sd4! [b] 2.Sf4#
    Corrections carry '!', thematic defences a letter; other play follows on its own line."""
    if t is None:
        return ''
    cols, cells, key = t['cols'], t['cells'], t['key']
    items, corr = [], set()
    for _, rnd, cor in t['groups']:
        items.append(('S~' if True else '', rnd[0], None)); corr.update(cor)
        for m in cor:
            items.append((m, m, None))
    merged = {}
    for san in t['rows']:
        if san not in [i[1] for i in items]:
            vec = tuple(cells[id(ph)].get(san) for _, ph in cols)
            merged.setdefault(vec, []).append(san)
    for sans in merged.values():          # c1=Q/c1=R with the same mates in every phase: one defence
        items.append(('/'.join(sans), sans[0], None))
    letters, n = {}, 0
    for label, san, _ in items:
        if not label.endswith('~'):
            letters[san] = 'abcdefghij'[n]; n += 1
    def cell(ph, san):
        c = cells[id(ph)].get(san)
        if c is None: return None
        if c == '-': return 'no mate'
        if c == '(threat)': return '2.threat'
        if c.endswith(' DUAL'): return '2.' + c[:-5] + ' (dual)'
        return '2.' + c
    def line(ph):
        out = []
        for label, san, _ in items:
            c = cell(ph, san)
            if c is None: continue
            if label.endswith('~'):
                piece = next(g[0] for g in t['groups'] if g[1][0] == san)
                out.append(f"1...{piece[0]}~ {c}")
            else:
                out.append(f"1...{label}{'!' if san in corr else ''} [{letters[san]}] {c}")
        return ', '.join(out)
    lines = []
    for name, ph in cols:
        thr = ph.get('threat') or []
        head = '' if ph['type'] == 'set' else (f"(2.{'/2.'.join(x['san'] for x in thr)})" if thr else 'zz')
        if ph['type'] == 'set':
            lines.append('Set: ' + line(ph))
        elif ph['type'] == 'try':
            lines.append(f"Try: 1.{ph['first_move']['san']}? {head}, {line(ph)}, but 1...{ph['refutations'][0]['san']}!")
        else:
            lines.append(f"Solution: 1.{ph['first_move']['san']}! {head}, {line(ph)}")
    shown = {m for i in items for m in i[0].split('/')} | {i[1] for i in items} | {m for g in t['groups'] for m in g[1]}
    kc = cells[id(key)]
    by, duals = {}, []
    for san, c in kc.items():
        if san in shown or c in ('(threat)',):
            continue
        if c.endswith(' DUAL'): duals.append(f"1...{san} 2.{c[:-5]}")
        elif c == '-': duals.append(f"1...{san} NO MATE")
        else: by.setdefault(c, []).append(san)
    if by:
        lines.append('Also: ' + ', '.join(f"1...{'/'.join(v)} 2.{k}" for k, v in by.items()))
    if duals:
        lines.append('Duals: ' + ', '.join(duals))
    return '\n'.join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('fen'); ap.add_argument('--defs'); ap.add_argument('--tries', type=int, default=3)
    a = ap.parse_args(argv)
    res, t = table(a.fen, a.defs.split(',') if a.defs else None, a.tries)
    print(f"#2 {res['count']}  {res['fen']}")
    print(format_album(res, t)); print(); print(format_table(res, t))


if __name__ == '__main__':
    main()
