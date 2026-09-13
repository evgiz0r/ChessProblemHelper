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
