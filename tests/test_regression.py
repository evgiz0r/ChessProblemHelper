"""Regression: every diagram in knowledge/problems.json with a stored key must still solve to that key.

    pytest tests/test_regression.py        (about 5 s)
"""
import json, os, sys
import pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from chesscomp import Problem, analyse

DB = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'problems.json')
CASES = [p for p in json.load(open(DB, encoding='utf-8'))['problems'] if p.get('keys')]


@pytest.mark.parametrize('case', CASES, ids=[c['id'] for c in CASES])
def test_stored_key(case):
    res = analyse(Problem.from_fen(case['fen'], case['stip']), include_set=False, time_limit=120)
    assert res.get('keys') == case['keys'], f"{case['id']}: got {res.get('keys')}"
    assert res.get('cooked') == case.get('cooked', False)


def test_dual_avoidance_no_check_is_reported_before_captures():
    """E. Bourd s21: 2.Sxg3? after 1...Qxe5 gives no check (Bd4 still closes the c4-f4 battery); the
    reason must not be 'another unit captures the mating unit' just because a capture is Black's first
    legal move."""
    import chess
    from chesscomp.motives import dual_avoidance_after
    b = chess.Board('KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n w - - 0 1')
    r = dual_avoidance_after(b, chess.Move.from_uci('h3g2'))
    by = {v['defence']: v for v in r['variations']}
    k = by['Qxe5']['avoided'][0]['kind']
    assert k.startswith('no check') and 'Bd4' in k and 'Rc4' in k
    k2 = by['Bxe5']['avoided'][0]['kind']
    assert k2.startswith('no check') and 'Qf6' in k2


def test_stalemating_promotions_are_shown_as_tries():
    """E. Bourd s24: the wrong promotions of an underpromotion key must appear in the report."""
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    r = analyse(Problem.from_fen('8/2K1P3/3P4/3kP3/7R/3N4/8/5R2 w - - 0 1', '#2'), include_set=False)
    tries = {ph['first_move']['san']: ph for ph in r['phases'] if ph['type'] == 'try'}
    assert r['keys'] == ['e8=B']
    assert tries['e8=Q'].get('stalemate') and tries['e8=R'].get('stalemate')
    assert [x['san'] for x in tries['e8=S']['refutations']] == ['Ke6']


def test_corrections_marked_per_piece_and_promoted_force_flagged():
    """E. Bourd s27: mark the random move and its corrections; a correction must stop the random mate.
    Sf5/Sc2 keep Bf4# (duals), so they are random moves, not corrections. Three knights = promoted force."""
    from chesscomp.core import Problem, promoted_force
    from chesscomp.analysis import analyse
    from chesscomp.report import format_report
    import chess
    p = Problem.from_fen('8/KB3Q2/N2k4/3p4/pP1N4/4nN1b/3B2p1/2r3b1 w - - 0 1', '#2')
    res = analyse(p, max_refutations=1, include_tries=False)
    key = [ph for ph in res['phases'] if ph['type'] == 'key' and ph['first_move']['san'] == 'Ba8'][0]
    knight = [c for c in key['corrections'] if c['piece'] == 'Se3'][0]
    assert knight['random']['mate'] == 'Bf4#'
    assert set(knight['random']['moves']) == {'Sf5', 'Sc2', 'Sf1', 'Sd1'}
    assert [c['move'] for c in knight['corrections']] == ['Sg4', 'Sc4']
    assert promoted_force(chess.Board(p.board.fen())) == ['White has 3 knights']
    assert 'PROMOTED FORCE: White has 3 knights' in format_report(res)


def test_bourd_double_correction_report_lines():
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    from chesscomp.report import format_report
    p = Problem.from_fen('BQ2R3/3K4/2N5/1np2p2/2k2P2/p4R1b/4P3/3Nb3 w - - 0 1', '#2')
    out = format_report(analyse(p, max_refutations=1, include_tries=False))
    assert 'S~ random Sc7/Sa7/Sd6 2.Qb3#; corrections Sd4 2.Se5#, Sc3 2.Se3#' in out
    assert 'PROMOTED' not in out


def test_compact_report_groups_random_and_corrections():
    """E. Bourd s28: the full report was too verbose on the bench; the compact form is the solution as read."""
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    from chesscomp.report import format_compact
    p = Problem.from_fen('5b2/2N5/p7/5n2/K1kPp2p/1Np4q/2P5/3Q4 w - - 0 1', '#2')
    out = format_compact(analyse(p, max_refutations=1))
    assert 'COOKED: 2 keys: Sa5#, Qh5' in out
    assert 'S~ Sg7/Sh6/Sg3 2.Qd5#  |  Se7 2.Qc5#  |  Se3 2.Qe2#' in out
    assert '[duals] Sd6 2.Qd5#/Qc5#  Sxd4 2.Qd5#/Sa5#' in out
    assert 'Try 1.Qg1? (2.Sa5#/Qg8#) but Se3!' in out
    assert 'Set play differs: Se7 Sa5#->Qc5#' in out
    assert 'Patterns' not in out and 'Transferred' not in out
