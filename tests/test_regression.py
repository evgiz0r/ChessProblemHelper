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
