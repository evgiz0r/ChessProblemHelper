"""Type-1 changed mates geometry (E. Bourd's type 1, 14 Oct 2026: one White piece, the queen, mates in both phases
on another line; each Black defender guards one mating square of each phase and frees both by moving).

Two findings it encodes:
- With the queen switching between two whole LINES, a rook and a bishop can never be the two defenders (king in the
  centre or anywhere: `line_pairs(K, 'RB')` is empty). A bishop's pair is two light edge squares of the field (c4/d3/
  d5/e4 for Kd4), a rook's pair needs a corner square on a rank or file; they never split one-and-one over two lines.
  A defender standing at the corner of its two squares (Rd4 for Ke5 guarding e4 and d5) keeps one guard on every move.
- It works when the queen's two POSTS reach different sets of field squares (`post_pairs`): for Kd4 one-step keys
  Qc7-b7 and Qg3-g2, longer ones Qa3-a8, Qc1-h1, Qg3-g8. The threats a bishop defender can parry are knight checks
  (every knight check on a dark-square king comes from a light square; contact checks on light squares are the pair
  squares themselves): `threats` lists them, with each defender's off-line defending moves and the on-line squares
  beyond its pair that a plug must close.

    python -m chesscomp.compose.type1_geometry d4 --types RB --maxkey 1
"""
from __future__ import annotations
import argparse
import itertools
import chess

SYM = {'R': chess.ROOK, 'B': chess.BISHOP, 'N': chess.KNIGHT, 'P': chess.PAWN, 'Q': chess.QUEEN}
WQ = chess.Piece(chess.QUEEN, chess.WHITE)
n = chess.square_name


def _board(king, units=()):
    b = chess.Board(None)
    b.set_piece_at(king, chess.Piece(chess.KING, chess.BLACK))
    for sq, p in units:
        b.set_piece_at(sq, p)
    return b


def _field(king):
    return set(chess.SquareSet(chess.BB_KING_ATTACKS[king]))


def _lines():
    out = set()
    for s in chess.SQUARES:
        for df, dr in ((1, 0), (0, 1), (1, 1), (1, -1)):
            f, r = chess.square_file(s), chess.square_rank(s)
            if 0 <= f - df < 8 and 0 <= r - dr < 8:
                continue
            sq, ff, rr = [], f, r
            while 0 <= ff < 8 and 0 <= rr < 8:
                sq.append(chess.square(ff, rr)); ff += df; rr += dr
            if len(sq) >= 3:
                out.add((tuple(sq), 'R' if df == 0 or dr == 0 else 'B'))
    return out


def line_pairs(king, types='RB'):
    """Queen line pairs (A, B) with disjoint field squares and two defenders, one of each type in `types` (or two of
    the same when types is one letter repeated), each on a line holding exactly one A-square and one B-square."""
    king = chess.parse_square(king) if isinstance(king, str) else king
    adj = _field(king)
    L = [l for l in _lines() if king not in l[0]]
    Q = [l for l in L if len([s for s in l[0] if s in adj]) >= 2]
    out = []
    for (A, _), (B, _) in itertools.permutations(Q, 2):
        mA, mB = {s for s in A if s in adj}, {s for s in B if s in adj}
        if mA & mB:
            continue
        defs = {}
        for D, t in L:
            if D in (A, B) or t not in types:
                continue
            on = [s for s in D if s in adj]
            a, b = [s for s in on if s in mA], [s for s in on if s in mB]
            if len(a) == 1 and len(b) == 1:
                defs.setdefault(t, []).append((a[0], b[0]))
        t1, t2 = types[0], types[-1]
        for d1 in defs.get(t1, []):
            for d2 in defs.get(t2, []):
                if not {d1[0], d1[1]} & {d2[0], d2[1]}:
                    out.append((n(A[0]) + '-' + n(A[-1]), n(B[0]) + '-' + n(B[-1]), t1, d1, t2, d2))
    return out


def _reach(king, post, units=()):
    b = _board(king, [(post, WQ)] + list(units))
    return {s for s in b.attacks(post) if s in _field(king)}


def post_pairs(king, types='RB', maxkey=7):
    """Queen posts PA -> PB (a queen move of at most `maxkey` squares) whose reach sets are disjoint, with two
    defenders (types from `types`, never two bishops or two knights) each guarding exactly one square of each reach,
    on one line through it for a rook or bishop. Each result: dict pa, pb, defenders [(type, sq, a_sq, b_sq)], left
    (reach squares no defender holds: they need another Black guard or a block)."""
    king = chess.parse_square(king) if isinstance(king, str) else king
    adj = _field(king)
    ok = [P for P in chess.SQUARES if P != king and P not in adj and king not in _board(king, [(P, WQ)]).attacks(P)]
    out = []
    for PA in ok:
        for PB in _board(king, [(PA, WQ)]).attacks(PA):
            if PB not in ok or chess.square_distance(PA, PB) > maxkey:
                continue
            RA0, RB0 = _reach(king, PA), _reach(king, PB)
            if RA0 & RB0 or len(RA0) < 2 or len(RB0) < 2:
                continue
            cands = []
            for sq in chess.SQUARES:
                if sq in (king, PA, PB) or sq in adj:
                    continue
                for t in types:
                    if t == 'P' and chess.square_rank(sq) in (0, 7):
                        continue
                    g = {s for s in _board(king, [(sq, chess.Piece(SYM[t], chess.BLACK))]).attacks(sq) if s in adj}
                    a, b = g & RA0, g & RB0
                    if len(a) != 1 or len(b) != 1:
                        continue
                    x, y = next(iter(a)), next(iter(b))
                    if t in 'RBQ' and not (chess.between(sq, y) & chess.BB_SQUARES[x] or chess.between(sq, x) & chess.BB_SQUARES[y]):
                        continue
                    cands.append((t, sq, x, y))
            for d1, d2 in itertools.combinations(cands, 2):
                if {d1[2], d1[3]} & {d2[2], d2[3]} or d1[1] == d2[1] or (d1[0] == d2[0] and d1[0] in 'BN'):
                    continue
                units = [(d[1], chess.Piece(SYM[d[0]], chess.BLACK)) for d in (d1, d2)]
                RA, RB = _reach(king, PA, units), _reach(king, PB, units)
                if not {d1[2], d2[2]} <= RA or not {d1[3], d2[3]} <= RB:
                    continue
                b = _board(king, units)
                if not all(s in b.attacks(d[1]) for d in (d1, d2) for s in (d[2], d[3])):
                    continue
                if any(d[1] in _board(king, [(P, WQ)] + units).attacks(P) for P in (PA, PB) for d in (d1, d2)):
                    continue                                  # the queen would attack a defender
                out.append({'pa': PA, 'pb': PB, 'defenders': [d1, d2],
                            'left': sorted((RA | RB) - {d1[2], d1[3], d2[2], d2[3]})})
    return out


