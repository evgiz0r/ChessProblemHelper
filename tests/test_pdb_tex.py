"""PDB LaTeX export -> db records (tools/pdb_tex.py)."""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import pdb_tex

BLOCK = r'''\begin{diagram}
% PDB-ID: P1376474
% Genre: 2#
\author{Bourd, Evgeni; Grinblat, Arieh}
\source{Rochade Europa}
\sourcenr{2280}
\year{2004}
\award{2. ehrende Erwähnung}
\pieces{wKc8, wDf8, wTe1b5, wLh1a1, wSb1e4, wBd2h3g5f5d6, sKf4, sSf7, sBf3c4}
%\fen{2K2Q2/5n2/3P4/1R3PP1/2p1Nk2/5p1P/3P4/BN2R2B}
\stip{\#2}
\solution{1. Sb1-c3! droht 2. Se4-g3\# \newline 1. \dots  Sf7xd6 2. Df8xd6\# \newline 1. \dots  Sf7-e5 2. Lh1xf3\#\newline }
\end{diagram}'''


def test_record():
    (r,) = pdb_tex.parse(BLOCK)
    assert r['id'] == 'pdb-P1376474' and r['stip'] == '#2' and r['count'] == '13+4'
    assert r['author'] == 'Evgeni Bourd; Arieh Grinblat'
    assert r['source'] == 'Rochade Europa 2280 2004\n2. HM'
    assert r['orthodox'] and r['fen'] == '2K2Q2/5n2/3P4/1R3PP1/2p1Nk2/5p1P/3P4/BN2R2B'


def test_solution_notation():
    (r,) = pdb_tex.parse(BLOCK)
    # the key keeps its disambiguation (two knights reach c3); the rest is short algebraic, S for knight
    assert r['solution'].split('\n') == ['1.Sbc3! threat 2.Sg3#', '1...Sxd6 2.Qxd6#', '1...Se5 2.Bxf3#']
