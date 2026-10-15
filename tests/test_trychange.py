import chess
from chesscomp.compose.trychange import evaluate, phase_rows

# Grimshaw on e6 (15 Oct 2026): bK c5, bR e8, bB g8, threat Qd6# from g6 or h6 through e6.
FEN = '4r1b1/Np1R2Q1/2p5/2k5/1R6/P7/4P3/K7 w - - 0 1'
DEFS = [chess.Move.from_uci('e8e6'), chess.Move.from_uci('g8e6')]


def test_queen_posts_change_both_grimshaw_mates():
    rows = {r['move']: r['defs'] for r in phase_rows(chess.Board(FEN), chess.G7, 'Qd6#', DEFS, {'g7g6', 'g7h6'})}
    assert rows['Qh6'] == [('Qc1#',), ('Qe3#',)]
    assert rows['Qg6'] == [('Qc2#',), ('Qg1#',)]


def test_pair_found_and_mate_in_one_penalised():
    sc, summ = evaluate(chess.Board(FEN), chess.G7, 'Qd6#', DEFS, {'g7g6', 'g7h6'})
    assert summ == 'Qh6 thr1 Qc1# Qe3# h0 || Qg6 thr1 Qc2# Qg1# h0'
    assert sc < 10                       # the diagram has 1.Qd4#: the queen on g7 reaches the guarded d4


def test_setkey_finds_the_check_cooks():
    from chesscomp.compose.trychange import setkey_evaluate
    sc, summ = setkey_evaluate(chess.Board(FEN), chess.G7, 'Qd6#', DEFS, {'g7g6', 'g7h6'})
    assert "Qc3+" in summ and "Qg1+" in summ and sc < 0      # 1.Qc3+ Bc4 2.Qxc4#, 1.Qg1+ Re3 2.Qxe3#


def test_posts_three_keys_when_the_c6_knight_guards_d4():
    from chesscomp.compose.trychange import posts_evaluate
    b = chess.Board('4r1b1/3R2Q1/ppn5/1pk5/1R6/KP4N1/8/8 w - - 0 1')
    sc, summ = posts_evaluate(b, chess.G7, 'Qd6#', DEFS, {'g7f6', 'g7g6', 'g7h6'})
    assert summ.count('ref KEY') == 3 and 'Qc1#' in summ and 'Qc2#' in summ and 'Qc3#' in summ
