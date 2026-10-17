"""Core data model: positions, stipulations, album-style notation."""
from __future__ import annotations
import re
from dataclasses import dataclass, field
import chess

PIECE_LETTER = {chess.KING: 'K', chess.QUEEN: 'Q', chess.ROOK: 'R',
                chess.BISHOP: 'B', chess.KNIGHT: 'S', chess.PAWN: ''}
LETTER_PIECE = {'K': chess.KING, 'Q': chess.QUEEN, 'R': chess.ROOK,
                'B': chess.BISHOP, 'S': chess.KNIGHT, 'N': chess.KNIGHT, 'P': chess.PAWN}


@dataclass
class Stipulation:
    kind: str            # 'direct' | 'help' | 'self'
    moves: float         # 2, 3, 2.5 ...
    text: str = ''

    @property
    def full_moves(self) -> int:
        return int(self.moves)

    @property
    def half(self) -> bool:          # h#2.5 etc: White starts
        return self.moves != int(self.moves)

    @staticmethod
    def parse(s: str) -> 'Stipulation':
        t = s.strip().lower().replace(' ', '')
        m = re.fullmatch(r'(h|s)?#(\d+(?:\.5)?)', t)
        if not m:
            raise ValueError(f'unsupported stipulation {s!r} (supported: #n, h#n, h#n.5, s#n)')
        kind = {'h': 'help', 's': 'self', None: 'direct'}[m.group(1)]
        return Stipulation(kind, float(m.group(2)), s.strip())


@dataclass
class Problem:
    board: chess.Board
    stip: Stipulation
    meta: dict = field(default_factory=dict)

    @staticmethod
    def from_pieces(white: list[str], black: list[str], stipulation: str, **meta) -> 'Problem':
        """white/black like ['Kg1','Qd1','Sf3','Pe2'] (S or N = knight, P optional for pawns)."""
        b = chess.Board(None)
        for color, lst in ((chess.WHITE, white), (chess.BLACK, black)):
            for tok in lst:
                tok = tok.strip()
                if len(tok) == 2:
                    tok = 'P' + tok
                pt = LETTER_PIECE[tok[0].upper()]
                b.set_piece_at(chess.parse_square(tok[1:3]), chess.Piece(pt, color))
        st = Stipulation.parse(stipulation)
        b.turn = chess.BLACK if (st.kind == 'help' and not st.half) else chess.WHITE
        _set_castling(b)
        return Problem(b, st, meta)

    @staticmethod
    def from_fen(fen: str, stipulation: str, **meta) -> 'Problem':
        st = Stipulation.parse(stipulation)
        b = chess.Board(fen if len(fen.split()) > 1 else fen + ' w - - 0 1')
        b.turn = chess.BLACK if (st.kind == 'help' and not st.half) else chess.WHITE
        return Problem(b, st, meta)

    def fen(self) -> str:
        """Piece placement only - the form used when passing positions around."""
        return self.board.fen().split()[0]

    def diagram(self, fen: bool = True) -> str:
        rows = []
        for r in range(7, -1, -1):
            row = ''
            for f in range(8):
                p = self.board.piece_at(chess.square(f, r))
                row += (p.symbol().replace('N', 'S').replace('n', 's') if p else ('.' if (f + r) % 2 else ':')) + ' '
            rows.append(f'{r + 1} {row}')
        rows.append('  a b c d e f g h')
        if fen:
            rows.append(self.fen() + '   ' + self.stip.text + ' ' + self.count())
        w = len(self.board.occupied_co[chess.WHITE].bit_count() * [0]) if hasattr(int, 'bit_count') else 0
        return '\n'.join(rows)

    def count(self) -> str:
        w = bin(self.board.occupied_co[chess.WHITE]).count('1')
        b = bin(self.board.occupied_co[chess.BLACK]).count('1')
        return f'({w}+{b})'


def _set_castling(b: chess.Board):
    fl = ''
    for col, k, rooks in ((chess.WHITE, 'e1', (('h1', 'K'), ('a1', 'Q'))), (chess.BLACK, 'e8', (('h8', 'k'), ('a8', 'q')))):
        kp = b.piece_at(chess.parse_square(k))
        if kp and kp == chess.Piece(chess.KING, col):
            for sq, f in rooks:
                if b.piece_at(chess.parse_square(sq)) == chess.Piece(chess.ROOK, col):
                    fl += f
    b.set_castling_fen(fl or '-')


