"""Validate chesscomp against a yacpdb export: does the solver find the published key / helpmate solutions?

usage: python tests/validate_yacpdb.py bourd_yacpdb.json [--kinds '#2,#3,s#2,h#2'] [--time 60] [--jobs 4]
"""
import argparse, json, re, sys, os, time
from multiprocessing import Pool
import chess
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from chesscomp import Problem, analyse
from chesscomp.core import Stipulation

ORTHO = set('KQRBSP')


def load(e):
    a = e.get('algebraic', {})
    if a.get('neutral') or e.get('twins') or e.get('options') and any(o.lower() not in ('setplay', 'defence 1') for o in e['options']):
        return None
    if any(t[0] not in ORTHO or len(t) != 3 for s in ('white', 'black') for t in a.get(s, [])):
        return None
    try:
        Stipulation.parse(e['stipulation'])
    except ValueError:
        return None
    return Problem.from_pieces(a['white'], a['black'], e['stipulation'], id=e['id'])


def to_uci(board, tok):
    m = re.search(r'([a-h][1-8])[-*x]?([a-h][1-8])(=?[QRBSN])?', tok)
    if m and re.search(r'[a-h][1-8][-*][a-h][1-8]', tok):
        pr = (m.group(3) or '').replace('=', '').replace('S', 'N').lower()
        return m.group(1) + m.group(2) + pr
    t = tok.replace('S', 'N').replace('0-0-0', 'O-O-O').replace('0-0', 'O-O')
    t = re.sub(r'[!?#+]+$', '', t)
    try:
        b = board.copy(); b.turn = chess.WHITE
        return b.parse_san(t).uci()
    except Exception:
        return None


def expected_keys(p, sol):
    keys = set()
    for m in re.finditer(r'(?m)^\s*1\.(?!\.)\s*([^\s{]+?)\s*(?:\{[^}]*\})?\s*!', sol):
        u = to_uci(p.board, m.group(1))
        if u:
            keys.add(u)
    return keys


def expected_help_first(p, sol):
    firsts = set()
    for m in re.finditer(r'(?m)^\s*1\.(?!\.)\s*(\S+)', sol):
        tok = m.group(1)
        mm = re.search(r'([a-h][1-8])[-*]([a-h][1-8])(=[QRBS])?', tok)
        if mm:
            firsts.add(mm.group(1) + mm.group(2) + (mm.group(3) or '').replace('=', '').replace('S', 'n').lower())
        else:
            try:
                firsts.add(p.board.parse_san(tok.replace('S', 'N').rstrip('+#')).uci())
            except Exception:
                pass
    return firsts


def run(args):
    e, tl = args
    p = load(e)
    if p is None:
        return {'id': e['id'], 'status': 'skip'}
    t0 = time.time()
    try:
        r = analyse(p, max_refutations=1, include_tries=True, include_set=True, time_limit=tl)
    except Exception as ex:
        return {'id': e['id'], 'stip': e['stipulation'], 'status': 'error', 'err': repr(ex)}
    out = {'id': e['id'], 'stip': e['stipulation'], 'sec': r['seconds']}
    if r.get('timeout'):
        out['status'] = 'timeout'; return out
    sol = e.get('solution', '')
    if p.stip.kind == 'help':
        exp = expected_help_first(p, sol)
        got = {s['uci'][0] for s in r['solutions']}
        out['n'] = r['n_solutions']; out['exp_first'] = sorted(exp); out['got_first'] = sorted(got)
        out['status'] = 'ok' if exp and exp <= got else ('nodata' if not exp else 'mismatch')
        if out['status'] == 'ok' and got - exp:
            out['status'] = 'extra-solutions'
    else:
        exp = expected_keys(p, sol)
        got = {k['first_move']['uci'] for k in r['phases'] if k['type'] == 'key'}
        out['exp'] = sorted(exp); out['got'] = sorted(got)
        out['tries'] = [ph['first_move']['san'] for ph in r['phases'] if ph['type'] == 'try']
        rel = r['relations']
        pats = {x['name'].split(' (')[0] for x in rel.get('patterns', [])}
        if rel.get('changed'): pats.add('Changed mates')
        if rel.get('reciprocal'): pats.add('Reciprocal')
        if rel.get('transferred'): pats.add('Transferred mates')
        pats |= {'Zagoruiko' for x in pats if x.startswith('Zagoruiko')}
        out['patterns'] = sorted(pats)
        out['keywords'] = e.get('keywords', [])
        if not exp:
            out['status'] = 'nodata'
        elif exp <= got and len(got) == len(exp):
            out['status'] = 'ok'
        elif exp <= got:
            out['status'] = 'cook?'
        else:
            out['status'] = 'mismatch'
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('json')
    ap.add_argument('--kinds', default='#2')
    ap.add_argument('--time', type=float, default=60)
    ap.add_argument('--jobs', type=int, default=os.cpu_count())
    ap.add_argument('--limit', type=int, default=0)
    ap.add_argument('--out', default='validation.json')
    a = ap.parse_args()
    data = json.load(open(a.json, encoding='utf-8'))
    kinds = [k.strip() for k in a.kinds.split(',')]
    sel = [e for e in data if e.get('stipulation', '').replace(' ', '') in kinds]
    if a.limit:
        sel = sel[:a.limit]
    with Pool(a.jobs) as pool:
        res = pool.map(run, [(e, a.time) for e in sel], chunksize=1)
    json.dump(res, open(a.out, 'w'), indent=1, ensure_ascii=False)
    from collections import Counter
    for k in kinds:
        c = Counter(r['status'] for r in res if r.get('stip', '').replace(' ', '') == k)
        secs = [r['sec'] for r in res if r.get('stip', '').replace(' ', '') == k and 'sec' in r]
        print(f"{k:6} {dict(c)}  avg {sum(secs)/max(1,len(secs)):.2f}s  max {max(secs or [0]):.1f}s")
    themes = ['Changed mates', 'Reciprocal', 'Le Grand', 'Pseudo Le Grand', 'Zagoruiko', 'Threat reversal', 'Dombrovskis', 'Transferred mates', 'Grimshaw', 'Bristol']
    print('theme recall (tagged in yacpdb -> detected):')
    for t in themes:
        tagged = [r for r in res if t in r.get('keywords', [])]
        hit = [r for r in tagged if t in r.get('patterns', [])]
        flagged = [r for r in res if t in r.get('patterns', []) and 'keywords' in r]
        if tagged or flagged:
            print(f"   {t:18} {len(hit)}/{len(tagged)} tagged found   (detected in {len(flagged)} problems overall)")
    print('skipped (fairy/twins):', sum(1 for r in res if r['status'] == 'skip'))


if __name__ == '__main__':
    main()
