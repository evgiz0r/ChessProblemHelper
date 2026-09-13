"""Structured analysis of a problem: phases (set play, tries, solution), threats,
variations, refutations, and cross-phase relations (changed / transferred / reciprocal mates).

Everything returned is plain dicts/lists (JSON-serialisable) so an AI agent can reason over it.
"""
from __future__ import annotations
import time
import chess
from .core import Problem, san
from .solver import Engine, Budget


_ORIGIN = {}   # current square -> diagram square, for the piece that made the first move


def _mid(board, m):
    """Problemist identity of a move: piece + its diagram square + destination (+promotion).
    So Qb8-g8 after 1.Bh2 and Qh8-g8 after 1.Qh8 are the same mate 'Qg8' by the same queen."""
    p = board.piece_at(m.from_square)
    frm = chess.square_name(m.from_square)
    frm = _ORIGIN.get(frm, frm)
    promo = chess.piece_symbol(m.promotion) if m.promotion else ''
    return f"{'KQRBSP'[6 - p.piece_type] if p else '?'}{frm}{chess.square_name(m.to_square)}{promo}"


def _cont_list(board, moves):
    return [{'uci': m.uci(), 'id': _mid(board, m), 'san': san(board, m)} for m in moves]


def _variations(eng: Engine, board: chess.Board, n: int, mode: str, threat_ucis: set):
    """Board: Black to move. For each Black move -> White continuations within n-1."""
    out = []
    for b in list(board.legal_moves):
        d_san = san(board, b); d_id = _mid(board, b)
        board.push(b)
        try:
            gb = eng.goal_after_black(board, mode)
            if gb is True:           # (selfmate) Black's move itself is the mate
                conts, ends = [], True
            elif gb is False:
                conts, ends = [], False
            else:
                conts = eng.continuations(board, n - 1, mode) if n - 1 >= 1 else []
                ends = False
            cl = _cont_list(board, conts)
        finally:
            board.pop()
        cu = {c['id'] for c in cl}
        out.append({
            'defence': {'uci': b.uci(), 'id': d_id, 'san': d_san},
            'continuations': cl,
            'goal_by_defence': ends,
            'refutes': (not ends) and not cl,
            'dual': len(cl) > 1,
            'threat_repeat': bool(threat_ucis) and bool(cu & threat_ucis),
        })
    return out


def _phase(eng, board, n, mode, first_move, kind, refs=None):
    """board is the position BEFORE first_move (White to move)."""
    ph = {'type': kind, 'first_move': {'uci': first_move.uci(), 'id': _mid(board, first_move), 'san': san(board, first_move)}}
    _ORIGIN.clear(); _ORIGIN[chess.square_name(first_move.to_square)] = chess.square_name(first_move.from_square)
    board.push(first_move)
    try:
        if refs is not None:
            ph['refutations'] = _cont_list(board, refs)
        threat = []
        if not board.is_check() and n - 1 >= 1:
            board.push(chess.Move.null())
            try:
                threat = _cont_list(board, eng.continuations(board, n - 1, mode))
            finally:
                board.pop()
        ph['threat'] = threat
        ph['zugzwang'] = not threat and not board.is_check()
        ph['check_key'] = board.is_check()
        ph['variations'] = _variations(eng, board, n, mode, {t['id'] for t in threat})
        ph['flights'] = _flights(board)
    finally:
        board.pop()
        _ORIGIN.clear()
    return ph


def _flights(board: chess.Board):
    """Squares the black king can move to (Black to move)."""
    k = board.king(chess.BLACK)
    return sorted(chess.square_name(m.to_square) for m in board.legal_moves if m.from_square == k)


def _set_play(eng, board, n, mode):
    if n - 1 < 1 and mode == 'direct':
        return None
    b = board.copy(stack=False)
    b.turn = chess.BLACK
    b.ep_square = None
    if not b.is_valid() or b.is_check():
        return None
    ph = {'type': 'set', 'first_move': None, 'threat': [], 'zugzwang': False}
    ph['variations'] = _variations(eng, b, n, mode, set())
    ph['flights'] = _flights(b)
    ph['unprovided'] = [v['defence']['san'] for v in ph['variations'] if v['refutes']]
    return ph


def _defence_map(ph, unique_only=True):
    """black move uci -> set of continuation ucis, for real defences (threat defeated)."""
    return {v['defence']['id']: {c['id'] for c in v['continuations']}
            for v in ph['variations']
            if v['continuations'] and not v['threat_repeat'] and (len(v['continuations']) == 1 or not unique_only)}


def _label(ph):
    if ph['type'] == 'set':
        return 'set play'
    return f"{ph['type']} {ph['first_move']['san']}"