def san(board: chess.Board, move: chess.Move) -> str:
    """Album notation: S for knight, x captures, + / # suffixes, 0-0 castling."""
    if move == chess.Move.null():
        return '...'
    s = board.san(move)
    s = s.replace('O-O-O', '0-0-0').replace('O-O', '0-0')
    s = re.sub(r'^N', 'S', s)
    s = s.replace('=N', '=S')
    return s


def _min_pawn_captures(board, col) -> int | None:
    """Fewest captures that bring this side's pawns from their home files to where they stand (each capture moves a
    pawn one file and one rank forward, so a pawn on rank r has made at most r-2 of them). None if no assignment."""
    import chess as _c
    pawns = [(_c.square_file(sq), _c.square_rank(sq) - 1 if col == _c.WHITE else 6 - _c.square_rank(sq))
             for sq in board.pieces(_c.PAWN, col)]
    INF = 99
    best = {0: 0}
    for f, steps in pawns:                     # steps: ranks advanced from the home rank
        nxt = {}
        for used, cost in best.items():
            for f0 in range(8):
                d = abs(f - f0)
                if used >> f0 & 1 or d > steps:
                    continue
                k = used | 1 << f0
                if cost + d < nxt.get(k, INF):
                    nxt[k] = cost + d
        best = nxt
        if not best:
            return None
    return min(best.values())


def illegal_position(board) -> list:
    """Retro checks a diagram must pass (E. Bourd, 17 Oct 2026: "the position is illegal, so its a fatal flaw", on
    bourd-pawn-battery-queen-sd2, whose Black pawns needed 9 captures with 3 White units gone). One line per failure:
    pawns on the first or last rank, a pawn structure no home files can produce, more pawn captures than the
    opponent has lost units, more promoted units than missing pawns."""
    import chess as _c
    out = []
    for col, name in ((_c.WHITE, 'White'), (_c.BLACK, 'Black')):
        opp = not col
        if any(_c.square_rank(sq) in (0, 7) for sq in board.pieces(_c.PAWN, col)):
            out.append(f'{name} has a pawn on the first or last rank')
            continue
        lost = 16 - _c.popcount(board.occupied_co[opp])
        need = _min_pawn_captures(board, col)
        if need is None:
            out.append(f'{name} pawns stand where no home files can bring them')
        elif need > lost:
            out.append(f'{name} pawns need at least {need} captures, but {"Black" if col else "White"} has lost only {lost} units')
        q = len(board.pieces(_c.QUEEN, col)); r = len(board.pieces(_c.ROOK, col)); n = len(board.pieces(_c.KNIGHT, col))
        bs = board.pieces(_c.BISHOP, col)
        light = sum(1 for sq in bs if (_c.square_file(sq) + _c.square_rank(sq)) % 2 == 1)
        extra = max(0, q - 1) + max(0, r - 2) + max(0, n - 2) + max(0, light - 1) + max(0, len(bs) - light - 1)
        if extra + len(board.pieces(_c.PAWN, col)) > 8:
            out.append(f'{name} has {extra} promoted units but only {8 - len(board.pieces(_c.PAWN, col))} pawns missing')
    return out


def promoted_force(board) -> list:
    """Units beyond the original set: more than one queen, two rooks, two knights, or two bishops on
    one colour. E. Bourd: a promoted piece in the diagram is a fatal flaw. Returns one line per side."""
    import chess as _c
    out = []
    for col, name in ((_c.WHITE, 'White'), (_c.BLACK, 'Black')):
        q = len(board.pieces(_c.QUEEN, col)); r = len(board.pieces(_c.ROOK, col)); n = len(board.pieces(_c.KNIGHT, col))
        bs = board.pieces(_c.BISHOP, col)
        light = sum(1 for sq in bs if (_c.square_file(sq) + _c.square_rank(sq)) % 2 == 1); dark = len(bs) - light
        parts = []
        if q > 1: parts.append(f'{q} queens')
        if r > 2: parts.append(f'{r} rooks')
        if n > 2: parts.append(f'{n} knights')
        if light > 1 or dark > 1: parts.append(f'{len(bs)} bishops, {max(light, dark)} on one colour')
        if parts: out.append(f"{name} has {', '.join(parts)}")
    return out
