from chesscomp.compose.rerefute import rerefute


def test_finds_his_bg6_regard():
    # E. Bourd's bench, 15 Oct 2026: 1.Qf7? Bxf3! becomes 1.Qf7? Rf5! with the f3 pawn replaced by a bishop on g6
    hits = rerefute('q7/2p1Q1p1/2b5/r1r4p/p1Pk4/3NNP2/3K4/8', 'e7e6', 'e7f7', ['c5', 'c6', 'a5', 'a8'], ['c6d5', 'c5d5'])
    assert [(c, r) for c, r, _ in hits] == [('-Pf3 +Bg6', 'Rf5')]


def test_lighten_finds_his_queen_removal():
    from chesscomp.compose.rerefute import lighten
    hits = lighten('q7/2p1Q1p1/2b3B1/r1r4p/p1Pk4/3NN3/3K4/8', 'e7e6', 'e7f7', ['c6d5', 'c5d5'], keep=['c5', 'c6', 'd4'])
    assert [c for _, c, _ in hits] == ['-qa8 -ph5 +Pg4']
