"""Half-pin with a pure try pair: one knight mates in both thematic variations from its key square, and each try
square reaches only one of the two mating squares (E. Bourd, 12 Oct 2026: "black half pin of a bishop and a rook"; on a
first version with 1...B~ 2.Sf6#: "this is not good, means again that we cannot make a try, as all of these will refute.
and the motivation of defense is not pure").

    SPEC='{"core": "4R3/8/4r3/4bN2/4k3/8/8/8", "key": "e3f5", "rook": "e6", "bishop": "e5",
           "mr": "Nf5g3", "mb": "Nf5d6", "tr": "e3g4", "tb": "e3d1", "budget": 280, "rng": 1}' \
        python3 -m chesscomp.compose.halfpin_pair

core: post-key units that never move (Z already on its key square). Post-key spec (scored): exactly one threat, not by
the key piece; exactly one defence by the rook, answered only by mr; exactly one by the bishop, answered only by mb
(pure motives: no other move of either unit defends); every other defence has one mate that is neither mr nor mb; no
black check. Diagram (Z back on the key's origin): no flight, no black check, the key is the only key, the try tr is
refuted only by the rook's defence and tb only by the bishop's. The threat is free: the search finds it.
"""
import json, os, random, sys, time
import chess
from chesscomp.compose.keyfind import post_spec
from chesscomp.core import Problem
from chesscomp.analysis import analyse

SPEC = json.loads(os.environ.get('SPEC', '{}'))


def promoted(b):
    for col in (chess.WHITE, chess.BLACK):
        n = lambda t: len(b.pieces(t, col))
        if n(chess.QUEEN) > 1 or n(chess.ROOK) > 2 or n(chess.KNIGHT) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def post_check(fen, spec):
    """(score, ok, rook defence uci, bishop defence uci, info) of the post-key position."""
    b = chess.Board(fen + ' b - - 0 1')
    if not b.is_valid() or not chess.Board(fen + ' w - - 0 1').is_valid() or promoted(b):
        return -1e9, False, None, None, ''
    key = chess.Move.from_uci(spec['key'])
    t, d = post_spec(fen)
    s = 0.0
    bykey = [x for x in t if x[1:3] == chess.square_name(key.to_square)]
    s -= 30 * (len(t) != 1) + 12 * max(0, len(t) - 1) + 25 * len(bykey) + (30 if not t else 0)
    rsq, bsq = chess.parse_square(spec['rook']), chess.parse_square(spec['bishop'])
    rdef = {u: m for u, m in d.items() if chess.Move.from_uci(u).from_square == rsq}
    bdef = {u: m for u, m in d.items() if chess.Move.from_uci(u).from_square == bsq}
    rgood = [u for u, m in rdef.items() if m == {spec['mr']}]
    bgood = [u for u, m in bdef.items() if m == {spec['mb']}]
    s += 14 * bool(rgood) + 14 * bool(bgood) - 8 * max(0, len(rdef) - 1) - 8 * max(0, len(bdef) - 1)
    s -= 6 * (not rdef) + 6 * (not bdef)
    other = {u: m for u, m in d.items() if u not in rdef and u not in bdef}
    holes = [u for u, m in other.items() if not m]
    duals = [u for u, m in other.items() if len(m) > 1]
    dups = [u for u, m in other.items() if m & {spec['mr'], spec['mb']}]
    s -= 6 * len(holes) + 4 * len(duals) + 10 * len(dups) + 1.5 * len(other)
    checks = [m for m in b.legal_moves if b.gives_check(m)]
    s -= 5 * len(checks) + 0.6 * len(b.piece_map())
    ok = (len(t) == 1 and not bykey and len(rdef) == 1 and len(bdef) == 1 and rgood and bgood
          and not holes and not duals and not dups and not checks)
    r = rgood[0] if len(rdef) == 1 and rgood else None
    bb = bgood[0] if len(bdef) == 1 and bgood else None
    info = (f"threat={sorted(t)} rook={ {u: sorted(m) for u, m in rdef.items()} } bishop={ {u: sorted(m) for u, m in bdef.items()} } "
            f"holes={holes} duals={duals} dups={dups} checks={len(checks)}")
    return s, ok, r, bb, info


