"""Random light #2 sampler (21 Nov 2026, chat "a simple mate in 2, pretty and quick").

    python -m chesscomp.compose.light_sampler SEED SECONDS OUT [--min-mates 2]

Draws random light positions (black king on c3-f6, White K+Q and 2-3 of R/B/B/N/N/P/P anywhere, 1-3 Black units of
p/p/p/n/b/r within two squares of the king), keeps those where the king has no move, Black is not stalemated and White
has no mate in one, then looks for a unique quiet key (no check, no capture). Each sound quiet position is written as
one line: D<distinct single mates> NK<of them after a non-king move> DU<defences with duals> FEN | key | threat | play.
Sort the file with `sort -r` and read the D3+ lines first; then solve with report --critique and the gate.

Why it exists: for a light simple problem, evolve (FLIGHT, SELFBLOCK and CORR modes from bare and seeded cores) and
keyfind returned only checking keys or cooks in 40 minutes; four 4-minute sampler jobs (about 8M positions, 13k boxed,
730 sound with a quiet key) gave three D3 lines, one of them claude-quick-qc6-pawns. It finds placements, never a
mechanism: use it for a quick light problem, not for a theme.
"""
import sys, random, time
import chess
from ..solver import Engine
from ..core import illegal_position, promoted_force

KSQ = [chess.square(f, r) for f in range(2, 6) for r in range(2, 6)]
WEXTRA = 'RBBNNPP'
BEXTRA = 'pppnbr'


def _near(sq, d):
    return [s for s in chess.SQUARES if chess.square_distance(s, sq) <= d]


def generate(rng):
    b = chess.Board(None)
    bk = rng.choice(KSQ)
    b.set_piece_at(bk, chess.Piece(chess.KING, chess.BLACK))
    free = lambda: [s for s in chess.SQUARES if b.piece_at(s) is None]
    wk = rng.choice([s for s in free() if chess.square_distance(s, bk) > 1])
    b.set_piece_at(wk, chess.Piece(chess.KING, chess.WHITE))
    for p in ['Q'] + rng.sample(WEXTRA, rng.choice([2, 2, 3])):
        sqs = free()
        if p == 'P':
            sqs = [s for s in sqs if 1 <= chess.square_rank(s) <= 6]
        b.set_piece_at(rng.choice(sqs), chess.Piece.from_symbol(p))
    for p in rng.sample(BEXTRA, rng.choice([1, 2, 2, 3])):
        sqs = [s for s in _near(bk, 2) if b.piece_at(s) is None]
        if p == 'p':
            sqs = [s for s in sqs if 1 <= chess.square_rank(s) <= 6]
        if not sqs:
            return None
        b.set_piece_at(rng.choice(sqs), chess.Piece.from_symbol(p))
    b.turn = chess.WHITE
    return b


def boxed(b):
    """Legal, king without a move, Black not stalemated in the set play."""
    if b.is_check() or not b.is_valid():
        return False
    bb = b.copy(); bb.turn = chess.BLACK
    if bb.is_check() or not bb.is_valid():
        return False
    ksq = bb.king(chess.BLACK)
    moves = list(bb.legal_moves)
    return bool(moves) and not any(m.from_square == ksq for m in moves)


def mates_in_one(b):
    out = []
    for w in list(b.legal_moves):
        if b.gives_check(w):
            b.push(w)
            mate = b.is_checkmate()
            b.pop()
            if mate:
                out.append(w)
    return out


def examine(b):
    """None, or (D, NK, DU, line) for a diagram with a unique quiet key."""
    try:
        if illegal_position(b) or promoted_force(b):
            return None
    except Exception:
        return None
    if mates_in_one(b):
        return None
    eng = Engine(5)
    keys = []
    try:
        for w in eng.ordered(b):
            b.push(w)
            r = eng.refutations(b, 2, 'direct', limit=0)
            b.pop()
            if r == []:
                keys.append(w)
                if len(keys) > 1:
                    return None
    except Exception:
        return None
    if len(keys) != 1 or b.gives_check(keys[0]) or b.is_capture(keys[0]):
        return None
    k = keys[0]
    key_san = b.san(k)
    b.push(k)
    nb = b.copy(); nb.push(chess.Move.null())
    threat = [] if nb.is_check() else [m.uci() for m in mates_in_one(nb)]
    var = []
    for d in list(b.legal_moves):
        d_san = b.san(d)
        is_king = d.from_square == b.king(chess.BLACK)
        b.push(d)
        ms = [m.uci() for m in mates_in_one(b)]
        b.pop()
        if threat and set(ms) & set(threat):
            continue          # the threat still mates: not a defence
        var.append((d_san, is_king, ms))
    b.pop()
    if len(threat) > 1:
        return None           # double threat
    single = [v for v in var if len(v[2]) == 1]
    duals = [v for v in var if len(v[2]) > 1]
    nonking = [v for v in single if not v[1]]
    dist = {v[2][0] for v in single}
    line = (f"D{len(dist)} NK{len(nonking)} DU{len(duals)} {b.fen().split(' ')[0]} | key {key_san} threat {threat} | "
            + ' '.join(f"{v[0]}:{v[2]}" for v in var))
    return len(dist), len(nonking), len(duals), line


def main(argv):
    seed, secs, out = int(argv[0]), float(argv[1]), argv[2]
    min_mates = int(argv[argv.index('--min-mates') + 1]) if '--min-mates' in argv else 2
    rng = random.Random(seed)
    t0 = time.time(); n = nb = ns = 0
    with open(out, 'w') as f:
        while time.time() - t0 < secs:
            b = generate(rng); n += 1
            if b is None or not boxed(b):
                continue
            nb += 1
            r = examine(b)
            if r is None:
                continue
            ns += 1
            if r[0] >= min_mates:
                f.write(r[3] + '\n'); f.flush()
    print(f'seed {seed}: {n} generated, {nb} boxed, {ns} sound with a quiet key', file=sys.stderr)


if __name__ == '__main__':
    main(sys.argv[1:])
