"""setplay_search scores a battery's set play: each named holder defence answered by its own discharge only (18 Oct 2026)."""
import chesscomp.compose.setplay_search as sp


def test_queen_holder_set_play_scores_ok():
    sp.WANT = {'Qxe1': 'b3e3', 'Qxf8': 'b3b6'}
    s, info = sp.score('5B2/8/K7/N1bk4/3N4/1R6/B4q2/Q3R3')
    assert s > 50, info


def test_double_check_mate_is_marked():
    sp.WANT = {'Nxe3': 'c3e3'}
    b = __import__('chess').Board('8/b7/6Q1/3rk3/8/2R1P1P1/1B6/3n1K2 b - - 0 1')
    b.push_san('Nxe3')
    assert 'c3e3+' in sp.mates_in_one(b)          # Rxe3 is a double check (rook on the e-file, bishop b2)


def test_holder_mode_lists_two_different_discharges():
    import chess
    sp.HOLDER = chess.C2
    sp.WANT = ['e3*', 'e3*']
    try:
        s, info = sp.score('8/8/2P1k1K1/R7/8/Q3B3/2n5/4R3')     # Sd4 2.Bxd4#, Sb4 2.Bf4# (a degenerate hit, but two mates)
        assert 'e3d4' in info and 'e3f4' in info, info
    finally:
        sp.HOLDER = None


def test_mutate_on_a_full_board_returns_the_position():
    """18 Oct 2026: from an invalid seed (a white knight giving check) the walk accepted every candidate until the
    board was full and mutate crashed on an empty choice."""
    from chesscomp.compose import setplay_search as S
    full = 'pRKPbBrp/NPPpPpbN/pRNpkPPb/PBPpQPnP/PRQRNBrQ/BRnrPpBb/PPBQrprP/rbQNRPpR'
    assert S.mutate(full) == full


def test_norecap_rejects_a_mate_on_the_holder_square():
    """Holder rook c7: 1...Rc4 2.Sxc4# and 1...Rc8 2.Sxc8# capture the holder; with NORECAP they do not count."""
    import importlib, os
    from chesscomp.compose import setplay_search as S
    fen = '8/2r5/RN2kPK1/4p3/8/8/3R4/8'
    os.environ['HOLDER'] = 'c7'; os.environ['NORECAP'] = '0'
    importlib.reload(S); S.WANT = ['b6c4', 'b6c8']
    assert S.score(fen)[0] > 100
    os.environ['NORECAP'] = '1'
    importlib.reload(S); S.WANT = ['b6c4', 'b6c8']
    assert S.score(fen)[0] < 100
    del os.environ['HOLDER'], os.environ['NORECAP']
    importlib.reload(S)
