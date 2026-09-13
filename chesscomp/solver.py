"""Search engine for orthodox #n, s#n, h#n.

Conventions
-----------
* A "white move" in direct/self problems is the attacker's move; Black defends.
* `forced(board, n, mode)`  : White to move, can White force the goal within n moves?
    direct: goal = Black checkmated
    self  : goal = White checkmated by Black (Black forced to give mate)
  Mates in fewer moves count (standard "within n").
* Helpmates: cooperative search; returns all solution lines.
"""
from __future__ import annotations
import time
import chess
import chess.polyglot

WHITE, BLACK = chess.WHITE, chess.BLACK


class Budget(Exception):
    pass


class Engine:
    def __init__(self, time_limit: float | None = None):
        self.tt: dict = {}
        self.nodes = 0
        self.deadline = time.time() + time_limit if time_limit else None

    # ------------------------------------------------------------ helpers
    def _tick(self):
        self.nodes += 1
        if self.deadline and (self.nodes & 1023) == 0 and time.time() > self.deadline:
            raise Budget()

    @staticmethod
    def ordered(board: chess.Board):
        """Checks and captures first - speeds up refutation/mate finding."""
        ms = list(board.legal_moves)
        ms.sort(key=lambda m: (not board.gives_check(m), not board.is_capture(m)))
        return ms

    def _key(self, board, n, mode):
        return (chess.polyglot.zobrist_hash(board), n, mode)

    # ------------------------------------------------------------ goal tests
    @staticmethod
    def goal_after_white(board, mode) -> bool | None:
        """Position after a White move (Black to move). True=goal reached, False=dead end, None=continue."""
        if mode == 'direct':
            if board.is_checkmate():
                return True
            if board.is_stalemate():
                return False
            return None
        else:  # self: White must not mate/stalemate Black
            if board.is_checkmate() or board.is_stalemate():
                return False
            return None

    @staticmethod
    def goal_after_black(board, mode) -> bool | None:
        """Position after a Black move (White to move)."""
        if mode == 'self':
            if board.is_checkmate():
                return True       # Black mated White: goal
            if board.is_stalemate():
                return False
            return None
        else:  # direct: Black mating White or stalemating White ends it badly for White
            if board.is_checkmate() or board.is_stalemate():
                return False
            return None

    # ------------------------------------------------------------ core recursion
    def forced(self, board: chess.Board, n: int, mode: str) -> bool:
        """White to move: can White force the goal within n White moves?"""
        if n <= 0:
            return False
        k = self._key(board, n, mode)
        if k in self.tt:
            return self.tt[k]
        res = False
        moves = self.ordered(board)
        if mode == 'direct' and n == 1:
            moves = [m for m in moves if board.gives_check(m)]
        for w in moves:
            self._tick()
            board.push(w)
            try:
                if self.black_fails(board, n, mode):
                    res = True
                    break
            finally:
                board.pop()
        self.tt[k] = res
        return res

    def black_fails(self, board: chess.Board, n: int, mode: str) -> bool:
        """Black to move after White's move number (remaining n counted incl. that move).
        True if every Black reply still leads to the goal."""
        g = self.goal_after_white(board, mode)
        if g is not None:
            return g
        if n <= 1 and mode == 'direct':
            return False
        for b in self.ordered(board):
            self._tick()
            board.push(b)
            try:
                gb = self.goal_after_black(board, mode)
                if gb is True:
                    continue
                if gb is False or not self.forced(board, n - 1, mode):
                    return False
            finally:
                board.pop()
        return True

    def refutations(self, board: chess.Board, n: int, mode: str, limit: int | None = None):
        """Board after a White first move. Return list of Black replies that refute it
        (None if the White move itself is a dead end, e.g. stalemate)."""
        g = self.goal_after_white(board, mode)
        if g is True:
            return []
        if g is False:
            return None
        refs = []
        for b in self.ordered(board):
            self._tick()
            board.push(b)
            try:
                gb = self.goal_after_black(board, mode)
                ok = gb is True or (gb is None and self.forced(board, n - 1, mode))
            finally:
                board.pop()
            if not ok:
                refs.append(b)
                if limit is not None and len(refs) > limit:
                    break
        return refs

    def continuations(self, board: chess.Board, n: int, mode: str):
        """White to move: all White moves that force the goal within n (the 'continuations')."""
        out = []
        moves = self.ordered(board)
        for w in moves:
            self._tick()
            board.push(w)
            try:
                if self.black_fails(board, n, mode):
                    out.append(w)
            finally:
                board.pop()
        return out

    # ------------------------------------------------------------ helpmates
    def help_solutions(self, board: chess.Board, plies: int, max_solutions: int = 50):
        """Cooperative: side to move starts; last ply is White's mating move."""
        sols, line = [], []
        dead = set()

        def rec(p):
            self._tick()
            if p == 0:
                return False
            key = (chess.polyglot.zobrist_hash(board), p)
            if key in dead:
                return False
            found = False
            moves = list(board.legal_moves)
            if p == 1:
                moves = [m for m in moves if board.gives_check(m)]
            for m in moves:
                board.push(m); line.append(m)
                try:
                    if p == 1:
                        if board.is_checkmate() and board.turn == BLACK:
                            sols.append(list(line)); found = True
                    elif not board.is_game_over():
                        if rec(p - 1):
                            found = True
                finally:
                    board.pop(); line.pop()
                if len(sols) >= max_solutions:
                    return found
            if not found:
                dead.add(key)
            return found

        rec(plies)
        return sols
