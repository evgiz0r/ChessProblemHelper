"""One White piece, two mates per defence, one excluded in each phase (E. Bourd, 14 Oct 2026: "the same piece has two
mates, one excluded per phase for some reason, then doubled").

The core holds the selector (the key KEY, e.g. Kd2-e2 shutting the queen's d1-h5 diagonal and opening her file) and the
mating piece MP. A Black unit scores when one of its defences is answered in the set by MP alone and after the key by MP
alone on another square; it scores more when that move is the unit's only defence (E. Bourd: "the random moves by the
knights are annoying"). Hard rules: no flight, no mate in one, quiet key, every defence after the key answered by exactly
one mate (holes and duals cost), two units with a change, unique key (every White first move, python-chess only).
It made the f6 knight's defence specific in claude-type3-queen-lines (1...Sd7 cuts Bc8-f5) and found that only a knight
on e1 holds d3 and f3 there (no other second unit in four runs).

    CORE=... SEED=... KEY=d2e2 MP=d1 [FIX=f6] [NOQTHR=1] [QUIET=1] [PAWNY=3] [THRSQ=f3] [KEYSQ=e3,d3] [MUTATE=1] BUDGET_S=280 python -m chesscomp.compose.type3 JOB OUT

FIX: Black squares that must stay occupied (the first thematic unit). NOQTHR: the threat may not be made by MP. QUIET: thematic defences that capture do not count. PAWNY=3: each officer costs 3 more than a pawn.
THRSQ=f3: the threat must land there; KEYSQ=e3,d3: only key mates on these squares count.
MUTATE=1: a zugzwang key is not penalised (every Black move must then have a mate).
MP=any: any White pieces may mate (a plain 2x2 change); BYMOVE=1: count thematic defence moves, not units. Confirm every hit with chesscomp.report.
"""
from __future__ import annotations
import os
import random
import sys
import time
import chess
from .trychange import legal, mutate
from .keysel import mate_moves, keys


def evaluate(b, key, mp, fix=(), noqthr=False, quiet=False, pawny=0.0, thrsq=None, keysq=None, mutate=False, bymove=False):
    """(score, summary). good[u] lists the defences of Black unit u with the MP change; ndef[u] counts its defences."""
    n = b.copy(); n.push(chess.Move.null())
    if not n.is_valid() or b.is_check():
        return -1e9, ''
    bk = n.king(chess.BLACK)
    if any(m.from_square == bk for m in n.legal_moves):
        return -500, 'flight'
    if mate_moves(b):
        return -500, 'mate in 1'
    if key not in b.legal_moves or b.gives_check(key):
        return -500, 'key'
    if any(not b.piece_at(s) for s in fix):
        return -500, 'fixed unit gone'
    p = b.copy(); p.push(key); q = p.copy(); q.push(chess.Move.null())
    thr = mate_moves(q) if q.is_valid() and not q.is_check() else []
    s = 15.0 if len(thr) == 1 or (mutate and not thr) else (-40 if not thr else -15 * (len(thr) - 1))
    if thrsq is not None and [t.to_square for t in thr] != [thrsq]:
        s -= 60     # the threat must land on this square (E. Bourd: "the threat is due to the f3 square")
    if noqthr and any(t.from_square == mp for t in thr):
        s -= 60     # E. Bourd, 16 Oct 2026: a threat on the queen's new line lets a block defend (1...Sd3)
    holes = duals = 0
    good, ndef, bad = {}, {}, []
    for d in list(p.legal_moves):
        p.push(d)
        if p.is_checkmate():
            p.pop(); continue
        km = mate_moves(p); kms = [p.san(x) for x in km]; p.pop()
        if any(t in km for t in thr):
            continue
        if d.from_square != bk:
            ndef[d.from_square] = ndef.get(d.from_square, 0) + 1
        if not km:
            holes += 1; bad.append(p.san(d) + ':-'); continue
        if len(km) > 1:
            duals += len(km) - 1; bad.append(p.san(d) + ':' + '/'.join(kms))
        if d.from_square == bk or d not in n.legal_moves:
            continue
        n.push(d); sm = mate_moves(n); n.pop()
        same = mp is None or sm[0].from_square == mp == km[0].from_square if sm and km else False
        if len(sm) == 1 and len(km) == 1 and same and sm[0] != km[0]:
            if keysq is None or km[0].to_square in keysq:
                good.setdefault(d.from_square, []).append(d)
        elif len(sm) > 1:
            duals += 0.5 * (len(sm) - 1)
    if quiet:   # a capture is a weaker thematic defence than a quiet move (1...Rxc8 of the first pawn version)
        good = {u: [d for d in v if not p.is_capture(d)] for u, v in good.items()}
        good = {u: v for u, v in good.items() if v}
    if bymove:  # one unit may make both thematic defences (Strebkovs: the bishop to c5 or d4)
        n_good = sum(len(v) for v in good.values())
        s += 35 * min(n_good, 3) - (40 if n_good < 2 else 0)
    else:
        s += sum(30 + (25 if ndef.get(u) == 1 else 10 if ndef.get(u) == 2 else 0) for u in good)
        s -= 40 if len(good) < 2 else 0
    s -= 10 * holes + 14 * duals
    summ = (f"thr {[t.uci() for t in thr]} good {sorted(chess.square_name(u) + ':' + str(len(v)) + '/' + str(ndef.get(u)) for u, v in good.items())}"
            f" holes {holes} duals {duals} {' '.join(bad[:6])}")
    if s > 60:
        ks = keys(b)
        s += 60 if ks == [key] else -30 * len([k for k in ks if k != key]) - (80 if key not in ks else 0)
        summ = f"keys {[b.san(k) for k in ks]} | " + summ
    officers = sum(1 for pc in b.piece_map().values() if pc.piece_type not in (chess.PAWN, chess.KING))
    return s - len(b.piece_map()) - pawny * officers, summ


