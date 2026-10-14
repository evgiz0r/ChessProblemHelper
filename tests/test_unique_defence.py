"""E. Bourd (14 Oct 2026): a knight defence is thematic only when it is the knight's ONLY defence; in
claude-changed-type1-qg8 every move of the d4 knight that stops 2.Qb8 gets the same mate."""
from chesscomp import Problem
from chesscomp.analysis import analyse
from chesscomp.compose.unique_defence import extra_defences


def _phase(fen, san):
    r = analyse(Problem.from_fen(fen + ' w - - 0 1', '#2'), max_refutations=1)
    return [p for p in r['phases'] if p['type'] in ('key', 'try') and p['first_move']['san'] == san][0]


def test_random_knight_defences_are_not_unique():
    ex = extra_defences(_phase('8/3BB3/5NQ1/4k1Pp/2pn4/2n1P3/8/7K', 'Qg8'), ['Se6', 'Sd5'])
    assert set(ex['Se6']) == {'Sc6', 'Sf5', 'Sdb5'} and set(ex['Sd5']) == {'Scb5', 'Se4'}


def test_unique_knight_defences():
    # 1.Qg8 (2.Sg4#): only Se6 cuts the queen's guard of d5, only Se4 cuts Bd3's guard of f5
    ex = extra_defences(_phase('8/2pK4/5NQ1/4k1P1/3n3p/2nBP3/8/8', 'Qg8'), ['Se6', 'Se4'])
    assert ex == {'Se6': [], 'Se4': []}
