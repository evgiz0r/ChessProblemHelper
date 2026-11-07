"""What a move changes (tools/move_delta.py): each false mate of the 6 Nov solving round must show up in the delta.

    pytest tests/test_move_delta.py
"""
import os, sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools'))
import chess
import move_delta as md

P1 = '3N1r1B/3R4/2P2q2/1K1pnp2/3k1p2/3B2p1/3PQ3/8'      # Novice Composers TT 2002 (the session-3 sight test)
P4 = '8/2p1Q1p1/2b3B1/r1r5/p1Pk2P1/3NN3/3K4/8'           # E. Bourd, bourd-grimshaw-d5-7x7


def test_defence_opens_the_rook_behind():
    # 1.Qe6 Rxc4 2.Qe5+? Rxe5: leaving c5 opens a5-e5
    _, d, _ = md.deltas(P4 + ' w - - 0 1', ['Qe6', 'Rxc4', 'Qe5'])
    assert chess.E5 in d['opens'][chess.A5]
    assert d['captured'] == chess.C4


def test_mating_piece_drops_the_guard_of_d3():
    # 1...Qf7 2.Qxe5+? Kxd3: the queen leaving e2 leaves the bishop d3 unprotected
    _, m = md.deltas(P1 + ' b - - 0 1', ['Qf7', 'Qxe5'])
    assert chess.D3 in m['side_loses'] and chess.D3 in m['flights_gained']
    assert 'no White unit covers any more' in md.text(m) and 'd3(B)' in md.text(m)


def test_bishop_sliding_on_its_line_keeps_e4():
    # 1...Bb7 2.Qe4+? Bxe4: the bishop still guards e4 through d5
    d, _ = md.deltas(P4 + ' b - - 0 1', ['Bb7', 'Qe4'])
    assert chess.E4 in d['keeps'] and chess.E4 not in d['drops']


def test_unpinning_interposition():
    # after the key 1.Bxf5, 1...Qd6 interposes on the d-file and frees d5 (2.Qd3#)
    _, d = md.deltas(P1 + ' w - - 0 1', ['Bxf5', 'Qd6'])
    assert chess.D5 in d['unpins']
    assert 'no longer pinned: bPd5' in md.text(d)


def test_svg_draws_the_opened_line():
    _, d, _ = md.deltas(P4 + ' w - - 0 1', ['Qe6', 'Rxc4', 'Qe5'])
    s = md.svg(d)
    assert s.count('<line') >= 2 and 'marker-end="url(#hg)"' in s
