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
