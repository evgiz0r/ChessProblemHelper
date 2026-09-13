import sys, time, itertools, chess
sys.path.insert(0,'/home/claude/chesscomp')
from chesscomp import *
from chesscomp.compose.scheme_search import mates_after
PT={'Q':chess.QUEEN,'R':chess.ROOK,'B':chess.BISHOP,'S':chess.KNIGHT,'P':chess.PAWN}

def solves(b, mv):
    """cheap: after White's move mv, does White mate in 1 against EVERY Black reply?"""
    t=b.copy(); t.push(mv)
    if t.is_checkmate() or t.is_stalemate(): return False
    if not t.legal_moves: return False
    for d in list(t.legal_moves):
        t.push(d)
        dead=(t.is_game_over() and not t.is_checkmate()) or not mates_after(t)
        t.pop()
        if dead: return False
    return True

def threatens(b, mv):
    t=b.copy(); t.push(mv); t.push(chess.Move.null())
    return bool(mates_after(t))

def king_profile(b):
    """For each White king move: does it solve / merely threaten?"""
    k=b.king(chess.WHITE)
    sol, thr = [], []
    for m in list(b.legal_moves):
        if m.from_square!=k: continue
        if solves(b,m): sol.append(m)
        elif threatens(b,m): thr.append(m)
    return sol, thr

def unique_solution(b, mv):
    """mv is the only White move that solves - and no White move mates at once (a short mate cooks a #2)."""
    for m in list(b.legal_moves):
        t = b.copy(); t.push(m)
        if t.is_checkmate():
            return False
        if m != mv and solves(b, m):
            return False
    return True

def blocks_white_line(b, frm, to):
    """Does moving the White king from `frm` to `to` cut a White line piece off from squares beyond?"""
    cut = []
    for sq in chess.SquareSet(b.occupied_co[chess.WHITE]):
        if sq == frm or b.piece_type_at(sq) not in (chess.QUEEN, chess.ROOK, chess.BISHOP): continue
        t = b.copy(); t.remove_piece_at(frm)
        before = set(t.attacks(sq))
        t.set_piece_at(to, chess.Piece(chess.KING, True))
        after = set(t.attacks(sq))
        lost = before - after
        if lost:
            cut.append((chess.square_name(sq), sorted(chess.square_name(x) for x in lost)))
    return cut