def compare_phases(phases, board=None):
    """Detect changed, transferred and reciprocally changed continuations between phases."""
    rel = {'changed': [], 'transferred': [], 'reciprocal': [], 'unchanged': []}
    sanmap = {}
    for ph in phases:
        for v in ph['variations']:
            sanmap.setdefault(v['defence']['id'], v['defence']['san'])
            for c in v['continuations']:
                sanmap.setdefault(c['id'], c['san'])
        for t in ph.get('threat', []):
            sanmap.setdefault(t['id'], t['san'])
    for i in range(len(phases)):
        for j in range(i + 1, len(phases)):
            A, B = phases[i], phases[j]
            ma, mb = _defence_map(A), _defence_map(B)
            common = set(ma) & set(mb)
            for d in sorted(common):
                if ma[d].isdisjoint(mb[d]):
                    rel['changed'].append({'defence': sanmap[d], 'phases': [_label(A), _label(B)],
                                           'from': sorted(sanmap[x] for x in ma[d]),
                                           'to': sorted(sanmap[x] for x in mb[d])})
                else:
                    rel['unchanged'].append({'defence': sanmap[d], 'phases': [_label(A), _label(B)]})
            # transferred: continuation after defence d in A appears after a different defence e in B
            for d, ca in ma.items():
                for e, cb in mb.items():
                    if d != e and d[1:3] != e[1:3]:
                        for w in ca & cb:
                            if w not in mb.get(d, set()):
                                rel['transferred'].append({'continuation': sanmap[w], 'phases': [_label(A), _label(B)],
                                                           'defences': [sanmap[d], sanmap[e]]})
            # reciprocal: d1->X, d2->Y  becomes  d1->Y, d2->X
            cl = sorted(common)
            for x in range(len(cl)):
                for y in range(x + 1, len(cl)):
                    d1, d2 = cl[x], cl[y]
                    if (ma[d1] & mb[d2]) and (ma[d2] & mb[d1]) and ma[d1].isdisjoint(mb[d1]) and ma[d2].isdisjoint(mb[d2]):
                        rel['reciprocal'].append({'defences': [sanmap[d1], sanmap[d2]], 'phases': [_label(A), _label(B)]})
    rel['patterns'] = detect_patterns(phases, sanmap, board)
    return rel


def _line_dir(a, b):
    fa, ra, fb, rb = chess.square_file(a), chess.square_rank(a), chess.square_file(b), chess.square_rank(b)
    df, dr = fb - fa, rb - ra
    if df == 0 and dr == 0:
        return None
    if df == 0 or dr == 0 or abs(df) == abs(dr):
        return ((df > 0) - (df < 0), (dr > 0) - (dr < 0))
    return None


def _between(a, b, c):
    """Is square b strictly between a and c on one line?"""
    d1, d2 = _line_dir(a, b), _line_dir(b, c)
    return d1 is not None and d1 == d2


def bristol(first_uci, follow_uci):
    """Bristol clearance (taught by E. Bourd, 2026): the first move travels along a line A->B; a second
    piece then moves along the SAME line in the SAME direction, passing over A and stopping short of B."""
    A, B = chess.parse_square(first_uci[:2]), chess.parse_square(first_uci[2:4])
    C, D = chess.parse_square(follow_uci[:2]), chess.parse_square(follow_uci[2:4])
    d = _line_dir(A, B)
    return d is not None and _line_dir(C, D) == d and _between(C, A, D) and (D == B or _between(A, D, B)) and D != B


def cut_lines(board_before: chess.Board, move: chess.Move):
    """White line pieces whose lines are CLOSED by `move` (the moving piece stands in their way afterwards).
    Returns {square_cut: [white piece names whose guard on it is lost]}."""
    after = board_before.copy(stack=False); after.push(move)
    ghost = after.copy(stack=False); ghost.remove_piece_at(move.to_square)
    cut = {}
    for sq in chess.SquareSet(after.occupied_co[chess.WHITE]):
        if sq == move.to_square or after.piece_type_at(sq) not in (chess.QUEEN, chess.ROOK, chess.BISHOP):
            continue
        lost = int(ghost.attacks(sq)) & ~int(after.attacks(sq))
        for t in chess.SquareSet(lost):
            if t != move.to_square:
                p = after.piece_at(sq)
                cut.setdefault(chess.square_name(t), []).append(f"{'QRB'[[chess.QUEEN, chess.ROOK, chess.BISHOP].index(p.piece_type)]}{chess.square_name(sq)}")
    return cut


