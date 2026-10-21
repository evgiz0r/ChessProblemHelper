"""unmask_search retypes non-core units (E. Bourd, 21 Oct 2026: "pieces like b1 b7 can be changed to other pieces")."""
import random
import chess
from chesscomp.compose import unmask_search as us

SEED = '6N1/1rp2B2/1p1R2P1/4B1K1/1R1NkP1p/3n1p2/2P2P2/1n6'
CORE = '6N1/8/3R4/8/1R1NkP2/3n1p2/2P2P2/8'


def test_retype_keeps_square_and_never_touches_core_or_kings():
    us.setup(['x', CORE, SEED, 'd6', 'f6', 'a1', '{}', '1', '7'])
    random.seed(7)
    base = chess.BaseBoard(SEED)
    retyped = set()
    for _ in range(3000):
        b = chess.BaseBoard(us.mutate(SEED))
        for sq, p in us.CSQ.items():
            assert b.piece_at(sq) == p                         # the core never changes
        assert b.king(chess.WHITE) is not None and b.king(chess.BLACK) is not None
        for sq in chess.SQUARES:
            p = b.piece_at(sq)
            if p and p.piece_type == chess.PAWN:
                assert chess.square_rank(sq) not in (0, 7)
        if b.piece_map().keys() == base.piece_map().keys():
            retyped |= {(chess.square_name(s), b.piece_at(s).symbol()) for s in b.piece_map() if b.piece_at(s) != base.piece_at(s)}
    assert len({sym for sq, sym in retyped if sq == 'b1'}) >= 6  # the black knight b1 becomes other pieces
    assert any(sym.isupper() for sq, sym in retyped if sq == 'b7')  # and a black unit can turn White


def test_white_pawn_weight_costs():
    us.setup(['x', CORE, SEED, 'd6', 'f6', 'a1', '{}', '1', '7'])
    us.PAWNW = 0.0
    s0 = us.post_score(SEED)[0]
    us.PAWNW = 3.0
    try:
        assert us.post_score(SEED)[0] == s0 - 3.0 * len(chess.BaseBoard(SEED).pieces(chess.PAWN, chess.WHITE))
    finally:
        us.PAWNW = 0.0
