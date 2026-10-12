"""Post-key search with a free threat: exactly one threat (not a move from the square NOQ, e.g. the pinner's),
the named defences each answered by the wanted mate only, no holes, no duals, no other defence repeating a wanted
mate, the wanted mates all different. Core units never move; every other unit is added, removed or moved.

    python3 -m chesscomp.compose.freethreat CORE SEED WANT_JSON NOQ BUDGET_S RNG     (NOQ=zz: no restriction)

WANT maps a defence (python-chess SAN, N for knights) to a mate pattern (fnmatch on move ids like Qa4c4: "*c4",
"N*c3"). Env PURE=1 also rejects a defence that guards a threat square from its arrival (impure).
Found the post-keys of the two-rooks unpin (11 Oct 2026) and the knight line-closing problem (12 Oct 2026):
    CORE=4Q3/8/8/3k4/8/8/8/2r1nN1b WANT='{"Nc2":"N*c3","Ng2":"Qe8e4"}' -> 4Q3/2K5/8/3k4/2R5/1Pp5/8/1Nr1nN1b
"""
import sys, os, random, time, json, chess, fnmatch
from .keyfind import post_spec

CORE, WANT, NOQ, CSQ = '8/8/8/8/8/8/8/8', {}, 'zz', {}


def configure(core: str, want: dict, noq: str = 'zz'):
    global CORE, WANT, NOQ, CSQ
    CORE, WANT, NOQ = core, want, noq
    b = chess.Board(core + ' b - - 0 1'); CSQ = {s: b.piece_at(s) for s in chess.SQUARES if b.piece_at(s)}


def promoted(b):
    for col in (chess.WHITE, chess.BLACK):
        w = lambda t: len(b.pieces(t, col))
        if w(chess.QUEEN) > 1 or w(chess.ROOK) > 2 or w(chess.KNIGHT) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def self_block_needed(b: chess.Board, defence_san: str, mate_id: str) -> bool:
    """True when the defence lands next to the black king and its mate fails once the blocker is taken off (the king
    escapes to the square): the self-block is the error (E. Bourd's theme, 12 Oct 2026)."""
    bb = b.copy()
    try:
        d = bb.parse_san(defence_san)
    except ValueError:
        return False
    if chess.square_distance(d.to_square, bb.king(chess.BLACK)) != 1:
        return False
    bb.push(d)
    mv = next((x for x in bb.legal_moves if f"{bb.piece_at(x.from_square).symbol().upper()}"
               f"{chess.square_name(x.from_square)}{chess.square_name(x.to_square)}" == mate_id), None)
    if mv is None or mv.to_square == d.to_square:        # capturing the blocker uses no self-block
        return False
    bb.push(mv)
    if not bb.is_checkmate():
        return False
    bb.remove_piece_at(d.to_square)
    # the king must escape to the emptied square itself; a mate that fails only because the blocker also cut a
    # black line (Sxc4 cutting Ra4-d4 against Qd3+) is an interference, not a self-block (12 Oct 2026)
    return any(m.to_square == d.to_square and bb.piece_type_at(m.from_square) == chess.KING for m in bb.legal_moves)


def score(fen):
    b = chess.Board(fen + ' b - - 0 1')
    if not b.is_valid() or promoted(b) or not chess.Board(fen + ' w - - 0 1').is_valid():
        return -1e9, ''
    t, d = post_spec(fen)
    s = 0.0
    bad = [x for x in t if x.startswith(NOQ) or x[1:3] == NOQ]
    good = [x for x in t if x not in bad]
    s -= 25 * len(bad) + (30 if not good else 12 * (len(good) - 1))
    names = {b.san(chess.Move.from_uci(u)): m for u, m in d.items()}
    holes = [k for k, m in names.items() if not m]; duals = [k for k, m in names.items() if len(m) > 1]
    s -= 6 * len(holes) + 4 * len(duals) + 2 * len([k for k in names if k not in WANT])
    def wok(m, want):
        return m is not None and len(m) == 1 and fnmatch.fnmatch(next(iter(m)), want)
    wanted_mates = set()
    for k, want in WANT.items():
        m = names.get(k)
        s += 12 if wok(m, want) else (-4 if m and any(fnmatch.fnmatch(x, want) for x in m) else -16)
        if m: wanted_mates |= set(m)
    dups = [k for k, m in names.items() if k not in WANT and m & wanted_mates]
    wm = [next(iter(names[k])) for k in WANT if names.get(k) and len(names[k]) == 1]
    if len(set(wm)) < len(wm):
        dups.append('same-mate')
    s -= 10 * len(dups)
    impure = []
    if os.environ.get('PURE') == '1':
        for k in WANT:
            try:
                mv = b.parse_san(k)
            except ValueError:
                continue
            bb = b.copy(); bb.push(mv)
            for x in t:
                if bb.is_attacked_by(chess.BLACK, chess.parse_square(x[3:5])) and not b.is_attacked_by(chess.BLACK, chess.parse_square(x[3:5])):
                    impure.append(k)
        s -= 20 * len(impure)
    unblocked = []
    if os.environ.get('SELFBLOCK') == '1':                 # the wanted mate must need the defence's self-block
        for k in WANT:
            m = names.get(k)
            if not m or len(m) != 1:
                continue
            if not self_block_needed(b, k, next(iter(m))):
                unblocked.append(k)
        s -= 20 * len(unblocked)
    checks = [b.san(m) for m in b.legal_moves if b.gives_check(m)]
    s -= 5 * len(checks) + 0.7 * len(b.piece_map())
    ok = not impure and not unblocked and len(t) == 1 and not bad and not holes and not duals and all(wok(names.get(k), w) for k, w in WANT.items()) and not dups
    return s + (100 if ok else 0), f"dups={dups} impure={impure} unblocked={unblocked} threat={sorted(t)} holes={holes} duals={duals} checks={checks} defs={ {k: sorted(v) for k, v in names.items()} }"


def mutate(fen):
    b = chess.Board(fen + ' b - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in CSQ]
    empty = [s for s in chess.SQUARES if not b.piece_at(s)]
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


def main(argv=None):
    a = argv or sys.argv[1:]
    configure(a[0], json.loads(a[2]), a[3])
    SEED, BUDGET = a[1], float(a[4]); random.seed(int(a[5]))
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


if __name__ == '__main__':
    main()