def interference_motive(board: chess.Board, try_ph: dict, key_ph: dict | None = None):
    """Why does the try fail? If the first move closed a White line and the refutation exploits a square
    that line used to guard, return the explanation (white self-interference try)."""
    fm = chess.Move.from_uci(try_ph['first_move']['uci'])
    cut = cut_lines(board, fm)
    if not cut:
        return None
    out = []
    for r in try_ph.get('refutations', []):
        b = board.copy(stack=False); b.push(fm); rm = chess.Move.from_uci(r['uci'])
        hits = set()
        if chess.square_name(rm.to_square) in cut:
            hits.add(chess.square_name(rm.to_square))
        b.push(rm)
        # candidate White answers: the try's threat, and the answer this defence gets in the SOLUTION
        cands = list(try_ph.get('threat', []))
        if key_ph:
            for v in key_ph['variations']:
                if v['defence']['uci'] == r['uci']:
                    cands += v['continuations']
        for t in cands:
            tm = chess.Move.from_uci(t['uci'])
            if tm not in b.legal_moves:
                continue
            b2 = b.copy(stack=False); b2.push(tm)
            for m in b2.legal_moves:          # how does Black survive the threat move?
                if chess.square_name(m.to_square) in cut:
                    hits.add(chess.square_name(m.to_square))
        if hits:
            out.append({'refutation': r['san'], 'squares': sorted(hits),
                        'lines': sorted({x for h in hits for x in cut[h]})})
    return out or None


def detect_patterns(phases, sanmap, board=None):
    """Named patterns. Extend this as new themes are taught."""
    pats = []
    if board is not None:
        for ph in phases:
            if ph['type'] == 'try':
                keyp = next((q for q in phases if q['type'] == 'key'), None)
                im = interference_motive(board, ph, keyp)
                if im:
                    for x in im:
                        pats.append({'name': 'White interference try', 'phases': [_label(ph)],
                                     'defence': f"1.{ph['first_move']['san']}? cuts {'/'.join(x['lines'])} -> {','.join(x['squares'])}; 1...{x['refutation']}!"})
    for ph in phases:
        if ph['type'] not in ('try', 'key'):
            continue
        fm = ph['first_move']['uci']
        for t in ph['threat']:
            if bristol(fm, t['uci']):
                pats.append({'name': 'Bristol', 'phases': [_label(ph)], 'defence': f"1.{ph['first_move']['san']} + 2.{t['san']}"})
        for v in ph['variations']:
            for c in v['continuations']:
                if not v['threat_repeat'] and bristol(fm, c['uci']):
                    pats.append({'name': 'Bristol (in variation)', 'phases': [_label(ph)],
                                 'defence': f"1.{ph['first_move']['san']} {v['defence']['san']} 2.{c['san']}"})
    real = [p for p in phases if p['type'] in ('try', 'key')]
    for i in range(len(real)):
        for j in range(len(real)):
            if i == j:
                continue
            A, B = real[i], real[j]
            ta = {t['id'] for t in A['threat']}; tb = {t['id'] for t in B['threat']}
            if not ta or not tb:
                continue
            if i < j and ta.isdisjoint(tb):
                pats.append({'name': 'changed threat', 'phases': [_label(A), _label(B)],
                             'threats': [sorted(sanmap.get(x, x) for x in ta), sorted(sanmap.get(x, x) for x in tb)]})
            ma, mb = _defence_map(A), _defence_map(B)
            # Le Grand: threat A / variation d->B  becomes  threat B / d->A
            for d in set(ma) & set(mb):
                if ma[d] <= tb and mb[d] <= ta and ta.isdisjoint(tb) and i < j:
                    pats.append({'name': 'Le Grand', 'phases': [_label(A), _label(B)], 'defence': sanmap.get(d, d)})
            # pseudo Le Grand: threat of A appears as mate after a defence in B, and vice versa (different defences)
            if i < j:
                xa = [d for d, c in mb.items() if c <= ta]
                xb = [d for d, c in ma.items() if c <= tb]
                if xa and xb and ta.isdisjoint(tb) and not (set(xa) & set(xb)):
                    pats.append({'name': 'Pseudo Le Grand', 'phases': [_label(A), _label(B)],
                                 'defences': [sanmap.get(xb[0]), sanmap.get(xa[0])]})
    # Threat reversal: 1.A? threat B  /  1.B! threat A  (first move and threat swap)
    for i in range(len(real)):
        for j in range(i + 1, len(real)):
            A, B = real[i], real[j]
            ta = {t['id'] for t in A['threat']}; tb = {t['id'] for t in B['threat']}
            if A['first_move'].get('id') in tb and B['first_move'].get('id') in ta:
                pats.append({'name': 'Threat reversal', 'phases': [_label(A), _label(B)]})
    # Dombrovskis: in phase A threat X is defeated by defence d (d refutes, or d stops X);
    # in phase B the same defence d is answered by X.
    for A in real:
        ta = {t['id'] for t in A['threat']}
        if not ta:
            continue
        stoppers = {v['defence']['id'] for v in A['variations'] if not v['threat_repeat']}
        for B in real:
            if B is A:
                continue
            for d, conts in _defence_map(B).items():
                if d in stoppers and conts & ta:
                    refuting = d in {r.get('id') for r in A.get('refutations', [])}
                    pats.append({'name': 'Dombrovskis' + (' (refutation)' if refuting else ''),
                                 'phases': [_label(A), _label(B)], 'defence': sanmap.get(d, d)})
    # Zagoruiko: best subset of >=3 phases sharing >=2 defences whose continuations change in every phase
    from itertools import combinations
    maps = [(p, _defence_map(p)) for p in phases]
    best = None
    for k in range(min(len(maps), 6), 2, -1):
        for combo in combinations(maps, k):
            common = set.intersection(*[set(m) for _, m in combo])
            steady = [d for d in common
                      if all(combo[x][1][d].isdisjoint(combo[y][1][d]) for x in range(k) for y in range(x + 1, k))]
            if len(steady) >= 2 and (best is None or (k, len(steady)) > (best[0], len(best[1]))):
                best = (k, steady, [_label(p) for p, _ in combo])
        if best:
            break
    if best:
        pats.append({'name': f'Zagoruiko {best[0]}x{len(best[1])}', 'defences': sorted(sanmap.get(d, d) for d in best[1]),
                     'phases': best[2]})
    return pats


