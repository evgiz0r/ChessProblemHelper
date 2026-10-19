"""Le Grand search (daily No. 14, 19 Oct 2026): a hill climb scored by python-chess alone, no solver.

Le Grand: a try 1.T? threatens 2.A#, and after a defence d 2.B# mates; the key 1.K! threatens 2.B#, and after the
same d 2.A# mates. The score looks for an ordered pair of quiet White first moves with single, different threats and a
Black move d that swaps them; then it wants the key sound and unique, the try refuted (one refutation is best).
It only tests checking moves for mates, so a position costs a few milliseconds where the solver costs seconds
(evolve ran at one position a second on this theme). Solve every HIT with chesscomp.report and the gate.

    CORE=8/8/8/8/4k3/8/8/8 SEED=8/8/8/8/4k3/8/2N5/K2Q4 BUDGET_S=600 \\
        python -m chesscomp.compose.legrand JOB OUTFILE

CORE: units that never move or disappear. SEED: the start (contains CORE). MAXU: most units (default 13).
DEFK=1: the thematic d must be a king move (Le Grand by flight); DEFK=0 (default) takes any Black move and gives
a bonus to a non-king one. FLIGHT=0 (default 1) refuses diagram flights without a set mate; with FLIGHT=1 a provided
flight is allowed and a set mate after d that differs from A and B scores extra (a third mate: Le Grand plus a change).
SAME=1 gives a bonus when the try and the key are moves of one White unit. NPAIR=2 asks for two Le Grand defences.
"""
from __future__ import annotations
from chesscomp.core import illegal_position as _illegal
import os, random, sys, time
import chess

TYPES_W = [chess.QUEEN, chess.ROOK, chess.ROOK, chess.BISHOP, chess.BISHOP, chess.KNIGHT, chess.KNIGHT, chess.PAWN, chess.PAWN]
TYPES_B = [chess.ROOK, chess.BISHOP, chess.KNIGHT, chess.PAWN, chess.PAWN]


def san(b, m):
    return b.san(m).replace('N', 'S').rstrip('#+')


def mates(b):
    """White to move: the mates, testing checking moves only. A mate is named by its piece and arrival square
    (Qf5, Pe8=S), not its departure: Qh5-f5 in the try and Qf1-f5 in the key are the same mate."""
    out = []
    for m in list(b.legal_moves):
        if not b.gives_check(m):
            continue
        b.push(m)
        if b.is_checkmate():
            out.append(b.piece_at(m.to_square).symbol().upper() + chess.square_name(m.to_square)
                       + ('=' + chess.piece_symbol(m.promotion).upper() if m.promotion else ''))
        b.pop()
    return sorted(set(out))


def promoted(b):
    if _illegal(b):
        return True
    for col in (chess.WHITE, chess.BLACK):
        if len(b.pieces(chess.QUEEN, col)) > 1 or len(b.pieces(chess.ROOK, col)) > 2 or len(b.pieces(chess.KNIGHT, col)) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def legal(b):
    if not b.is_valid() or b.is_check() or promoted(b):
        return False
    n = b.copy(); n.push(chess.Move.null())
    return not n.is_check()


def threat(b):
    """Black to move after White's first move: White's mates if Black passes (None if Black is in check)."""
    if b.is_check():
        return None
    b.push(chess.Move.null())
    t = mates(b)
    b.pop()
    return t


def phase(b, m):
    """White plays m: (threats, {black uci: mates}, refutations)."""
    b.push(m)
    t = threat(b)
    dm, refs = {}, []
    for d in list(b.legal_moves):
        b.push(d)
        mm = mates(b)
        b.pop()
        dm[d.uci()] = mm
        if not mm:
            refs.append(d.uci())
    b.pop()
    return t, dm, refs


def set_play(b):
    n = b.copy(); n.push(chess.Move.null())
    out = {}
    for d in list(n.legal_moves):
        n.push(d); out[d.uci()] = mates(n); n.pop()
    return out


DEFK = os.environ.get('DEFK', '0') == '1'
FLIGHT = os.environ.get('FLIGHT', '1') == '1'
SAME = os.environ.get('SAME', '0') == '1'
NPAIR = int(os.environ.get('NPAIR', '1'))


