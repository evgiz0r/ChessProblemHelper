"""Half-pin diagram search with thematic tries: the key and the tries are whatever the solver finds (E. Bourd, 13 Oct 2026,
on the orthogonal half-pin: "try to find a scheme where maybe multiple mates might be available. that freedom will
allow not to get stuck and have some choices").

    SPEC='{"core": "4R3/8/4r3/4b3/4k3/8/8/8", "seed": "...", "rook": "e6", "bishop": "e5", "budget": 280, "rng": 1}' \\
        python3 -m chesscomp.compose.halfpin_tries

Score of a diagram (solver phases): one key; in the key phase exactly one defence by the rook and one by the bishop,
each with one mate, the two mates different and each needing the pin (the mate fails with the pinner removed);
then tries refuted by the rook's defence alone and by the bishop's alone (a pure pair); no flight, no black check;
on a full candidate the critique runs and every fatal finding costs heavily. The mates and the threat are free.
"""
import json, os, random, time
import chess
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique
from chesscomp.compose.halfpin_pair import promoted

SPEC = json.loads(os.environ.get('SPEC', '{}'))


def pin_used(D, first, defence, mate, pinner):
    """True when the mate needs the pin: with the pinner gone it is no longer mate."""
    b = chess.Board(D + ' w - - 0 1')
    for u in (first, defence):
        mv = chess.Move.from_uci(u)
        if mv not in b.legal_moves:
            return False
        b.push(mv)
    m = chess.Move.from_uci(mate)
    if m not in b.legal_moves or m.from_square == pinner:
        return False
    b.remove_piece_at(pinner)
    if not b.is_valid():
        return False
    b.push(m)
    return not b.is_checkmate()


def phase_defs(ph, rsq, bsq):
    out = {'r': [], 'b': [], 'other': []}
    for v in ph['variations']:
        if v.get('threat_repeat'):
            continue
        d = v['defence']
        fs = chess.parse_square(d['uci'][:2])
        k = 'r' if fs == rsq else 'b' if fs == bsq else 'other'
        out[k].append((d['uci'], [c['uci'] for c in v['continuations']], d['san'], [c['san'] for c in v['continuations']]))
    return out


