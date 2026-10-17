"""Unmasking-key search: the key unit stands on FSQ in the diagram (masking the pin) and goes to KSQ.
Post-key: exactly one threat (not by the pinner on PSQ), the named defences each with the wanted mate, no holes,
no duals, no black checks; every white unit needed (removing it breaks the post-key spec); diagram: the key is unique.
usage: python3 -m chesscomp.compose.unmask_search CORE SEED KSQ FSQ PSQ WANT_JSON BUDGET_S RNG
The key unit may be any piece (a masking unit leaving the pin line, or the pinner arriving: KSQ=a5 FSQ=a2).
Optional env TRIES='{"d5c7": "b6b5"}': tries by first move uci, each with exactly that refutation.
Optional env SELFBLOCK=1: each wanted mate must need its defence's self-block (freethreat.self_block_needed).
Optional env THREAT=Qh4e4: the one threat must be that mate (a knight wheel on e4: every knight move guards e4).
The diagram must have no flight and no black check, and the key piece must guard a square of the king's field.
e.g. (two black rooks unpin Sc5, 11 Oct 2026; found 1.Bd5-f7! by hand from its failures):
  CORE=8/8/1r6/Q1n1k3/1r6/8/8/8 WANT='{"R6b5":"Qa5c7","R4b5":"Qa5c3"}' KSQ=e7 FSQ=d5 PSQ=a5
"""
from chesscomp.core import illegal_position as _illegal
import sys, os, random, time, json, chess
from chesscomp.compose.keyfind import post_spec
from chesscomp.core import Problem
from chesscomp.analysis import analyse
from chesscomp.compose.freethreat import self_block_needed
SELFBLOCK = os.environ.get('SELFBLOCK') == '1'
THREAT = os.environ.get('THREAT')                   # optional: the threat must be exactly this mate id

CORE, SEED = sys.argv[1], sys.argv[2]
KSQ, FSQ, PSQ = (chess.parse_square(x) for x in sys.argv[3:6])
TRIES = json.loads(os.environ.get('TRIES', '{}'))   # optional: {try uci: its one refutation uci}
WANT = json.loads(sys.argv[6]); BUDGET = float(sys.argv[7]); random.seed(int(sys.argv[8]))
core = chess.Board(CORE + ' b - - 0 1'); CSQ = {s: core.piece_at(s) for s in chess.SQUARES if core.piece_at(s)}


def promoted(b):
    if _illegal(b):                                   # retro: pawn captures, promotions (17 Oct 2026)
        return True
    for col in (chess.WHITE, chess.BLACK):
        w = lambda t: len(b.pieces(t, col))
        if w(chess.QUEEN) > 1 or w(chess.ROOK) > 2 or w(chess.KNIGHT) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def spec_ok(fen):
    b = chess.Board(fen + ' b - - 0 1')
    if not b.is_valid() or not chess.Board(fen + ' w - - 0 1').is_valid():
        return None
    t, d = post_spec(fen)
    names = {b.san(chess.Move.from_uci(u)): m for u, m in d.items()}
    return t, names, b


def post_score(fen):
    r = spec_ok(fen)
    if r is None:
        return -1e9, False, ''
    t, names, b = r
    s = 0.0
    bad = [x for x in t if x[1:3] == chess.square_name(PSQ)]
    good = [x for x in t if x not in bad]
    s -= 25 * len(bad) + (30 if not good else 12 * (len(good) - 1))
    s -= 30 if THREAT and set(t) != {THREAT} else 0
    holes = [k for k, m in names.items() if not m]; duals = [k for k, m in names.items() if len(m) > 1]
    s -= 6 * len(holes) + 4 * len(duals) + 2 * len([k for k in names if k not in WANT])
    for k, want in WANT.items():
        m = names.get(k)
        s += 12 if m == {want} else (-4 if m and want in m else -16)
    checks = [b.san(m) for m in b.legal_moves if b.gives_check(m)]
    s -= 5 * len(checks) + 0.7 * len(b.piece_map())
    # a by-play that repeats a wanted mate is a big flaw (E. Bourd, 11 Oct 2026): 1...Rd1 2.Sc3# beside 1...Sc2 2.Sc3#
    dups = [k for k, m in names.items() if k not in WANT and m & set(WANT.values())]
    s -= 10 * len(dups)
    unblocked = [k for k, w in WANT.items() if SELFBLOCK and names.get(k) == {w} and not self_block_needed(b, k, w)]
    s -= 20 * len(unblocked)
    ok = len(t) == 1 and not bad and (not THREAT or set(t) == {THREAT}) and not holes and not duals and not checks and not dups and not unblocked \
        and all(names.get(k) == {w} for k, w in WANT.items())
    return s, ok, f"unblocked={unblocked} threat={sorted(t)} holes={holes} duals={duals} dups={dups} checks={checks} defs={ {k: sorted(v) for k, v in names.items()} }"


