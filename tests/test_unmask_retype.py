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


def test_loose_ignores_duals_of_unnamed_defences():
    # his bench scheme: random mask moves Bd6/Bf4 allow both double checks; only Bxc7/Bg3 are named
    post = '2n2N1K/2RB1PB1/p4R2/1p2b1p1/1P1k2P1/qpN4Q/4pPn1/4r3'
    us.setup(['x', '5N2/2RB2B1/5R2/4b3/3k4/7Q/8/8', post, 'd7', 'e6', 'a8',
              '{"Bxc7": "Rf6f4", "Bg3": "Rf6d6"}', '1', '7'])
    us.LOOSE = False
    strict = us.post_score(post)[2]
    us.LOOSE = True
    try:
        loose = us.post_score(post)[2]
    finally:
        us.LOOSE = False
    assert "duals=[]" not in strict and "duals=[]" in loose


def test_allowcheck_passes_a_check_answered_by_mate():
    # Black unpins White (23 Oct 2026): Ba1 pins Qc3 to Kh8, 1...Bxc3+ is answered by 2.Sxc3#
    post = '7K/8/3N3R/1B1k4/5P2/2Q2n2/8/bN4B1'
    us.setup(['x', '7K/8/8/3k4/8/2Q2n2/8/b7', post, 'c3', 'c7', 'a1',
              '{"Ne5": "Qc3c5", "Nd4": "Qc3c4"}', '1', '7'])
    us.ALLOWCHECK = False
    assert us.post_score(post)[1] is False
    us.ALLOWCHECK = True
    try:
        assert us.post_score(post)[1] is True
    finally:
        us.ALLOWCHECK = False


def test_allowcheck_diagram_needs_a_set_mate():
    # 1.Bb5! diagram: 1...Bxc3+ has no set mate (Sxc3+ Kc6), so it stays a diagram check
    d = chess.Board('7K/8/3N3R/3k4/5P2/2Q2n2/8/bN3BB1 b - - 0 1')
    m = d.parse_san('Bxc3+')
    assert us.mated_after(d, m) is False
    p = chess.Board('7K/8/3N3R/1B1k4/5P2/2Q2n2/8/bN4B1 b - - 0 1')
    assert us.mated_after(p, p.parse_san('Bxc3+')) is True