def score(D, spec):
    rsq, bsq = chess.parse_square(spec['rook']), chess.parse_square(spec['bishop'])
    b = chess.Board(D + ' w - - 0 1')
    if not b.is_valid() or promoted(b) or b.is_check():
        return -1e9, ''
    s = -0.5 * len(b.piece_map())
    bb = chess.Board(D + ' b - - 0 1')
    flights = [m for m in bb.legal_moves if bb.piece_type_at(m.from_square) == chess.KING]
    checks = [m for m in bb.legal_moves if bb.gives_check(m)]
    s -= 20 * len(flights) + 6 * len(checks)
    try:
        r = analyse(Problem.from_fen(D + ' w - - 0 1', '#2'), max_refutations=2, time_limit=6)
    except Exception:
        return -1e9, ''
    keys = r.get('keys') or []
    if not keys:
        return s - 100, 'no key'
    s -= 25 * (len(keys) - 1)
    kph = [p for p in r['phases'] if p['type'] == 'key'][0]
    if not kph.get('threat'):
        s -= 15
    dd = phase_defs(kph, rsq, bsq)
    pinner = None
    ksq = bb.king(chess.BLACK)
    for sq in chess.SquareSet(chess.BB_RAYS[ksq][rsq]) if chess.BB_RAYS[ksq][rsq] else []:
        p = b.piece_at(sq)
        if p and p.color == chess.WHITE and sq not in (rsq, bsq) and p.piece_type in (chess.ROOK, chess.QUEEN):
            if chess.square_distance(sq, ksq) > chess.square_distance(rsq, ksq):
                pinner = sq
                break
    good = {}
    for k in ('r', 'b'):
        lst = dd[k]
        s -= 10 * max(0, len(lst) - 1) + (25 if not lst else 0)
        singles = [x for x in lst if len(x[1]) == 1]
        if len(lst) == 1 and singles:
            u, (m,), san, msan = singles[0]
            used = pinner is not None and pin_used(D, kph['first_move']['uci'], u, m, pinner)
            s += 20 + (10 if used else -10)
            good[k] = (u, m, san, msan[0], used)
        elif singles:
            s += 5
    if len(good) == 2 and good['r'][1] == good['b'][1]:
        s -= 15
    s -= 6 * len([x for x in dd['other'] if len(x[1]) > 1]) + 2 * len(dd['other'])
    info = f"keys={keys} threat={[t['san'] for t in kph.get('threat') or []]} R={good.get('r')} B={good.get('b')} other={[(x[2], x[3]) for x in dd['other']]}"
    tries = []
    if len(good) == 2:
        rr, br = good['r'][0], good['b'][0]
        pr = pb = False
        for p in r['phases']:
            if p['type'] != 'try' or not p.get('threat'):
                continue
            refs = [x['uci'] for x in p.get('refutations') or []]
            if refs == [rr]:
                pr = True; tries.append(p['first_move']['san'] + '?' + good['r'][2])
            elif refs == [br]:
                pb = True; tries.append(p['first_move']['san'] + '?' + good['b'][2])
        s += 40 * pr + 40 * pb
        info += f" tries={tries}"
        if pr and pb and len(keys) == 1 and not flights and not checks:
            s += 60
            try:
                c = critique(Problem.from_fen(D + ' w - - 0 1', '#2'), r, necessity=False)
                major = [f['rule'] for f in c['findings'] if f['severity'] == 'major']
            except Exception as e:
                major = ['critique-error']
            s -= 40 * len(major)
            info += f" major={major}" + (' FULL' if not major else '')
    return s, info + f" flights={len(flights)} checks={len(checks)}"


def mutate(fen, fixed):
    b = chess.Board(fen + ' w - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in fixed]
    empty = [s for s in chess.SQUARES if not b.piece_at(s)]
    op = random.random()
    if op < .33 and empty:
        sym = random.choice('NBRPPQpppnbr')
        sq = random.choice(empty)
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7):
            return fen
        b.set_piece_at(sq, chess.Piece.from_symbol(sym))
    elif op < .53 and free:
        s = random.choice(free)
        if b.piece_type_at(s) != chess.KING:
            b.remove_piece_at(s)
    elif free and empty:
        s = random.choice(free)
        p = b.piece_at(s)
        b.remove_piece_at(s)
        t = random.choice(empty)
        if p.piece_type == chess.PAWN and chess.square_rank(t) in (0, 7):
            return fen
        b.set_piece_at(t, p)
    return b.board_fen()


def main():
    spec = SPEC
    random.seed(spec.get('rng', 1))
    fixed = set(chess.BaseBoard(spec['core']).piece_map())
    seed = spec.get('seed', spec['core'])
    t0 = time.time()
    budget = spec.get('budget', 280)
    pop = [(score(seed, spec)[0], seed)]
    seen = {seed}
    best = pop[0]
    print('SEED', round(best[0], 1), seed, score(seed, spec)[1], flush=True)
    while time.time() - t0 < budget:
        pop.sort(key=lambda x: -x[0])
        pop = pop[:14]
        ch = random.choice(pop[:6])[1]
        for _ in range(random.choice((1, 1, 2))):
            ch = mutate(ch, fixed)
        if ch in seen:
            continue
        seen.add(ch)
        sc, info = score(ch, spec)
        pop.append((sc, ch))
        if sc > best[0]:
            best = (sc, ch)
            print('BEST', round(sc, 1), ch, info, flush=True)
    pop.sort(key=lambda x: -x[0])
    for sc, f in pop[:3]:
        print('TOP', round(sc, 1), f, score(f, spec)[1], flush=True)
    print('evaluated', len(seen), flush=True)


if __name__ == '__main__':
    main()
