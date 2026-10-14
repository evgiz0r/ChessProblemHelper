"""E. Bourd (14 Oct 2026), on 1.Bc7-d8! in bourd-halfpin-ss-bd8: "key is slightly less flawed here, as we have a set
mate, and the bishop seems to guard e5 as well". The attacked-key-piece finding names the set mates that need the key
piece on its diagram square (not those where its guard is doubled) and the captures of it left without a set mate."""
import chess
from chesscomp import Problem
from chesscomp.analysis import analyse
from chesscomp.critique import critique, key_piece_set_roles, key_piece_captures_unprovided

FEN = 'b3R1N1/Q1B5/5Ppp/R2nnkN1/6pP/1K1P2P1/1P6/4r3 w - - 0 1'


def test_set_role_of_attacked_key_piece():
    p = Problem.from_fen(FEN, '#2')
    res = analyse(p, max_refutations=1)
    key = chess.Move.from_uci('c7d8')
    roles = key_piece_set_roles(p.board, key, res['phases'])
    assert set(roles) == {'Rxe5#'}               # Qf2# is not listed: there Re8 also guards e5
    assert len(roles['Rxe5#']) == 7               # 1...R~ along the first rank
    assert key_piece_captures_unprovided(p.board, key, res['phases']) == ['Sxc7']
    msg = [f['msg'] for f in critique(p, res, necessity=False)['findings'] if f['rule'] == 'attacked key piece'][0]
    assert 'milder' in msg and 'Rxe5#' in msg and 'Sxc7' in msg
