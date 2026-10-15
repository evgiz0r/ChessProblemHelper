"""Make one move of the selector the only key while keeping a set/key change (E. Bourd, 15 Oct 2026: "changes where not
the same white piece does all the play, but 2 pieces ... the change is not due to movement of the piece, but rather
other effect which makes only 1 of the 2 mates possible").

The core holds the mechanism: the selector KP (its departure or arrival makes one of two mates possible), the Black
defence DEF, the set mate SETM and the key mate KEYM by another White unit. Everything else is mutated. Hard
constraints: no flight in the diagram, no mate in one, DEF answered in the set by SETM only and after the key by KEYM
only. Score: other keys (a complete check of every White first move, python-chess only), single quiet threat, units.
It found the reason for the key of claude-type2-d4-scheme: 1.Sc7! cuts Rb7 from d7, where the rook would close the
queen's file (1.Se7? Rd7!), from a position where all six knight moves solved.

    CORE=... SEED=... KP=d5 DEF=c5c4 SETM=d1d4 KEYM=d8d4 BUDGET_S=280 python -m chesscomp.compose.keysel JOB OUT

Confirm every hit with chesscomp.report.
"""
from __future__ import annotations
import os
import random
import sys
import time
import chess
from .trychange import legal, mutate


def mate_moves(p):
    out = []
    for m in p.legal_moves:
        p.push(m); ok = p.is_checkmate(); p.pop()
        if ok:
            out.append(m)
    return out


def solves(b, m):
    """True when White's first move m mates in two against every reply (stalemate is no solution)."""
    p = b.copy(); p.push(m)
    if p.is_stalemate():
        return False
    for bm in list(p.legal_moves):
        p.push(bm)
        if not p.is_checkmate():
            ok = False
            for wm in p.legal_moves:
                p.push(wm); ok = p.is_checkmate(); p.pop()
                if ok:
                    break
            if not ok:
                p.pop()
                return False
        p.pop()
    return True


def keys(b):
    return [m for m in list(b.legal_moves) if solves(b, m)]


def evaluate(b, kp, dfn, setm, keym):
    """(score, summary) for a diagram b; kp a square, dfn/setm/keym chess.Move."""
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid():
        return -1e9, ''
    if any(m.from_square == n.king(chess.BLACK) for m in n.legal_moves):
        return -500, 'flight'
    if mate_moves(b):
        return -500, 'mate in 1'
    if dfn not in n.legal_moves:
        return -500, 'no def'
    n.push(dfn); sm = mate_moves(n); n.pop()
    if sm != [setm]:
        return -400, 'set mate'
    ks = keys(b)
    sel = [m for m in ks if m.from_square == kp]
    s = -40.0 * (len(ks) - len(sel)) - 25 * max(0, len(sel) - 1)
    if not sel:
        return s - 100, f'no selector key; keys {[b.san(k) for k in ks]}'
    best = None
    for k in sel:
        p = b.copy(); p.push(k); q = p.copy(); q.push(chess.Move.null())
        thr = mate_moves(q) if q.is_valid() and not q.is_check() else []
        sc = -20 * abs(len(thr) - 1) - (40 if not thr else 0)
        if dfn in p.legal_moves:
            p.push(dfn); km = mate_moves(p); p.pop()
            sc += 40 if km == [keym] else -200
        if any(p.is_capture(m) for m in thr) or b.gives_check(k) or b.is_capture(k):
            sc -= 30
        if best is None or sc > best[0]:
            best = (sc, k, thr)
    s += best[0] + 60 - len(b.piece_map())
    return s, f"keys {[b.san(k) for k in ks]} | best {b.san(best[1])} thr {[t.uci() for t in best[2]]}"


def main(argv=None):
    a = argv or sys.argv[1:]
    job, out = int(a[0]), a[1]
    e = os.environ
    core = chess.Board(e['CORE'] + ' w - - 0 1')
    core_sq = {s for s in chess.SQUARES if core.piece_at(s)}
    kp = chess.parse_square(e['KP'])
    dfn, setm, keym = (chess.Move.from_uci(e[x]) for x in ('DEF', 'SETM', 'KEYM'))
    random.seed(job * 7919 + int(time.time()))
    seed = chess.Board(e.get('SEED', e['CORE']) + ' w - - 0 1')
    pop, seen, t0 = [(evaluate(seed, kp, dfn, setm, keym), seed)], {}, time.time()
    while time.time() - t0 < float(e.get('BUDGET_S', '240')):
        _, par = random.choice(pop[:6]) if random.random() < 0.8 else random.choice(pop)
        ch = mutate(par, core_sq, int(e.get('MAX_UNITS', '15')))
        if random.random() < 0.3:
            ch = mutate(ch, core_sq)
        if not legal(ch, set()) or ch.board_fen() in seen:
            continue
        r = evaluate(ch, kp, dfn, setm, keym); seen[ch.board_fen()] = r
        pop.append((r, ch)); pop.sort(key=lambda x: -x[0][0]); pop = pop[:40]
    with open(out, 'w') as f:
        for fen, (sc, summ) in sorted(seen.items(), key=lambda x: -x[1][0])[:20]:
            f.write(f'{sc:.1f} | {fen} | {summ}\n')


if __name__ == '__main__':
    main()
