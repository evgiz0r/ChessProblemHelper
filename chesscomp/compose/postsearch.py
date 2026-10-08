"""Local search on a POST-KEY position (E. Bourd, 8 Oct 2026: the threat first, then the mates): the threat is fixed,
the named defences must each get one mate, all different, with no holes and no duals; the core never moves.

    python3 -m chesscomp.compose.postsearch CORE SEED THREAT_IDS DEFS BUDGET_S RNG
    e.g. CORE=3R4/8/8/8/4k3/r7/3PP3/b1Q5 THREAT_IDS=Qc1c6 DEFS=Rc3,Bc3
"""
import sys, os, random, time, chess
from chesscomp.compose.keyfind import post_spec, move_id
from chesscomp.core import Problem
from chesscomp.analysis import analyse
READY = os.environ.get('READY', '0') == '1'   # also minimise White's other real mates in two (key readiness)


def other_solutions(fen, threat):
    """White first moves that force mate although the threat no longer mates after them (E. Bourd: waiting moves
    that keep the threat are the solution being sound, not cooks)."""
    try:
        keys = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), include_tries=False, include_set=False, time_limit=8).get('keys') or []
    except Exception:
        return 99
    n = 0
    for san in keys:
        b = chess.Board(fen + ' w - - 0 1')
        try:
            m = b.parse_san(san.replace('S', 'N'))
        except ValueError:
            n += 1; continue
        if move_id(b, m) in threat:
            continue
        b.push(m)
        if not b.is_check():
            b.push(chess.Move.null())
            if any(move_id(b, x) in threat and (b.push(x) or True) and (b.is_checkmate(), b.pop())[0] for x in list(b.legal_moves)):
                continue
        n += 1
    return n
CORE = sys.argv[1]; SEED = sys.argv[2]; THREAT = set(sys.argv[3].split(','))
DEFS = sys.argv[4].split(','); BUDGET = float(sys.argv[5]); random.seed(int(sys.argv[6]))
core = chess.Board(CORE + ' b - - 0 1'); CSQ = {s: core.piece_at(s) for s in chess.SQUARES if core.piece_at(s)}
def promoted(b):
    w = lambda t: len(b.pieces(t, chess.WHITE))
    if w(chess.QUEEN) > 1 or w(chess.ROOK) > 2 or w(chess.KNIGHT) > 2: return True
    bs = list(b.pieces(chess.BISHOP, chess.WHITE))
    return len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2)
def score(fen):
    b = chess.Board(fen + ' b - - 0 1')
    if not b.is_valid() or promoted(b): return -1e9, ''
    w = chess.Board(fen + ' w - - 0 1')
    if not w.is_valid(): return -1e9, ''
    t, d = post_spec(fen)
    s = 0.0
    s -= 15 * len(t - THREAT) + 25 * len(THREAT - t)
    names = {b.san(chess.Move.from_uci(u)): m for u, m in d.items()}
    holes = [k for k, m in names.items() if not m]; duals = [k for k, m in names.items() if len(m) > 1]
    s -= 6 * len(holes) + 4 * len(duals)
    mates = []
    for dd in DEFS:
        m = names.get(dd)
        if m is None: s -= 20; continue                       # not a defence (threat still mates)
        if len(m) == 1: s += 10; mates.append(next(iter(m)))
        else: s -= 5
    if len(mates) == len(DEFS) and len(set(mates)) == len(mates): s += 15
    s -= 0.7 * len(b.piece_map())
    ok = t == THREAT and not holes and not duals and len(mates) == len(DEFS) and len(set(mates)) == len(DEFS)
    extra = ''
    if ok and READY:
        o = other_solutions(fen, THREAT); s -= 8 * o; extra = f' others={o}'
    return s + (100 if ok else 0), f"holes={holes} duals={duals} {dict((k, sorted(names.get(k, []))) for k in DEFS)}{extra}"
def mutate(fen):
    b = chess.Board(fen + ' b - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in CSQ]
    empty = [s for s in chess.SQUARES if not b.piece_at(s)]
    op = random.random()
    if op < .35:
        sym = random.choice('NBRPPpppnbr'); sq = random.choice(empty)
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7): return fen
        b.set_piece_at(sq, chess.Piece.from_symbol(sym))
    elif op < .55 and free:
        s = random.choice(free)
        if b.piece_type_at(s) != chess.KING: b.remove_piece_at(s)
    elif free:
        s = random.choice(free); p = b.piece_at(s); b.remove_piece_at(s); b.set_piece_at(random.choice(empty), p)
    return b.board_fen()
t0 = time.time(); pop = [(score(SEED)[0], SEED)]; seen = {SEED}
best = pop[0]
while time.time() - t0 < BUDGET:
    pop.sort(key=lambda x: -x[0]); pop = pop[:12]
    par = random.choice(pop[:5])[1]; ch = par
    for _ in range(random.choice((1, 1, 2))): ch = mutate(ch)
    if ch in seen: continue
    seen.add(ch); sc, info = score(ch); pop.append((sc, ch))
    if sc > 100 and (not READY or sc > best[0]): best = (sc, ch); print('HIT', round(sc, 1), ch, info, flush=True)
pop.sort(key=lambda x: -x[0])
for sc, f in pop[:3]: print('TOP', round(sc, 1), f, score(f)[1])
print('evaluated', len(seen))