def evaluate(b):
    """(score, summary, hit)."""
    if mates(b):
        return -1e9, 'mate in one', False
    k = b.king(chess.BLACK)
    sp = set_play(b)
    flights = [d for d in sp if chess.Move.from_uci(d).from_square == k]
    unprov = sum(1 for d in flights if not sp[d]) + (0 if FLIGHT else 10 * len(flights))
    cands = []
    for m in list(b.legal_moves):
        if b.gives_check(m):
            continue
        b.push(m); t = threat(b); b.pop()
        if t and len(t) == 1:
            cands.append(m)
    if len(cands) < 2:
        return -100 + 10 * len(cands) - 10 * unprov, 'few threats', False
    ph = {m: phase(b, m) for m in cands}
    best, bsum, bhit = -1e9, '', False
    for K in cands:
        tk, dk, rk = ph[K]
        for T in cands:
            tt, dt, rt = ph[T]
            if T == K or tt == tk:
                continue
            A, B = tt[0], tk[0]
            lg = []
            part = 0
            for d in set(dt) & set(dk):
                a = dt[d] == [B]; c = dk[d] == [A]
                part = max(part, 5 * (B in dt[d]) + 5 * (A in dk[d]) + 3 * a + 3 * c)
                if a and c and (not DEFK or chess.Move.from_uci(d).from_square == k):
                    lg.append(d)
            s = part + 30 * min(len(lg), NPAIR)
            s -= 6 * min(len(rk), 6)
            s -= 2 * max(0, len(rt) - 1) + (8 if not rt else 0)
            if lg:
                kingd = [d for d in lg if chess.Move.from_uci(d).from_square == k]
                if len(kingd) < len(lg) and not DEFK:
                    s += 6
                for d in lg:
                    if FLIGHT and d in sp and sp[d] and A not in sp[d] and B not in sp[d]:
                        s += 8
                        break
            if SAME and K.from_square == T.from_square:
                s += 6
            if b.is_capture(K):
                s -= 10
            s -= 15 * unprov
            hit = False
            if lg and len(lg) >= NPAIR and not rk and rt and not unprov and not b.is_capture(K):
                hit = unique_key(b, K, ph)
                s += 40 if hit else -5
            if s > best:
                best, bhit = s, hit
                bsum = (f'try {san(b, T)}? ({A}) refs={len(rt)} key {san(b, K)}! ({B}) refs={len(rk)} LG={lg}'
                        + (' setmate=' + ','.join(sp[lg[0]]) if lg and lg[0] in sp else ''))
    units = len(b.piece_map())
    return best - 0.8 * max(0, units - 10), bsum, bhit


def unique_key(b, K, ph):
    for m in list(b.legal_moves):
        if m == K:
            continue
        r = ph.get(m)
        if r is None:
            r = phase(b, m)
        if not r[2]:
            return False
    return True


def mutate(b, core, maxu):
    b = b.copy()
    free = [sq for sq, p in b.piece_map().items() if sq not in core and p.piece_type != chess.KING]
    empty = [sq for sq in chess.SQUARES if not b.piece_at(sq)]
    op = random.random()
    if op < 0.3 and len(b.piece_map()) < maxu:
        col = random.random() < 0.6
        t = random.choice(TYPES_W if col else TYPES_B)
        sq = random.choice(empty)
        if t == chess.PAWN and chess.square_rank(sq) in (0, 7):
            return b
        b.set_piece_at(sq, chess.Piece(t, col))
    elif op < 0.5 and free:
        b.remove_piece_at(random.choice(free))
    elif op < 0.75:
        movable = free + [sq for sq, p in b.piece_map().items() if p.piece_type == chess.KING and p.color == chess.WHITE and sq not in core]
        if not movable:
            return b
        sq = random.choice(movable); p = b.piece_at(sq); to = random.choice(empty)
        if p.piece_type == chess.PAWN and chess.square_rank(to) in (0, 7):
            return b
        b.remove_piece_at(sq); b.set_piece_at(to, p)
    elif free:
        sq = random.choice(free); p = b.piece_at(sq)
        f, r = chess.square_file(sq), chess.square_rank(sq)
        nb = [chess.square(f + x, r + y) for x in (-1, 0, 1) for y in (-1, 0, 1)
              if (x or y) and 0 <= f + x < 8 and 0 <= r + y < 8 and not b.piece_at(chess.square(f + x, r + y))]
        if nb:
            to = random.choice(nb)
            if not (p.piece_type == chess.PAWN and chess.square_rank(to) in (0, 7)):
                b.remove_piece_at(sq); b.set_piece_at(to, p)
    return b


def main():
    job = int(sys.argv[1]) if len(sys.argv) > 1 else 0
    out = sys.argv[2] if len(sys.argv) > 2 else f'legrand_{job}.txt'
    random.seed(int(os.environ.get('RNG', job)))
    core_b = chess.Board(os.environ.get('CORE', '8/8/8/8/4k3/8/8/8') + ' w - - 0 1')
    core = set(core_b.piece_map())
    seed = chess.Board(os.environ.get('SEED', core_b.board_fen()) + ' w - - 0 1')
    if seed.king(chess.WHITE) is None:
        for sq in (chess.A1, chess.H1, chess.A8, chess.H8):
            if not seed.piece_at(sq):
                seed.set_piece_at(sq, chess.Piece(chess.KING, chess.WHITE)); break
    maxu = int(os.environ.get('MAXU', '13'))
    budget = float(os.environ.get('BUDGET_S', '600'))
    t0 = time.time()
    cur = seed; cs = evaluate(cur)[0] if legal(cur) else -1e9
    seen, n, hits, last = set(), 0, set(), time.time()
    while time.time() - t0 < budget:
        c = mutate(cur, core, maxu)
        if random.random() < 0.3:
            c = mutate(c, core, maxu)
        key = c.board_fen()
        if key in seen or not legal(c):
            if random.random() < 0.01:
                cur, cs = seed, -1e9
            continue
        seen.add(key); n += 1
        s, summ, hit = evaluate(c)
        if hit and key not in hits:
            hits.add(key)
            with open(out, 'a') as f:
                f.write(f'HIT {s:.1f} | {key} | {summ}\n')
        if s >= cs or random.random() < 0.02:
            cur, cs = c, s
        if n % 500 == 0 or time.time() - last > 30:
            last = time.time()
            print(f'-- {time.time() - t0:.0f}s {n} best {cs:.1f} | {cur.board_fen()} | {summ}', flush=True)
        if n % 3000 == 0 and cs < 0:
            cur, cs = seed, -1e9


if __name__ == '__main__':
    main()
