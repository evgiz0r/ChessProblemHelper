"""White correction score (daily No. 10, 15 Oct 2026): the key piece's random move fails to one defence, its
corrections fail to others, the key is the correction with no negative effect.

    from chesscomp.compose.white_correction import wcorr_score
    sc, summary, ok = wcorr_score(board, analysis, 'e7', ncorr=2)

`analysis` is `chesscomp.analysis.analyse(..., include_tries=True)`. Only the phases whose first move is by the
unit on `sq` count. The random refutation is the single refutation shared by the most tries (at least two); each
other single refutation of a try by that unit is a correction's. `ok` needs: the key by that unit and unique, quiet
and not a capture, one threat shared by the key and the counted tries, the random stage, `ncorr` distinct correction
refutations, no try refuted by a king move, and a single mate in the key after every one of those refutations (or the threat itself, when the key
leaves it no defence).
Used by `chesscomp.compose.evolve` (WCORR=<square>) and by `python -m chesscomp.compose.white_correction FEN SQ`.
"""
import sys
from collections import Counter

import chess


def _nref(ph):
    r = ph['refutations']
    return len(r) if isinstance(r, list) else r


def wcorr_score(b, r, sq, ncorr=2):
    phases = r.get('phases') or []
    keys = r.get('keys') or []
    ksq = chess.square_name(b.king(chess.BLACK))
    mine = [ph for ph in phases if ph['type'] in ('key', 'try') and ph['first_move']['uci'][:2] == sq
            and not ph.get('check_key')]
    key = next((ph for ph in mine if ph['type'] == 'key'), None)
    t = 0.0
    if key and len(keys) == 1:
        t += 60
    elif key:
        t += 30 - 20 * (len(keys) - 1)
    else:
        t -= 40 + 18 * len(keys)
    thr = lambda ph: frozenset(x['san'] for x in ph.get('threat') or [])
    ref = key or (min((ph for ph in mine), key=_nref) if mine else None)
    if not ref:
        return t - 60, f'no move of the unit on {sq}', False
    kthr = thr(ref)
    tries = [ph for ph in mine if ph['type'] == 'try' and thr(ph) == kthr]
    single = [(ph, ph['refutations'][0]) for ph in tries if isinstance(ph['refutations'], list) and _nref(ph) == 1]
    cnt = Counter(x['uci'] for _, x in single)
    rnd, nrnd = (cnt.most_common(1)[0] if cnt else (None, 0))
    corr = {u for u in cnt if u != rnd}
    king_refs = sum(1 for ph in tries if isinstance(ph['refutations'], list)
                    and any(x['uci'][:2] == ksq for x in ph['refutations']))
    t += 25 * (nrnd >= 2) + 4 * min(nrnd, 4)
    t += 22 * min(len(corr), ncorr + 1)
    t -= 15 * king_refs + 2 * sum(_nref(ph) - 1 for ph in tries if _nref(ph) > 1)
    t -= 10 * (len(mine) - len(tries) - (1 if key else 0))      # moves of the unit with another threat or none
    t += 4 if len(kthr) == 1 else -8 * max(0, len(kthr) - 1)
    if 'x' in ref['first_move']['san']:
        t -= 20
    # the key answers every thematic refutation with one mate; a mate changed from the random stage is content
    vm = {v['defence']['uci']: v for v in ref['variations']} if key else {}
    answered, changed = 0, 0
    for u in ([rnd] if rnd else []) + sorted(corr):
        v = vm.get(u)
        if key and (not v or v['threat_repeat']):       # no longer a defence after the key: the threat mates
            answered += 1
        elif v and len(v['continuations']) == 1:
            answered += 1
            km = v['continuations'][0]['san']
            others = [w for ph, x in single if x['uci'] != u for w in ph['variations']
                      if w['defence']['uci'] == u and w['continuations']]
            if others and all(km not in {c['san'] for c in w['continuations']} for w in others):
                changed += 1
        elif v:
            t -= 6
    t += 10 * answered + 8 * changed
    ok = (bool(key) and len(keys) == 1 and len(kthr) == 1 and 'x' not in key['first_move']['san']
          and nrnd >= 2 and len(corr) >= ncorr and not king_refs and answered == 1 + len(corr))
    san = {x['uci']: x['san'] for _, x in single}
    summ = (f"{(key or ref)['first_move']['san']} thr={'/'.join(sorted(kthr))} random {san.get(rnd, '-')}x{nrnd} "
            + ' '.join(f"{ph['first_move']['san']}?{x['san']}" for ph, x in single if x['uci'] != rnd)
            + f" kingref={king_refs} changed={changed}")
    return t, summ, ok


if __name__ == '__main__':
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    fen, sq = sys.argv[1], sys.argv[2]
    b = chess.Board(fen if ' ' in fen else fen + ' w - - 0 1')
    r = analyse(Problem.from_fen(b.fen(), '#2'), max_refutations=4, include_tries=True, include_set=True, time_limit=30)
    sc, summ, ok = wcorr_score(b, r, sq, int(sys.argv[3]) if len(sys.argv) > 3 else 2)
    print(f'{"OK" if ok else "no"} {sc:.1f} {summ}')
