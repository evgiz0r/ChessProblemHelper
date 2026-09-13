"""Find candidate KEYS from a fixed post-key position (method taught by E. Bourd, session 3).

The composer first settles the post-key play, then looks for a first move that produces it. Any candidate
key is a White unit standing elsewhere in the diagram:

    diagram = post-key position with one White unit moved back from s to t      (key = t->s)

Two flavours, both covered by that operation:
  * arrive : an existing White unit of the post-key position comes from t (e.g. a knight from d6 that
             pins d5 on leaving, a queen reaching the same square from e2/c2/f3)
  * park   : a NEW White unit stands on the critical square t in the diagram (e.g. on the threat line)
             and moves away to a harmless parking square s; every other destination is a try

Tries are the other moves of the key piece from t. A try is *thematic* when its refutation uses the
thematic Black units (the half-pinned pair, say) rather than something incidental.
"""
from __future__ import annotations
import chess, time
from ..core import Problem, Stipulation, san
from ..analysis import analyse
from ..motives import explain_key_phase, detect_half_pin

PT = {'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'S': chess.KNIGHT, 'N': chess.KNIGHT, 'P': chess.PAWN}


def _origins(board: chess.Board, sq: int, ptype: int, color=chess.WHITE):
    """Squares from which a piece of this type could quietly reach sq in the given position."""
    b = board.copy()
    piece = b.piece_at(sq)
    b.remove_piece_at(sq)
    out = []
    for t in chess.SQUARES:
        if b.piece_at(t) or t == sq:
            continue
        if ptype == chess.PAWN and (chess.square_rank(t) in (0, 7) or chess.square_rank(sq) in (0, 7)):
            continue
        bb = b.copy()
        bb.set_piece_at(t, chess.Piece(ptype, color))
        bb.turn = color
        if chess.Move(t, sq) in bb.legal_moves:
            out.append(t)
    if piece:
        b.set_piece_at(sq, piece)
    return out


def candidates(post_fen: str, stipulation: str = '#2', park: list[str] | None = None,
               park_pieces: str = 'SBRQ', thematic_squares: list[str] | None = None,
               time_limit: float = 240, want_threat: str | None = None, verbose=True):
    """post_fen: position AFTER the key, Black to move.
    park: optional list of parking squares for an ADDED White unit (mode 'park').
    thematic_squares: Black units considered thematic (e.g. ['f6','e5']); refutations from them count as thematic.
    """
    post = chess.Board(post_fen if len(post_fen.split()) > 1 else post_fen + ' b - - 0 1')
    stip = Stipulation.parse(stipulation)
    res, t0 = [], time.time()
    jobs = []
    # mode 'arrive': relocate an existing White unit
    for s in chess.SquareSet(post.occupied_co[chess.WHITE]):
        p = post.piece_at(s)
        if p.piece_type == chess.KING:
            continue
        for t in _origins(post, s, p.piece_type):
            jobs.append(('arrive', s, t, p.piece_type))
    # mode 'park': a new White unit parks on s and could have come from t
    for ps in (park or []):
        s = chess.parse_square(ps)
        if post.piece_at(s):
            continue
        for sym in park_pieces:
            pt = PT[sym]
            b = post.copy(); b.set_piece_at(s, chess.Piece(pt, chess.WHITE))
            for t in _origins(b, s, pt):
                jobs.append(('park', s, t, pt))
    for mode, s, t, pt in jobs:
        if time.time() - t0 > time_limit:
            if verbose:
                print(f'(time limit after {len(res)} hits)')
            break
        d = post.copy()
        d.remove_piece_at(s)
        d.set_piece_at(t, chess.Piece(pt, chess.WHITE))
        d.turn = chess.WHITE
        if not d.is_valid():
            continue
        p = Problem(d, stip)
        r = analyse(p, max_refutations=1, include_set=False, time_limit=20)
        keys = r.get('keys', [])
        if len(keys) != 1:
            continue
        kp = [x for x in r['phases'] if x['type'] == 'key'][0]
        km = chess.Move.from_uci(kp['first_move']['uci'])
        if km.from_square != t or km.to_square != s or kp.get('check_key') or d.is_capture(km):
            continue
        if want_threat and want_threat not in [x['san'] for x in kp['threat']]:
            continue
        tries = [x for x in r['phases'] if x['type'] == 'try' and x['first_move']['uci'][:2] == chess.square_name(t)]
        th = set(thematic_squares or [])
        def thematic(tr):
            return all(x['uci'][:2] in th for x in tr['refutations'])
        good = [x for x in tries if thematic(x)]
        vars_ = [v for v in kp['variations'] if not v['threat_repeat'] and v['continuations']]
        entry = {'mode': mode, 'key': f"{san(d, km)}", 'from': chess.square_name(t), 'to': chess.square_name(s),
                 'piece': chess.piece_symbol(pt).upper().replace('N', 'S'),
                 'threat': '/'.join(x['san'] for x in kp['threat']),
                 'variations': [f"{v['defence']['san']}->{'/'.join(c['san'] for c in v['continuations'])}" for v in vars_],
                 'tries': [f"{x['first_move']['san']}? but {'/'.join(y['san'] for y in x['refutations'])}!" for x in tries],
                 'thematic_tries': len(good), 'n_tries': len(tries), 'fen': d.fen()}
        res.append(entry)
        if verbose and good:
            print(f"  {entry['piece']}{entry['from']}->{entry['to']}: 1.{entry['key']}! ({entry['threat']}) "
                  f"thematic tries {len(good)}/{len(tries)}: {entry['tries']}")
    res.sort(key=lambda e: (-e['thematic_tries'], -e['n_tries'], len(e['variations'])))
    return res