def diagram_of(fen, spec):
    key = chess.Move.from_uci(spec['key'])
    d = chess.Board(fen + ' w - - 0 1')
    p = d.piece_at(key.to_square)
    if p is None or d.piece_at(key.from_square):
        return None
    d.remove_piece_at(key.to_square)
    d.set_piece_at(key.from_square, p)
    return d.board_fen()


def score(fen, spec):
    s, ok, r, bb, info = post_check(fen, spec)
    if s < -1e8:
        return s, ''
    D = diagram_of(fen, spec)
    if D is None or not chess.Board(D + ' w - - 0 1').is_valid():
        return s - 80, info
    bd = chess.Board(D + ' b - - 0 1')
    flights = [m for m in bd.legal_moves if bd.piece_type_at(m.from_square) == chess.KING]
    dchecks = [m for m in bd.legal_moves if bd.gives_check(m)]
    s -= 20 * len(flights) + 6 * len(dchecks)
    if not ok:
        return s, info
    s += 100
    wd = chess.Board(D + ' w - - 0 1')
    key = chess.Move.from_uci(spec['key'])
    if key not in wd.legal_moves:
        return s - 60, info
    key_san = wd.san(key).replace('N', 'S').rstrip('+#')
    try:
        res = analyse(Problem.from_fen(D + ' w - - 0 1', '#2'), include_set=False, max_refutations=3, time_limit=10)
    except Exception:
        return s - 50, info
    keys = res.get('keys') or []
    got = {p['first_move']['uci']: [x['uci'] for x in p['refutations']] for p in res['phases'] if p['type'] == 'try'}
    good = keys == [key_san]
    s += 80 if good else (15 if key_san in keys else 0) - 8 * len(keys)
    want = {spec['tr']: r, spec['tb']: bb}
    for t, ref in want.items():
        g = got.get(t)
        s += 40 if g == [ref] else (8 if g and ref in g else -12)
    full = good and all(got.get(t) == [ref] for t, ref in want.items()) and not flights and not dchecks
    if full:
        s += 150
    return s, f"{info} keys={keys} tries={ {t: got.get(t) for t in want} } flights={len(flights)} dchecks={len(dchecks)} D={D}{' FULL' if full else ''}"


def mutate(fen, fixed, keep_empty):
    b = chess.Board(fen + ' b - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in fixed]
    empty = [s for s in chess.SQUARES if not b.piece_at(s) and s not in keep_empty]
    op = random.random()
    if op < .35 and empty:
        sym = random.choice('NBRPPPpppnbr')
        sq = random.choice(empty)
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7):
            return fen
        b.set_piece_at(sq, chess.Piece.from_symbol(sym))
    elif op < .55 and free:
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
    core = chess.BaseBoard(spec['core'])
    fixed = set(core.piece_map())
    key = chess.Move.from_uci(spec['key'])
    keep_empty = {key.from_square}
    for u in (spec['tr'], spec['tb']):
        keep_empty.add(chess.Move.from_uci(u).to_square)
    for m in (spec['mr'], spec['mb']):
        keep_empty.add(chess.parse_square(m[3:5]))
    seed = spec.get('seed', spec['core'])
    sb = chess.BaseBoard(seed)
    if sb.king(chess.WHITE) is None:
        sb.set_piece_at(chess.A1, chess.Piece.from_symbol('K'))
        seed = sb.board_fen()
    t0 = time.time()
    budget = spec.get('budget', 280)
    pop = [(score(seed, spec)[0], seed)]
    seen = {seed}
    best = pop[0]
    while time.time() - t0 < budget:
        pop.sort(key=lambda x: -x[0])
        pop = pop[:14]
        ch = random.choice(pop[:6])[1]
        for _ in range(random.choice((1, 1, 2))):
            ch = mutate(ch, fixed, keep_empty)
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
