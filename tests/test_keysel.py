import chess
from chesscomp.compose.keysel import evaluate, keys

M = chess.Move.from_uci
ARGS = (chess.D5, M('c5c4'), M('d1d4'), M('d8d4'))


def test_scheme_has_one_key_and_the_change():
    # claude-type2-d4-scheme: set 1...c4 2.Rd4#, 1.Sc7! (2.Qd3#) c4 2.Qd4#; 1.Se7? Rd7!
    b = chess.Board('3Q1R2/1r6/8/2pNN3/4kP2/2P5/8/3RK3 w - - 0 1')
    sc, summ = evaluate(b, *ARGS)
    assert summ.startswith("keys ['Nc7']") and "thr ['d8d3']" in summ and sc > 0


def test_without_the_rook_every_knight_move_solves():
    b = chess.Board('3Q1R2/8/8/2pNN3/4kP2/2P5/8/3RK3 w - - 0 1')
    assert {b.san(k) for k in keys(b)} >= {'Nc7', 'Ne7', 'Nb6'}


def test_critique_counts_a_double_threat_stopper_as_needed():
    from chesscomp import Problem
    from chesscomp.analysis import analyse
    from chesscomp.critique import piece_necessity
    p = Problem.from_fen('8/8/2PQ1Br1/2KNP3/4k1P1/2pppR2/3qn1P1/8 w - - 0 1', '#2')
    r = analyse(p, max_refutations=1, include_tries=True, include_set=True, time_limit=30)
    assert piece_necessity(p, r)['c6'].startswith('needed (stops the double threat')


def test_landings_that_cut_a_line_are_not_a_random_move():
    # E. Bourd (16 Oct 2026): "its not a random move" - 1...Sd4/Sc3 2.Rf6# both cut Ba1-f6; with the knight simply
    # removed Rf6+ is met by Bxf6, so the shared mate comes from the arrival, not from the departure.
    from chesscomp import Problem
    from chesscomp.analysis import analyse
    r = analyse(Problem.from_fen('8/2pK4/6R1/5kpP/4Np2/3NRB2/4n3/b5r1 w - - 0 1', '#2'), include_set=True, time_limit=60)
    sp = next(ph for ph in r['phases'] if ph['type'] == 'set')
    assert not sp['corrections']
    # a real random move stays random (daily No. 2: the bishop's departure from d4 gives Qg4#)
    r2 = analyse(Problem.from_fen('3R4/8/6K1/4P3/3bk3/N1p3Q1/8/8 w - - 0 1', '#2'), include_set=True, time_limit=60)
    key = next(ph for ph in r2['phases'] if ph['type'] == 'key')
    assert key['corrections'] and key['corrections'][0]['random']['mate'] == 'Qg4#'


def test_moves_that_defend_by_arrival_are_not_a_random_move():
    # E. Bourd (17 Oct 2026, his bench mvcop42d): "the solution random move again is somewhat bad" - after 1.Sd2!
    # (2.Bf3#) the queen's removal leaves Bf3# mating, so 1...Qb5 (cuts Ra5-f5) and 1...Qxb8 (takes the f4 guard)
    # are specific defences even though the battery mates work with the queen removed.
    from chesscomp import Problem
    from chesscomp.analysis import analyse
    r = analyse(Problem.from_fen('1B4nK/4p1rp/2B1PP1R/R5p1/2p1N1kp/1qPP2p1/4PpP1/3Qbr2 w - - 0 1', '#2'),
                include_set=False, time_limit=60)
    key = next(ph for ph in r['phases'] if ph['type'] == 'key')
    assert key['first_move']['san'] == 'Sd2' and not key['corrections']


def test_a_unit_that_stops_solution_duals_is_not_set_play_only():
    # claude-type3-queen-lines: wSg1 protects f3 for the set mates and, after 1.Ke2!, shuts Qh1# out of 1...Sd3/Sc2
    from chesscomp import Problem
    from chesscomp.analysis import analyse
    from chesscomp.critique import piece_necessity, critique
    p = Problem.from_fen('2B5/8/2N2n2/8/2P1k3/1p2P3/3K4/1R1Qn1N1 w - - 0 1', '#2')
    r = analyse(p, max_refutations=1, include_tries=True, include_set=True, time_limit=30)
    assert piece_necessity(p, r)['g1'].startswith('needed (stops the dual(s) 1...S')
    rules = {f['rule'] for f in critique(p, r)['findings']}
    assert 'set-play-only unit' not in rules and 'set play + dual stopper' in rules
