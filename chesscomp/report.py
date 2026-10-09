"""Human-readable (album style) rendering of an analysis dict, plus a small CLI."""
from __future__ import annotations
import argparse, json, sys
from .core import Problem, promoted_force
import chess
from .analysis import analyse


def _conts(cs):
    return '/'.join(c['san'] for c in cs)


def format_phase(ph, show_threat_repeats=False):
    lines = []
    if ph['type'] == 'set':
        head = 'Set play:'
    else:
        mark = '!' if ph['type'] == 'key' else '?'
        head = f"{'Key' if ph['type']=='key' else 'Try'}: 1.{ph['first_move']['san']}{mark}"
        if ph.get('threat'):
            head += f" (threat: 2.{_conts(ph['threat'])})"
        elif ph.get('check_key'):
            head += ' (check)'
        elif ph.get('stalemate'):
            head += ' (stalemate)'
        elif ph.get('zugzwang'):
            head += ' (zugzwang)'
    lines.append(head)
    hidden = 0
    groups = {}
    for v in ph['variations']:
        if v['refutes']:
            continue
        if v['threat_repeat'] and not show_threat_repeats:
            hidden += 1
            continue
        key = (v['defence']['uci'][:2], tuple(c['san'] for c in v['continuations']), v['goal_by_defence'])
        groups.setdefault(key, []).append(v)
    for (frm, conts, goal), vs in groups.items():
        d = '/'.join(v['defence']['san'] for v in vs)
        if goal:
            lines.append(f"   1...{d}"); continue
        dual = '  [dual]' if len(conts) > 1 else ''
        lines.append(f"   1...{d} 2.{'/'.join(conts)}{dual}")
    if hidden:
        lines.append(f'   ({hidden} further moves allow the threat)')
    for c in ph.get('corrections', []):
        r = c['random']
        dual = f" (dual after {'/'.join(r['duals'])})" if r['duals'] else ''
        cors = ', '.join(f"{x['move']} 2.{'/'.join(x['mates'])}" for x in c['corrections'])
        lines.append(f"   {c['piece'][0]}~ random {'/'.join(r['moves'])} 2.{r['mate']}{dual}; corrections {cors}")
    if ph['type'] == 'try':
        lines.append('   but stalemate!' if ph.get('stalemate') else '   but ' + ', '.join(f"1...{r['san']}!" for r in ph['refutations']))
    if ph['type'] == 'set' and ph.get('unprovided'):
        lines.append('   unprovided: ' + ', '.join(ph['unprovided']))
    return '\n'.join(lines)


def format_report(res):
    out = [f"{res['stipulation']} {res['count']}   FEN {res['fen']}"]
    try:
        for line in promoted_force(chess.Board(res['fen'])):
            out.append(f"PROMOTED FORCE: {line}  (fatal)")
    except Exception:
        pass
    if res.get('timeout'):
        out.append('** time limit reached - analysis incomplete **')
    if res['kind'] == 'help':
        out.append(f"{res['n_solutions']} solution(s):")
        out += ['   ' + s['line'] for s in res['solutions']]
    else:
        for ph in res.get('phases', []):
            out.append(format_phase(ph))
        if not res.get('keys'):
            out.append('No solution found.')
        elif res.get('cooked'):
            out.append(f"COOKED: {len(res['keys'])} keys: {', '.join(res['keys'])}")
        rel = res.get('relations', {})
        if rel.get('changed'):
            out.append('Changed continuations:')
            for c in rel['changed']:
                out.append(f"   1...{c['defence']}: {'/'.join(c['from'])} -> {'/'.join(c['to'])}   [{c['phases'][0]} vs {c['phases'][1]}]")
        if rel.get('reciprocal'):
            out.append('Reciprocal changes:')
            for r in rel['reciprocal']:
                out.append(f"   {r['defences'][0]} / {r['defences'][1]}   [{r['phases'][0]} vs {r['phases'][1]}]")
        if rel.get('patterns'):
            out.append('Patterns:')
            for p in rel['patterns']:
                extra = p.get('defence') or ', '.join(p.get('defences', [])) or ' / '.join('/'.join(t) for t in p.get('threats', []))
                out.append(f"   {p['name']}: {extra}   [{' vs '.join(p['phases'])}]")
        if rel.get('transferred'):
            out.append('Transferred continuations:')
            for t in rel['transferred'][:20]:
                out.append(f"   {t['continuation']}: after {t['defences'][0]} -> after {t['defences'][1]}   [{t['phases'][0]} vs {t['phases'][1]}]")
    out.append(f"({res['nodes']} nodes, {res['seconds']}s)")
    return '\n'.join(out)


