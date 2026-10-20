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


def test_zag_reads_published_zagoruikos():
    from chesscomp.compose.trychange import zag_evaluate
    mv = chess.Move.from_uci
    # Rogoshin, Vratnica-64 2003, 2nd Prize: set d3 Qg7#, Kd3 Qf3#; 1.Qc8? d3 Qh8#, Kd3 Qh3# (d5!); 1.Qa6! Qa1#, Rb3#
    sc, summ = zag_evaluate(chess.Board('B7/1Q5K/1p1p4/1R6/2pp1P2/2k5/5R2/8 w - - 0 1'), None, '**', [mv('d4d3'), mv('c3d3')])
    assert summ.startswith('phases 3') and 'Qa6(Qa3#) Qa1# Rb3# ref KEY' in summ
    # Delobel, Problemesis 2004 (4x2, blocks): every try refuted by 1...d4, the same mate twice is never a phase
    sc, summ = zag_evaluate(chess.Board('8/7R/8/3p4/5pp1/1P2PPk1/Q1pR4/2K4B w - - 0 1'), None, '**', [mv('g4f3'), mv('f4e3')])
    assert summ.startswith('phases 4') and 'Qa8() Qg8# Qb8# ref KEY' in summ


def test_zag_capture_and_quiet_mate_on_one_square_are_one_mate():
    from chesscomp.compose.trychange import zag_evaluate
    mv = chess.Move.from_uci
    # Bxd4# after Sd4 and Bd4# after Sd6 are the same mate: no phase in which the two defences differ
    sc, summ = zag_evaluate(chess.Board('8/8/2r4R/1nB1k3/5Rp1/3b1Qp1/6P1/3K1n2 w - - 0 1'), None, '**', [mv('b5d4'), mv('b5d6')])
    assert 'Bxd4# Bd4#' not in summ


def test_zag_any_unit_finds_a_knight_key_phase():
    from chesscomp.compose.trychange import zag_evaluate
    mv = chess.Move.from_uci
    # Foster, The Problemist 2003-II, 3rd Prize: queen tries and the knight key, which brings its own mate (daily No. 15)
    sc, summ = zag_evaluate(chess.Board('7Q/2N5/1B1pp1K1/3Ppp2/3pkP2/5R2/4B3/8 w - - 0 1'), 'any', '**', [mv('d4d3'), mv('e5f4')])
    assert summ.startswith('phases 3 || Sb5() Sc3# Qxd4# ref KEY') and 'Qa4# Qxe6#' in summ