def threats(king, pair):
    """For one post pair, white threat units X (knight anywhere; bishop, rook or pawn with a contact check) that guard
    a field square F the queen covers from PB but not from PA (the key frees X: E. Bourd's 1.Qc7! engine), with a
    checking move to T that no defender guards after the key. Each defender must have at least one off-line move
    guarding T and no move inside its pair line doing so; on-line moves beyond the pair are reported as plugs."""
    king = chess.parse_square(king) if isinstance(king, str) else king
    adj = _field(king)
    PA, PB, D = pair['pa'], pair['pb'], pair['defenders']
    base = [(d[1], chess.Piece(SYM[d[0]], chess.BLACK)) for d in D]
    covA = {s for s in _board(king, base + [(PA, WQ)]).attacks(PA) if s in adj}
    covB = {s for s in _board(king, base + [(PB, WQ)]).attacks(PB) if s in adj}
    pairsq = {d[2] for d in D} | {d[3] for d in D}
    out = []
    for xt in 'NBRP':
        for xs in chess.SQUARES:
            if xs in adj or xs in (king, PA, PB) or any(xs == d[1] for d in D):
                continue
            if xt == 'P' and chess.square_rank(xs) in (0, 7):
                continue
            b = _board(king, base + [(PB, WQ), (xs, chess.Piece(SYM[xt], chess.WHITE))])
            if king in b.attacks(xs) or not all(d[2] in b.attacks(d[1]) and d[3] in b.attacks(d[1]) for d in D):
                continue
            bA = _board(king, base + [(PA, WQ), (xs, chess.Piece(SYM[xt], chess.WHITE))])
            if not {d[2] for d in D} <= set(bA.attacks(PA)) or not {d[3] for d in D} <= set(b.attacks(PB)):
                continue
            F = {s for s in b.attacks(xs) if s in covB - covA}
            if not F:
                continue
            b.turn = chess.WHITE
            for m in b.pseudo_legal_moves:
                if m.from_square != xs or m.promotion:
                    continue
                bb = b.copy(); bb.push(m)
                T = m.to_square
                if not bb.is_check() or T in pairsq or (xt in 'BR' and T not in adj):
                    continue
                rows = []
                for d in D:
                    if T in b.attacks(d[1]):
                        break
                    b2 = b.copy(); b2.turn = chess.BLACK
                    offs, beyond, inside = [], [], []
                    far = max(chess.square_distance(d[1], d[2]), chess.square_distance(d[1], d[3]))
                    for mv in b2.pseudo_legal_moves:
                        if mv.from_square != d[1]:
                            continue
                        b3 = b2.copy(); b3.push(mv)
                        if not (T in b3.attacks(mv.to_square) or mv.to_square == T):
                            continue
                        keeps = d[2] in b3.attacks(mv.to_square) or d[3] in b3.attacks(mv.to_square)
                        if not keeps and mv.to_square not in adj:
                            offs.append(b2.san(mv))
                        elif keeps and chess.square_distance(d[1], mv.to_square) > far:
                            beyond.append(b2.san(mv))
                        elif keeps:
                            inside.append(b2.san(mv))
                    if not offs or inside:
                        break
                    rows.append((offs, beyond))
                else:
                    out.append({'x': xt + n(xs), 'f': sorted(n(s) for s in F), 't': n(T), 'defences': rows})
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    ap.add_argument('king')
    ap.add_argument('--types', default='RB')
    ap.add_argument('--maxkey', type=int, default=7)
    a = ap.parse_args()
    lp = line_pairs(a.king, a.types if len(a.types) == 2 else a.types * 2)
    print(f'queen line pairs with {a.types} defenders on lines: {len(lp)}')
    for p in post_pairs(a.king, a.types, a.maxkey):
        th = threats(a.king, p)
        if not th:
            continue
        ds = ' '.join(f'{t}{n(sq)}({n(x)},{n(y)})' for t, sq, x, y in p['defenders'])
        print(f"Q{n(p['pa'])}-{n(p['pb'])} {ds} left {','.join(n(s) for s in p['left'])}")
        for t in th:
            dd = ' | '.join('/'.join(o) + (' plug:' + ','.join(bd) if bd else '') for o, bd in t['defences'])
            print(f"   threat {t['x']}-{t['t']} (frees {','.join(t['f'])}): {dd}")


if __name__ == '__main__':
    main()
