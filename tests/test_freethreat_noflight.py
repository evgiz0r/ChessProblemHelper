"""compose.freethreat with NOFLIGHT=1 rejects a post-key where the black king can still move (E. Bourd, 13 Oct 2026:
"something without king flight, its a bit limiting in general")."""
import os
from chesscomp.compose import freethreat as f


def test_noflight_flags_the_given_flight(monkeypatch):
    monkeypatch.setenv('NOFLIGHT', '1')
    f.configure('8/8/8/8/4k3/3n4/2r5/1B6', {'Nf4': 'Q*c4', 'Rc5': 'Q*g4'}, 'b1')
    s, info = f.score('6Q1/3NN3/7B/8/1p2k3/3n2K1/2rP4/1B6')   # claude-halfpin-rs-qg8 post-key, 1...Kd4 2.Qd5#
    assert "flights=['Kd4']" in info and s < 100, info
    monkeypatch.delenv('NOFLIGHT')
    s2, info2 = f.score('6Q1/3NN3/7B/8/1p2k3/3n2K1/2rP4/1B6')
    assert 'flights=[]' in info2 and s2 >= 100, info2