def format_compact(res):
    """Solution the way a composer reads it (E. Bourd s28): verdict first, key with threat, the thematic
    play grouped per piece (random move / corrections), duals on one line, tries on one line each,
    set play only where it differs. No patterns, no transfer lists, no move-by-move set play."""
    out = [f"{res['stipulation']} {res['count']}   {res['fen']}"]
    try:
        for line in promoted_force(chess.Board(res['fen'])):
            out.append(f"PROMOTED FORCE: {line}  (fatal)")
    except Exception:
        pass
    if res['kind'] != 'help':
        try:   # E. Bourd s29: the theme first, phase against phase, before the clutter
            from .thematic import build, format_table
            t = build(res)
            if t and (t['groups'] or t['rows']):
                out.append('Thematic play:')
                out += ['   ' + l for l in format_table(res, t).split('\n')]
        except Exception:
            pass
    if res['kind'] == 'help':
        out.append(f"{res['n_solutions']} solution(s): " + ' ; '.join(s['line'] for s in res['solutions']))
        return '\n'.join(out)
    phases = res.get('phases', [])
    setp = next((p for p in phases if p['type'] == 'set'), None)
    keys = [p for p in phases if p['type'] == 'key']
    tries = [p for p in phases if p['type'] == 'try']
    if not res.get('keys'):
        out.append('No solution.')
    elif res.get('cooked'):
        out.append(f"COOKED: {len(res['keys'])} keys: {', '.join(res['keys'])}")
    if setp:
        checks = [u for u in setp.get('unprovided', []) if u.endswith('+')]
        if checks:
            out.append('UNPROVIDED CHECK in the set play: ' + ', '.join(checks) + '  (fatal)')

    def phase_lines(ph, indent='   '):
        L = []
        real = [v for v in ph['variations'] if v['continuations'] and not v['refutes'] and not v['threat_repeat'] and not v['goal_by_defence']]
        used = set()
        for c in ph.get('corrections', []):
            r = c['random']
            parts = [f"{c['piece'][0]}~ {'/'.join(m for m in r['moves'] if m not in r['duals'])} 2.{r['mate']}"]
            parts += [f"{x['move']} 2.{'/'.join(x['mates'])}" for x in c['corrections'] if len(x['mates']) == 1]
            L.append(indent + '  |  '.join(parts))
            used.update(r['moves']); used.update(x['move'] for x in c['corrections'])
        singles, duals = [], []
        for v in real:
            d = v['defence']['san']
            if d in used and len(v['continuations']) == 1:
                continue
            if len(v['continuations']) > 1:
                duals.append(f"{d} 2.{'/'.join(x['san'] for x in v['continuations'])}")
            elif d not in used:
                singles.append((v['continuations'][0]['san'], d))
        by_mate = {}
        for m, d in singles:
            by_mate.setdefault(m, []).append(d)
        if by_mate:
            L.append(indent + '  |  '.join(f"{'/'.join(ds)} 2.{m}" for m, ds in by_mate.items()))
        if duals:
            L.append(indent + '[duals] ' + '  '.join(duals))
        hidden = sum(1 for v in ph['variations'] if v['threat_repeat'] and not v['refutes'])
        if hidden:
            L.append(indent + f'({hidden} other moves allow the threat)')
        return L

    for k in keys:
        head = f"1.{k['first_move']['san']}!"
        if k.get('threat'): head += f" (2.{_conts(k['threat'])})"
        elif k.get('check_key'): head += ' (mate in one)' if k['first_move']['san'].endswith('#') else ' (check)'
        else: head += ' (zugzwang)'
        out.append(head)
        out += phase_lines(k)
    if tries:
        for t in tries:
            th = f" (2.{_conts(t['threat'])})" if t.get('threat') else (' (check)' if t.get('check_key') else '')
            ref = 'stalemate!' if t.get('stalemate') else ', '.join(f"{r['san']}!" for r in t['refutations'])
            out.append(f"Try 1.{t['first_move']['san']}?{th} but {ref}")
            # E. Bourd (s29): the changes are the content; the short solution must show them under the try
            chg = _changes(res, 'try ' + t['first_move']['san'])
            if chg:
                out.append('   changed: ' + chg)
    rel = res.get('relations', {})
    ch = [c for c in rel.get('changed', []) if c['phases'][0] == 'set play' and c['phases'][1].startswith('key')]
    if ch:
        out.append('Set play differs: ' + _changes(res, 'set play'))
    if setp and keys and any(v['continuations'] for v in setp['variations']):
        km = {v['defence']['san']: [c['san'] for c in v['continuations']] for v in keys[0]['variations']
              if v['continuations'] and not v['threat_repeat']}
        changed_defs = {c['defence'] for c in ch}
        other = []
        for v in setp['variations']:
            if not v['continuations'] or v['defence']['san'] in changed_defs:
                continue
            sm = [c['san'] for c in v['continuations']]
            if v['defence']['san'] in km and sm != km[v['defence']['san']]:
                other.append(f"{v['defence']['san']} 2.{'/'.join(sm)}" + (' [dual]' if len(sm) > 1 else ''))
        if other:
            out.append('Set play also: ' + '  '.join(other))
        elif not ch and all([c['san'] for c in v['continuations']] == km.get(v['defence']['san'])
                            for v in setp['variations'] if v['continuations']):
            out.append('Set play: same mates as after the key')
    pats = [p_ for p_ in rel.get('patterns', []) if p_['name'] not in ('changed threat',)]
    if pats:
        seen = []
        for p_ in pats:
            what = p_.get('defence') or ', '.join(p_.get('defences', [])) or ''
            line = f"{p_['name']}{(': ' + what) if what else ''} [{' vs '.join(p_.get('phases', []))}]"
            if line not in seen:
                seen.append(line)
        out.append('Patterns: ' + '; '.join(seen[:6]))
    return '\n'.join(out)