def idle_units(fen, t0):
    """White units (not king, not pinner) whose removal keeps the post-key spec intact."""
    w = chess.Board(fen + ' w - - 0 1'); out = []
    _, names0, _ = spec_ok(fen)
    for sq, p in w.piece_map().items():
        if p.color != chess.WHITE or p.piece_type == chess.KING or sq == PSQ:
            continue
        x = w.copy(); x.remove_piece_at(sq)
        r = spec_ok(x.board_fen())
        if r is None:
            continue
        t, names, _ = r
        if t == t0 and all(names.get(k) == {v} for k, v in WANT.items()) and not [k for k, m in names.items() if not m]:
            out.append(p.symbol() + chess.square_name(sq))
    return out


def score(fen):
    b = chess.Board(fen + ' b - - 0 1')
    if promoted(b):
        return -1e9, ''
    s, ok, info = post_score(fen)
    if s < -1e8:
        return s, ''
    d = chess.Board(fen + ' w - - 0 1'); p = d.piece_at(KSQ)
    if p is None or d.piece_at(FSQ):
        return s - 80, info
    d.remove_piece_at(KSQ); d.set_piece_at(FSQ, p); D = d.board_fen()
    if not chess.Board(D + ' w - - 0 1').is_valid():
        return s - 80, info
    bb = chess.Board(D + ' b - - 0 1')
    dchecks = [bb.san(m) for m in bb.legal_moves if bb.gives_check(m)]
    dflights = [bb.san(m) for m in bb.legal_moves if bb.piece_type_at(m.from_square) == chess.KING]
    s -= 6 * len(dchecks) + 20 * len(dflights)
    if not ok:
        return s, info
    s += 100
    idle = idle_units(fen, post_spec(fen)[0])
    s -= 25 * len(idle)
    wd = chess.Board(D + ' w - - 0 1'); key = wd.san(chess.Move(FSQ, KSQ)).replace('N', 'S').rstrip('+#')
    try:
        keys = analyse(Problem.from_fen(D + ' w - - 0 1', '#2'), include_tries=False, include_set=False, time_limit=8).get('keys') or []
    except Exception:
        return s - 50, info
    good = keys == [key]
    s += 80 if good else (15 if key in keys else 0) - 8 * len(keys)
    ksq = bb.king(chess.BLACK); field = chess.SquareSet(chess.BB_KING_ATTACKS[ksq])
    inplay = bool(chess.Board(D + ' w - - 0 1').attacks(FSQ) & field)
    s += 0 if inplay else -40
    tinfo = ''
    if good and TRIES:
        try:
            ph = analyse(Problem.from_fen(D + ' w - - 0 1', '#2'), include_set=False, max_refutations=3, time_limit=10)['phases']
        except Exception:
            ph = []
        got = {p['first_move']['uci']: [r['uci'] for r in p['refutations']] for p in ph if p['type'] == 'try'}
        for t, ref in TRIES.items():
            g = got.get(t)
            s += 30 if g == [ref] else (8 if g and ref in g else -12)
        tinfo = f" tries={ {t: got.get(t) for t in TRIES} }"
        good = good and all(got.get(t) == [r] for t, r in TRIES.items())
    if good and not idle and not dchecks and not dflights and inplay:
        s += 100
    return s, f"{info} idle={idle} dchecks={dchecks} dflights={dflights} inplay={inplay} keys={keys}{tinfo} D={D}"


def mutate(fen):
    b = chess.Board(fen + ' b - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in CSQ]
    empty = [s for s in chess.SQUARES if not b.piece_at(s) and s != FSQ]
    op = random.random()
    if op < .35:
        sym = random.choice('NBRPPPpppnb'); sq = random.choice(empty)
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7):
            return fen
        b.set_piece_at(sq, chess.Piece.from_symbol(sym))
    elif op < .55 and free:
        s = random.choice(free)
        if b.piece_type_at(s) != chess.KING:
            b.remove_piece_at(s)
    elif free:
        s = random.choice(free); p = b.piece_at(s); b.remove_piece_at(s); b.set_piece_at(random.choice(empty), p)
    return b.board_fen()


t0 = time.time(); pop = [(score(SEED)[0], SEED)]; seen = {SEED}; best = pop[0]
while time.time() - t0 < BUDGET:
    pop.sort(key=lambda x: -x[0]); pop = pop[:14]
    ch = random.choice(pop[:6])[1]
    for _ in range(random.choice((1, 1, 2))):
        ch = mutate(ch)
    if ch in seen:
        continue
    seen.add(ch); sc, info = score(ch); pop.append((sc, ch))
    if sc > best[0]:
        best = (sc, ch); print('BEST', round(sc, 1), ch, info, flush=True)
pop.sort(key=lambda x: -x[0])
for sc, f in pop[:3]:
    print('TOP', round(sc, 1), f, score(f)[1])
print('evaluated', len(seen))
