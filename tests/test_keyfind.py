"""keyfind: it must recognise E. Bourd's 1.Be4! (three captures on e4) as a sound, sacrificial key."""
import chess
from chesscomp.compose.keyfind import solve_one, post_spec, retractions

POST = '1K6/8/8/p1N2Qnp/1b1kB3/3P1bN1/1PPn1P2/7q'


def test_post_spec_reads_three_defences():
    threat, defs = post_spec(POST)
    assert threat == {'Qf5d5'} and len(defs) == 3


def test_retraction_b7_is_sound_sacrifice():
    pre = next(p for p, k in retractions(chess.Board(POST + ' b - - 0 1')) if k.uci() == 'b7e4')
    r = solve_one((pre.fen(), 'b7e4', None))
    assert r[0] == 'ok' and r[2] == 'Be4' and 'sacrifice' in r[3][1]


def test_king_retraction_is_cooked():
    pre = next(p for p, k in retractions(chess.Board(POST + ' b - - 0 1')) if k.uci() == 'c8b8')
    assert solve_one((pre.fen(), 'c8b8', None))[0] == 'cooked'


def test_newunit_finds_the_clearance_key():
    import subprocess, sys
    r = subprocess.run([sys.executable, '-m', 'chesscomp.compose.keyfind', '8/4K3/2p5/2rpk3/1Qbp1RP1/2np4/6N1/8',
                        '--newunit', '--jobs', '2', '--top', '5'], capture_output=True, text=True, timeout=600)
    assert '1.Ra6!' in r.stdout
