"""effects: errors of a Black move, with what is shared between defences (E. Bourd's scheme C, 8 Oct 2026)."""
from chesscomp.compose.effects import effects

POST = '8/4K3/2p5/2rpk3/1Qb2R2/2np2P1/8/7B'


def test_knight_to_e4_self_blocks_and_closes_lines():
    e = effects(POST, 'Ne4')
    assert any(x.startswith('self-block e4') for x in e)
    assert any('closes a line of wBh1' in x and 'd5' in x for x in e)
    assert any('opens a line of wQb4: now reaches e1,d2' in x for x in e)


def test_both_knight_moves_open_the_same_diagonal():
    assert 'opens a line of wQb4: now reaches e1,d2' in effects(POST, 'Nb5')
