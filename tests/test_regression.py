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


def test_idle_key_piece_is_flagged():
    """E. Bourd, session 29: 1.Rf1 from h1 brings a piece out of play into the game; his own 1.Re7 is not
    flagged (the rook was not idle in that sense and its tries are the content)."""
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    from chesscomp.critique import critique
    def rules(fen):
        p = Problem.from_fen(fen + ' w - - 0 1', '#2')
        return {f['rule'] for f in critique(p, analyse(p), necessity=False)['findings']}
    assert 'idle key piece' in rules('1r2k3/1N1p3p/7n/8/8/B7/Q1B1K3/7R')
    assert 'idle key piece' not in rules('3R4/4b3/K7/1Np2n2/2kPp2p/B1p4q/2P5/3Q4')


def test_compact_report_shows_changes_under_try():
    """E. Bourd, session 29: the short solution must name the changes, not only the full report."""
    from chesscomp.core import Problem
    from chesscomp.analysis import analyse
    from chesscomp.report import format_compact
    p = Problem.from_fen('2B5/2p1N3/3k4/3NpK2/8/3pQ3/3P4/8 w - - 0 1', '#2')
    out = format_compact(analyse(p))
    assert 'changed: c5 Qxe5#->Qh6#, c6 Sc8#->Sf5#' in out
    assert 'Set play also: c5 2.Qxe5#/Qh6# [dual]' in out


def test_separator_finds_try_key_pair():
    """The dual separator finds 1.Be6 / 1.Ke4 in his pawn-step problem and nothing before the e5 pawn."""
    from chesscomp.compose.separate import table, pairs
    _, prs = pairs(table('2B5/2p1N3/3k4/3NpK2/8/3pQ3/3P4/8', ['c6', 'c5']), ['c6', 'c5'])
    assert [(a, b) for a, b, *_ in prs] == [('Be6', 'Ke4')]
    _, prs = pairs(table('2B5/2p1N3/3k4/3N1K2/8/4Q3/8/8', ['c6', 'c5']), ['c6', 'c5'])
    assert prs == []


def test_keepkill_finds_his_e5_pawn():
    """E. Bourd, session 29: the black pawn e5 killed the rival queen mates and kept 2.Qh6#; the tool ranks it first."""
    from chesscomp.compose.keepkill import search, parse_phase
    hits = search('2B5/2p1N3/3k4/3N1K2/8/4Q3/8/8', [parse_phase('Ke4: c6=Sf5 c5=Qh6'), parse_phase('Be6: c6=Sc8 c5=Qe5')])
    assert hits[0][1] == 'bPe5'