def analyse(problem: Problem, max_refutations: int = 1, include_tries: bool = True,
            include_set: bool = True, time_limit: float | None = 120, checking_tries: bool = False) -> dict:
    st = problem.stip
    board = problem.board.copy()
    eng = Engine(time_limit)
    t0 = time.time()
    res = {'stipulation': st.text, 'kind': st.kind, 'fen': board.fen(), 'count': problem.count()}
    try:
        if st.kind == 'help':
            plies = 2 * st.full_moves + (1 if st.half else 0)
            sols = eng.help_solutions(board, plies)
            res['solutions'] = [_help_line(board, s, st) for s in sols]
            res['n_solutions'] = len(sols)
        else:
            n, mode = st.full_moves, st.kind
            phases = []
            if include_set:
                sp = _set_play(eng, board, n, mode)
                if sp and any(v['continuations'] for v in sp['variations']):
                    phases.append(sp)
            keys, tries = [], []
            for w in eng.ordered(board):
                board.push(w)
                try:
                    refs = eng.refutations(board, n, mode, limit=max_refutations if include_tries else 0)
                finally:
                    board.pop()
                if refs is None:
                    continue
                if not refs:
                    keys.append(w)
                elif include_tries and len(refs) <= max_refutations and (checking_tries or not board.gives_check(w)):
                    tries.append((w, refs))
            for w, refs in tries:
                phases.append(_phase(eng, board, n, mode, w, 'try', refs))
            for w in keys:
                phases.append(_phase(eng, board, n, mode, w, 'key', []))
            res['keys'] = [san(board, k) for k in keys]
            res['cooked'] = len(keys) > 1
            res['phases'] = phases
            res['relations'] = compare_phases(phases, board)
            try:
                from .motives import explain_key_phase, detect_grimshaw
                ex = explain_key_phase(problem, res)
                res['motives'] = ex
                for g in detect_grimshaw(ex):
                    res['relations']['patterns'].append({'name': 'Grimshaw', 'phases': ['key'], 'defence': f"{'/'.join(g['defences'])} on {g['square']}"})
            except Exception as exc:
                res['motives_error'] = repr(exc)
    except Budget:
        res['timeout'] = True
    res['nodes'] = eng.nodes
    res['seconds'] = round(time.time() - t0, 2)
    return res


def _help_line(board, moves, st):
    """Helpmate line in album numbering: h#n -> 1.B W 2.B W# ; h#n.5 -> 1...W 2.B W ..."""
    b = board.copy(stack=False)
    out, n = [], 1
    for i, m in enumerate(moves):
        s = san(b, m)
        if st.half and i == 0:
            out.append(f'1...{s}'); n = 2
        elif b.turn == chess.BLACK:
            out.append(f'{n}.{s}')
        else:
            out.append(s); n += 1
        b.push(m)
    return {'line': ' '.join(out), 'uci': [m.uci() for m in moves]}
