"""Free-threat post-key search (chesscomp.compose.freethreat) and line-closing skeletons (line_skeletons)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import chess
from chesscomp.compose import freethreat
from chesscomp.compose.line_skeletons import skeletons


def test_knight_line_closing_post_key_scores_as_finished():
    # 12 Oct 2026: 1...Sg2 closes Bh1's diagonal (2.Qe4#), 1...Sc2 closes Rc1's file (2.Sxc3#); threat 2.Se3#
    freethreat.configure('4Q3/8/8/3k4/8/8/8/1Nr1nN1b', {'Nc2': 'N*c3', 'Ng2': 'Qe8e4'})
    sc, info = freethreat.score('4Q3/2K5/8/3k4/2R5/1Pp5/8/1Nr1nN1b')
    assert sc > 100, info
    assert "threat=['Nf1e3']" in info and 'holes=[]' in info


def test_skeleton_e1_knight_found():
    sk = [(t, o, a1, a2) for t, o, a1, a2, _ in skeletons(chess.D5, chess.E3)]
    assert (chess.E3, chess.E1, chess.C2, chess.G2) in sk
    assert all(chess.D5 not in (a1, a2) for _, _, a1, a2 in sk)


def test_knight_pair_escape_check():
    # 1...Rd1 (rook c1, T d4) is an escape no self-block on the king's field stops; Rf6-f4 is stopped by a pawn on e4
    from chesscomp.compose.knight_pair_skeletons import escapes, F
    k, T = chess.D5, chess.D4
    occ = {k, chess.E3, T}
    assert chess.D1 in escapes('R', chess.C1, T, occ, F(k) - {T})
    assert escapes('R', chess.F6, T, occ, F(k) - {T}) == []


def test_self_block_needed():
    # Strebkovs (Vratnica-64 2003): after 1.Sb3, 1...Sc4 2.e4# and 1...Bc6 2.Sc7# both need the self-block
    b = chess.Board('b1Q1N3/5p2/5K2/2PkP3/1n4R1/1N6/1n2P3/6b1 b - - 0 1')
    assert freethreat.self_block_needed(b, 'Nc4', 'Pe2e4')
    assert freethreat.self_block_needed(b, 'Bc6', 'Ne8c7')


def test_capturing_the_blocker_is_no_self_block():
    b = chess.Board('3N4/8/3p4/1K1k4/3P3R/2Q1n2N/5B2/7b b - - 0 1')
    assert not freethreat.self_block_needed(b, 'Nc4', 'Qc3c4')
    assert freethreat.self_block_needed(b, 'Be4', 'Nh3f4')


def test_self_block_needs_the_king_on_the_square():
    """1...Sxc4 2.Qd3#: without the knight the rook a4 interposes on d4, but the king cannot go to c4 (Qd3 guards it)."""
    b = chess.Board('5B2/8/1P6/1P1knK2/r1N5/2Q5/8/8 b - - 0 1')
    assert not freethreat.self_block_needed(b, 'Nxc4', 'Qc3d3')
    assert freethreat.self_block_needed(b, 'Rxc4', 'Qc3e5')