def _changes(res, phase_label):
    """'c6 Sc8#->Sf5#, c5 Qxe5#->Qh6#' for one phase against the key (relations.changed)."""
    out = []
    for c in res.get('relations', {}).get('changed', []):
        if c['phases'][0] == phase_label and c['phases'][1].startswith('key'):
            f = '/'.join(c['from']) if isinstance(c['from'], list) else c['from']
            t = '/'.join(c['to']) if isinstance(c['to'], list) else c['to']
            item = f"{c['defence']} {f}->{t}"
            if f != t and item not in out:      # the same mate played by another unit or from elsewhere is no change
                out.append(item)
    return ', '.join(out)


def main(argv=None):
    ap = argparse.ArgumentParser(description='Orthodox chess problem solver/analyser (#n, h#n, s#n)')
    ap.add_argument('--white', help='e.g. "Kg1 Qd1 Sf3 e2"')
    ap.add_argument('--black', help='e.g. "Ke8 Rh8 f7"')
    ap.add_argument('--fen', help='FEN (piece placement is enough)')
    ap.add_argument('stipulation', help='#2, #3, h#2, h#2.5, s#2 ...')
    ap.add_argument('--tries', type=int, default=1, help='show tries with up to N refutations (0 = none)')
    ap.add_argument('--no-set', action='store_true')
    ap.add_argument('--time', type=float, default=120)
    ap.add_argument('--json', action='store_true')
    ap.add_argument('--critique', action='store_true', help="composer's critique (flaws / merits)")
    ap.add_argument('--compact', action='store_true', help='short solution: verdict, key, grouped play, tries')
    a = ap.parse_args(argv)
    if a.fen:
        p = Problem.from_fen(a.fen, a.stipulation)
    else:
        p = Problem.from_pieces(a.white.split(), a.black.split(), a.stipulation)
    res = analyse(p, max_refutations=a.tries, include_tries=a.tries > 0, include_set=not a.no_set, time_limit=a.time)
    print(json.dumps(res, indent=1, ensure_ascii=False) if a.json else (format_compact(res) if a.compact else format_report(res)))
    if a.critique and p.stip.kind != 'help':
        from .critique import critique, format_critique
        print('\nCritique:'); print(format_critique(critique(p, res)))


if __name__ == '__main__':
    main()
