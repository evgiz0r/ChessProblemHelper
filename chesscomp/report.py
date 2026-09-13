"""Human-readable (album style) rendering of an analysis dict, plus a small CLI."""
from __future__ import annotations
import argparse, json, sys
from .core import Problem
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
    if ph['type'] == 'try':
        lines.append('   but ' + ', '.join(f"1...{r['san']}!" for r in ph['refutations']))
    if ph['type'] == 'set' and ph.get('unprovided'):
        lines.append('   unprovided: ' + ', '.join(ph['unprovided']))
    return '\n'.join(lines)


def format_report(res):
    out = [f"{res['stipulation']} {res['count']}   FEN {res['fen']}"]
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
    a = ap.parse_args(argv)
    if a.fen:
        p = Problem.from_fen(a.fen, a.stipulation)
    else:
        p = Problem.from_pieces(a.white.split(), a.black.split(), a.stipulation)
    res = analyse(p, max_refutations=a.tries, include_tries=a.tries > 0, include_set=not a.no_set, time_limit=a.time)
    print(json.dumps(res, indent=1, ensure_ascii=False) if a.json else format_report(res))
    if a.critique and p.stip.kind != 'help':
        from .critique import critique, format_critique
        print('\nCritique:'); print(format_critique(critique(p, res)))


if __name__ == '__main__':
    main()