def main(argv=None):
    a = argv or sys.argv[1:]
    job, out = int(a[0]), a[1]
    E = os.environ
    core = chess.Board(E['CORE'] + ' w - - 0 1')
    core_sq = {s for s in chess.SQUARES if core.piece_at(s)}
    key = chess.Move.from_uci(E['KEY'])
    mp = None if E['MP'] == 'any' else chess.parse_square(E['MP'])
    fix = [chess.parse_square(x) for x in E.get('FIX', '').split(',') if x]
    noq, quiet, pawny = bool(E.get('NOQTHR')), bool(E.get('QUIET')), float(E.get('PAWNY') or 0)
    thrsq = chess.parse_square(E['THRSQ']) if E.get('THRSQ') else None
    keysq = {chess.parse_square(x) for x in E['KEYSQ'].split(',')} if E.get('KEYSQ') else None
    mut, bym = bool(E.get('MUTATE')), bool(E.get('BYMOVE'))
    random.seed(job * 7919 + int(time.time()))
    seed = chess.Board(E.get('SEED', E['CORE']) + ' w - - 0 1')
    if not legal(seed, set()):   # a third knight or a second dark bishop makes the seed promoted force (16 Oct 2026)
        print(f'warning: seed {seed.board_fen()} is not legal (promoted force, check or pawn on rank 1/8): '
              'the search starts from its mutations', file=sys.stderr)
    pop, seen, t0 = [(evaluate(seed, key, mp, fix, noq, quiet, pawny, thrsq, keysq, mut, bym), seed)], {}, time.time()
    while time.time() - t0 < float(E.get('BUDGET_S', '240')):
        _, par = random.choice(pop[:6]) if random.random() < 0.8 else random.choice(pop)
        ch = mutate(par, core_sq, int(E.get('MAX_UNITS', '13')))
        if random.random() < 0.3:
            ch = mutate(ch, core_sq)
        if not legal(ch, set()) or ch.board_fen() in seen:
            continue
        r = evaluate(ch, key, mp, fix, noq, quiet, pawny, thrsq, keysq, mut, bym); seen[ch.board_fen()] = r
        pop.append((r, ch)); pop.sort(key=lambda x: -x[0][0]); pop = pop[:40]
    with open(out, 'w') as f:
        for fen, (sc, summ) in sorted(seen.items(), key=lambda x: -x[1][0])[:15]:
            f.write(f'{sc:.1f} | {fen} | {summ}\n')


if __name__ == '__main__':
    main()
