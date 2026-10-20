"""freethreat THREAT= (20 Oct 2026): a fixed threat is rewarded, any other threat is penalised."""
from chesscomp.compose import freethreat as ft

POST = '8/7K/4P3/3bbR2/8/p3p1pN/R1P1k1P1/1Q3N2'


def test_fixed_threat_is_scored():
    ft.configure('8/8/8/3bbR2/8/4p2N/R1P1k3/1Q6', {'Bf3': 'Pc2c3', 'Bf4': 'Pc2c4'})
    ft.THREAT = None
    free, _ = ft.score(POST)
    ft.THREAT = 'Nh3g1'
    right, info = ft.score(POST)
    ft.THREAT = 'Qb1e1'
    wrong, _ = ft.score(POST)
    ft.THREAT = None
    assert right == free and right > 100 and "threat=['Nh3g1']" in info
    assert wrong < right - 100
