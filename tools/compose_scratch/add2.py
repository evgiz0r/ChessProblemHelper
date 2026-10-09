import chess, sys, itertools
from add1 import ok, base, WANT
C3 = chess.C3
near = [s for s in chess.SQUARES if chess.square_distance(s, C3) <= 2 and not base.piece_at(s)]
units = [(s, sym) for s in near for sym in 'RBNPprbn' if not (sym in 'Pp' and chess.square_rank(s) in (0, 7))]
res = []
for (s1, a), (s2, b) in itertools.combinations(units, 2):
    if s1 == s2 or C3 in (s1, s2): continue
    x = base.copy(); x.set_piece_at(s1, chess.Piece.from_symbol(a)); x.set_piece_at(s2, chess.Piece.from_symbol(b))
    if x.is_attacked_by(chess.WHITE, C3): continue
    d = ok(x)
    if d is not None:
        res.append((d, a + chess.square_name(s1), b + chess.square_name(s2), x.board_fen())); print(res[-1], flush=True)
