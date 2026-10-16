import chess
from chesscomp.compose.type3 import evaluate

KEY, MP = chess.Move.from_uci('d2e2'), chess.D1


def test_specific_defence_scores_above_random_knights():
    # claude-type3-queen-lines: 1.Ke2! (2.Qd4#) Sd7 Qd5# (set Qg4#), Se1-c2/f3/d3 Qd3# (set Qf3#)
    sc, summ = evaluate(chess.Board('2B5/8/2N2n2/8/2P1k3/1p2P3/3K4/1R1Qn1N1 w - - 0 1'), KEY, MP)
    assert summ.startswith("keys ['Ke2']") and "good ['e1:3/3', 'f6:1/1']" in summ and 'duals 0' in summ
    # the scheme stage: every move of the f6 knight defends (Bh8 opens to d4)
    sc0, summ0 = evaluate(chess.Board('7b/8/5n2/R7/4k3/1p2P3/3K4/1R1Qn1N1 w - - 0 1'), KEY, MP)
    assert "'f6:5/7'" in summ0 and sc > sc0


def test_pawn_selector_with_a_threat_off_the_queen_lines():
    # claude-type3-pawn-g5: 1.g5! (2.Sd3#) Rxc8 Qf4# (set Qg5#), Sb4 Qd4# (set Qe7#)
    b = chess.Board('2B2r2/8/2n3p1/1NNpk3/6PQ/5pK1/8/8 w - - 0 1')
    k, mp = chess.Move.from_uci('g4g5'), chess.H4
    sc, summ = evaluate(b, k, mp, noqthr=True)
    assert summ.startswith("keys ['g5']") and "thr ['c5d3']" in summ and "good ['c6:1/1', 'f8:1/2']" in summ
    assert "'f8" not in evaluate(b, k, mp, noqthr=True, quiet=True)[1]     # 1...Rxc8 is a capture


def test_pawny_charges_officers():
    b = chess.Board('2B2r2/8/2n3p1/1NNpk3/6PQ/5pK1/8/8 w - - 0 1')
    k, mp = chess.Move.from_uci('g4g5'), chess.H4
    assert evaluate(b, k, mp, noqthr=True)[0] - evaluate(b, k, mp, noqthr=True, pawny=3)[0] == 3 * 6   # Q B S S r s


def test_keysq_keeps_only_the_named_key_mates():
    # bourd-type3-pawn-g4: 1.g4! (2.Sd2#) Rc7 Qf3#, Sb3 Qd3#
    b = chess.Board('1B6/5r2/1N6/1Kn3p1/2Npk3/6PQ/4P3/8 w - - 0 1')
    k, mp = chess.Move.from_uci('g3g4'), chess.H3
    full = evaluate(b, k, mp, noqthr=True)[1]
    assert "'c5:1/1'" in full and "'f7:1/" in full
    only_d3 = evaluate(b, k, mp, noqthr=True, keysq={chess.D3})[1]
    assert "'c5:1/1'" in only_d3 and "'f7" not in only_d3
    assert evaluate(b, k, mp, thrsq=chess.F3)[0] < evaluate(b, k, mp)[0]      # the threat is Sd2#, not on f3


def test_mutate_option_drops_the_no_threat_penalty():
    # claude-type3-c5-flights-scheme: 1.c5 is a zugzwang key
    b = chess.Board('3N4/8/2RB1p2/1Q5K/1nP1k3/2R5/2P1N3/8 w - - 0 1')
    k, mp = chess.Move.from_uci('c4c5'), chess.B5
    plain, mut = evaluate(b, k, mp), evaluate(b, k, mp, mutate=True)
    assert "good ['b4:5/6', 'f6:1/1']" in plain[1] and not plain[1].startswith('keys')
    # without the penalty the full key check runs and finds the waiting-move cooks
    assert mut[1].startswith("keys ['Bf4', 'Bxb4', 'Qf5+', 'Rh3', 'Rg3', 'c5']")


def test_any_piece_by_move_recognises_the_strebkovs_swap():
    # Strebkovs 2003 (psis-c1d0392e2e): 1.Sb3! Bxc5 Qxc5#, Bd4 Rxd4# (set Sc7#, e4#): one bishop makes both defences
    b = chess.Board('b1Q1N3/5p2/5K2/N1PkP3/1n4R1/8/1n2P3/6b1 w - - 0 1')
    sc, summ = evaluate(b, chess.Move.from_uci('a5b3'), None, bymove=True)
    assert summ.startswith("keys ['Nb3']") and "good ['g1:2/2']" in summ
