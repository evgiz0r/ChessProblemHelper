"""Composer's critique of a #2 / s#2 analysis: explicit, inspectable rules.

Rules taught by Evgeni Bourd (Sept 2026), plus standard conventions. Each finding has a severity:
  'major'  - considered a big flaw by judges
  'minor'  - a blemish
  'plus'   - a merit
Rules are data-light functions so they can be corrected / extended as more of the composer's
judgement is taught.
"""
from __future__ import annotations
import chess
from .core import Problem, san, promoted_force, illegal_position
from .analysis import analyse
from .solver import Engine

NAMES = {chess.KING: 'K', chess.QUEEN: 'Q', chess.ROOK: 'R', chess.BISHOP: 'B', chess.KNIGHT: 'S', chess.PAWN: 'P'}


def _pname(board, sq):
    p = board.piece_at(sq)
    return f"{'w' if p.color else 'b'}{NAMES[p.piece_type]}{chess.square_name(sq)}"


def _mate_positions(problem, res):
    """Yield (label, board_after_mate, origin_map) for threat + all real-defence mates of the key.
    origin_map: current square -> diagram square for White pieces that moved (key piece, mating piece)."""
    board = problem.board
    for ph in res['phases']:
        if ph['type'] != 'key':
            continue
        key = chess.Move.from_uci(ph['first_move']['uci'])
        b1 = board.copy(); b1.push(key)
        base = {key.to_square: key.from_square}

        def after(mv, b2):
            m = chess.Move.from_uci(mv)
            om = dict(base)
            om[m.to_square] = om.pop(m.from_square, m.from_square)
            b2.push(m)
            return om
        for t in ph['threat']:
            b2 = b1.copy(); b2.push(chess.Move.null())
            om = after(t['uci'], b2)
            yield f"threat 2.{t['san']}", b2, om
        bk = b1.king(chess.BLACK)
        for v in ph['variations']:
            # a king flight answered by the threat mate is still a different mate position (session 29:
            # 1.Qc2! Kd4 2.Qc5# needs wKb6), so king moves count even when they only repeat the threat
            kmove_def = bk is not None and chess.Move.from_uci(v['defence']['uci']).from_square == bk
            if (v['threat_repeat'] and not kmove_def) or not v['continuations']:
                continue
            for c in v['continuations']:
                b2 = b1.copy(); b2.push(chess.Move.from_uci(v['defence']['uci']))
                om = after(c['uci'], b2)
                yield f"1...{v['defence']['san']} 2.{c['san']}", b2, om


def mate_participation(problem, res):
    """For each White piece (by diagram square): the mates in which it takes part.
    Takes part = makes the mating move (a battery's front piece), gives check, guards a square of the king's field (incl.
    the square of an adjacent White piece), stands on a square of the field (a guarded blocker), or pins a Black piece. Also records squares guarded more than once (impurity)."""
    use = {}
    for label, b, om in _mate_positions(problem, res):
        k = b.king(chess.BLACK)
        field = [s for s in chess.SquareSet(chess.BB_KING_ATTACKS[k])
                 if not b.piece_at(s) or b.piece_at(s).color == chess.WHITE]
        fmask = 0
        for s in field:
            fmask |= chess.BB_SQUARES[s]
        pinned_lines = 0
        for bs in chess.SquareSet(b.occupied_co[chess.BLACK]):
            if b.is_pinned(chess.BLACK, bs):
                pinned_lines |= int(b.pin(chess.BLACK, bs))
        checkers = b.checkers()
        mover = b.peek().to_square if b.move_stack else None   # a battery's front piece plays the mate (19 Oct 2026)
        for sq in chess.SquareSet(b.occupied_co[chess.WHITE]):
            att = int(b.attacks(sq))
            if (att & fmask) or (sq in checkers) or (sq in field) or sq == mover or (chess.BB_SQUARES[sq] & pinned_lines and b.piece_type_at(sq) != chess.PAWN):
                use.setdefault(chess.square_name(om.get(sq, sq)), []).append(label)
    return use


def set_play_only_units(problem, res):
    """White units (diagram squares) that take part in a set-play mate but are redundant in every mate of the
    key phase: removed there, the mate still stands (E. Bourd, mentor issue #4: Rc8 of Daily No. 3 gave only
    the set mate 1...Sxe5 2.Rd8#; after the key the king duplicates its guards. "If completely redundant,
    it's bad")."""
    board = problem.board
    sp = next((ph for ph in res.get('phases', []) if ph['type'] == 'set'), None)
    key = next((ph for ph in res.get('phases', []) if ph['type'] == 'key'), None)
    if not sp or not key:
        return []
    in_set = set()
    for v in sp.get('variations', []):
        for c in v.get('continuations', []):
            b2 = board.copy(); b2.turn = chess.BLACK
            b2.push(chess.Move.from_uci(v['defence']['uci']))
            m = chess.Move.from_uci(c['uci'])
            b2.push(m)
            k = b2.king(chess.BLACK)
            for sq in chess.SquareSet(b2.occupied_co[chess.WHITE]):
                if sq == m.to_square:
                    in_set.add(m.from_square); continue
                t = b2.copy(); t.remove_piece_at(sq)
                if not t.is_checkmate():
                    in_set.add(sq)
    kfrom = chess.Move.from_uci(key['first_move']['uci']).from_square
    out = []
    for sq in sorted(in_set):
        if sq == kfrom or board.piece_type_at(sq) == chess.KING:
            continue
        needed = False
        for label, b2, om in _mate_positions(problem, res):
            cur = [c for c, o in om.items() if o == sq]
            if cur:                                   # it moved: it is the mating piece
                needed = True; break
            if b2.piece_at(sq) is None:               # captured on the way: no claim
                continue
            t = b2.copy(); t.remove_piece_at(sq)
            if not t.is_checkmate():
                needed = True; break
        if not needed:
            out.append(chess.square_name(sq))
    return out


def king_pin_anchor(problem, res):
    """Defences of the key phase that PIN a White piece against the White king (E. Bourd s20: the White
    king is thematic when it anchors the pin a defence creates - 1...Rxe4 pinning Qe2 is why the threat
    fails). Returns strings like '1...Rxe4 pins Qe2'."""
    out = []
    key_ph = next((ph for ph in res.get('phases', []) if ph['type'] == 'key'), None)
    if not key_ph:
        return out
    b1 = problem.board.copy()
    b1.push(chess.Move.from_uci(key_ph['first_move']['uci']))
    wk = b1.king(chess.WHITE)
    if wk is None:
        return out
    before = {sq for sq in chess.SquareSet(b1.occupied_co[chess.WHITE]) if b1.is_pinned(chess.WHITE, sq)}
    for v in key_ph['variations']:
        if v['threat_repeat'] or not v['continuations']:
            continue
        b2 = b1.copy(); b2.push(chess.Move.from_uci(v['defence']['uci']))
        new = {sq for sq in chess.SquareSet(b2.occupied_co[chess.WHITE]) if b2.is_pinned(chess.WHITE, sq)} - before
        for sq in sorted(new):
            out.append(f"1...{v['defence']['san']} pins {_pname(b2, sq)}")
    return out


def piece_necessity(problem, res, time_limit=20):
    """Remove each non-royal piece from the diagram: does the problem stay sound with the same key?
    If yes, the piece is not needed for soundness (it may still be needed for a variation)."""
    key = res['keys'][0] if res.get('keys') else None
    key_ph = next((ph for ph in res.get('phases', []) if ph['type'] == 'key'), None)
    key_uci = key_ph['first_move']['uci'] if key_ph else None
    out = {}
    for sq in chess.SQUARES:
        p = problem.board.piece_at(sq)
        if not p or p.piece_type == chess.KING:
            continue
        b = problem.board.copy(); b.remove_piece_at(sq)
        if not b.is_valid():
            out[chess.square_name(sq)] = 'needed (legality)'; continue
        pr = Problem(b, problem.stip)
        r = analyse(pr, max_refutations=1, include_tries=True, include_set=True, time_limit=time_limit)
        keys = r.get('keys', [])
        base_thr = {t['san'] for t in (key_ph or {}).get('threat') or []}
        new_key = next((ph for ph in r.get('phases', []) if ph['type'] == 'key'), None)
        new_thr = {t['san'] for t in (new_key or {}).get('threat') or []}
        if keys == [key] and len(base_thr) == 1 and len(new_thr) > 1:
            # a double threat is fatal for us: the unit that prevents it is a cook-stopper (his wPc6, 16 Oct 2026)
            out[chess.square_name(sq)] = f"needed (stops the double threat {'/'.join(sorted(new_thr))})"
        elif keys == [key]:
            k0 = [ph for ph in r['phases'] if ph['type'] == 'key'][0]
            real = [v for v in k0['variations'] if not v['threat_repeat'] and v['continuations']]
            base_k = [ph for ph in res['phases'] if ph['type'] == 'key'][0]
            base_real = [v for v in base_k['variations'] if not v['threat_repeat'] and v['continuations']]
            base_duals = {v['defence']['uci'] for v in base_real if v['dual']}
            duals = [v for v in real if v['dual'] and v['defence']['uci'] not in base_duals]
            lost = len(base_real) - len(real)
            # tries are content too: a unit may exist only to make the thematic tries fail
            kp_sq = key_uci[:2] if key_uci else None
            base_tries = {ph['first_move']['san'] for ph in res['phases']
                          if ph['type'] == 'try' and ph['first_move']['uci'][:2] == kp_sq}
            new_tries = {ph['first_move']['san'] for ph in r.get('phases', [])
                         if ph['type'] == 'try' and ph['first_move']['uci'][:2] == kp_sq}
            lost_tries = base_tries - new_tries
            # changed-mate relations are content whoever makes the try (E. Bourd s19: the try 1.e6? by a pawn
            # carries the changes); so are duals introduced into a try phase that takes part in a change
            def _changes(rr):
                return {(c['defence'], tuple(c['phases'])) for c in rr.get('relations', {}).get('changed', [])}
            lost_changes = _changes(res) - _changes(r)
            try:
                from .motives import dual_avoidance_after as _da
                km = chess.Move.from_uci(key_uci)
                base_kinds = set(_da(problem.board, km).get('thematic_kinds', []))
                new_kinds = set(_da(b, km).get('thematic_kinds', []))
            except Exception:
                base_kinds = new_kinds = set()
            base_sp = next((ph for ph in res['phases'] if ph['type'] == 'set'), None)
            new_sp = next((ph for ph in r.get('phases', []) if ph['type'] == 'set'), None)
            new_unprov = set(new_sp.get('unprovided', [])) - set(base_sp.get('unprovided', [])) if (base_sp and new_sp) else set()
            if duals:
                # a dual after the key is fatal, so this comes before tries and changes (claude-type3-queen-lines:
                # wSg1 makes the set mate Qf3# and shuts Qh1# out of 1...Sd3/Sc2 after 1.Ke2!)
                out[chess.square_name(sq)] = ('needed (stops the dual(s) ' +
                    ', '.join(f"1...{v['defence']['san']} {'/'.join(c['san'] for c in v['continuations'])}" for v in duals[:2]) + ')')
            elif lost_tries:
                out[chess.square_name(sq)] = ('needed for the CONTENT: without it the tries '
                                              + ', '.join('1.' + t + '?' for t in sorted(lost_tries)) + ' are lost')
            elif lost_changes:
                out[chess.square_name(sq)] = ('needed for the CONTENT: without it the changed mate(s) after '
                                              + ', '.join(sorted({'1...' + d for d, _ in lost_changes})) + ' are lost')
            elif lost > 0:
                out[chess.square_name(sq)] = f'needed for the CONTENT: {lost} variation(s) lost without it'
            elif new_unprov:
                out[chess.square_name(sq)] = ('needed for the SET PLAY: without it '
                                              + ', '.join('1...' + x for x in sorted(new_unprov)) + ' is unprovided')
            elif base_kinds and new_kinds and new_kinds != base_kinds:
                out[chess.square_name(sq)] = ('needed for the CONTENT: the dual-avoidance motive degrades from '
                                              + '/'.join(sorted(base_kinds)) + ' to ' + '/'.join(sorted(new_kinds)))
            else:
                out[chess.square_name(sq)] = f'not needed ({len(real)} variations remain, no duals)'
        elif not keys:
            out[chess.square_name(sq)] = 'needed (no solution without it)'
        else:
            extra = [k for k in keys if k != key]
            out[chess.square_name(sq)] = f"needed (stops {', '.join(extra[:4])})" if extra else 'needed'
    return out


def _king_stops_cooks(problem, res, ksq, tries=16) -> bool:
    """True when the White king's square matters: moving it to some other legal square spoils the problem
    (cooked or unsound), so it stands where it does to stop cooks (E. Bourd s30: not a flaw)."""
    board = problem.board
    key = next((ph for ph in res['phases'] if ph['type'] == 'key'), None)
    if key is None:
        return False
    bk = board.king(chess.BLACK)
    cands = sorted((s for s in chess.SQUARES if not board.piece_at(s) and chess.square_distance(s, bk) >= 2),
                   key=lambda s: chess.square_distance(s, ksq))[:tries]     # the nearby squares tell most
    tested = 0
    for s in cands:
        b = board.copy(); b.remove_piece_at(ksq); b.set_piece_at(s, chess.Piece(chess.KING, chess.WHITE))
        if not b.is_valid() or b.is_check():
            continue
        tested += 1
        try:
            r = analyse(Problem.from_fen(b.fen(), '#2'), max_refutations=0, include_tries=False, include_set=False, time_limit=5)
        except Exception:
            continue
        if r.get('keys') != res.get('keys') or r.get('cooked'):
            return True           # placed elsewhere it lets a cook in (or breaks the key): a cook-stopper
    return False


def critique(problem: Problem, res: dict | None = None, necessity: bool = True) -> dict:
    res = res or analyse(problem, max_refutations=1)
    F = []
    add = lambda sev, rule, msg: F.append({'severity': sev, 'rule': rule, 'msg': msg})
    board = problem.board
    for line in promoted_force(board):
        add('major', 'promoted force', line + ' (fatal, E. Bourd)')
    for line in illegal_position(board):
        add('major', 'illegal position', line + ' (fatal, E. Bourd 17 Oct 2026)')
    if board.turn == chess.WHITE and board.is_check():
        add('major', 'white in check', 'White is in check in the diagram: the key only escapes the check (illegal for a problem)')
    if not res.get('keys'):
        add('major', 'unsound', 'no solution'); return {'findings': F}
    if res.get('cooked'):
        add('major', 'cook', f"cooked: {', '.join(res['keys'])}")
    key = [ph for ph in res['phases'] if ph['type'] == 'key'][0]
    tries = [ph for ph in res['phases'] if ph['type'] == 'try']
    kmove = chess.Move.from_uci(key['first_move']['uci'])

    # --- key quality
    if key.get('check_key'):
        add('major', 'check key', 'the key gives check')
    if board.is_capture(kmove):
        cap = board.piece_at(kmove.to_square)
        add('minor', 'capture key', 'the key captures a pawn (minor, E. Bourd 13 Oct 2026)'
            if cap is None or cap.piece_type == chess.PAWN else 'the key captures a piece')
    # E. Bourd (s30): a key that moves a White piece Black attacks is a flaw (the piece "escapes"), milder when
    # the alternative is a piece out of play
    kp0 = board.piece_at(kmove.from_square)
    att = black_captures(board, kmove.from_square)
    if kp0 and kp0.piece_type != chess.KING and att:
        msg = f"the key piece stands attacked in the diagram (from {', '.join(att)}): the key looks like an escape"
        # E. Bourd (14 Oct 2026, 1.Bd8! from c7 in bourd-halfpin-ss-bd8): "key is slightly less flawed here, as we have
        # a set mate, and the bishop seems to guard e5 as well" - a set mate that needs the piece on its diagram square
        # gives the square a reason; the attack is then a by-product, not the decoration of an escape
        roles = key_piece_set_roles(board, kmove, res['phases'])
        if roles:
            mates = '; '.join(f"1...{ds[0]}{f' (+{len(ds) - 1})' if len(ds) > 1 else ''} 2.{m}" for m, ds in roles.items())
            unprov = [m for m in key_piece_captures_unprovided(board, kmove, res['phases'])]
            msg += (f"; milder: the set mate{'s' if len(roles) > 1 else ''} {mates} need{'' if len(roles) > 1 else 's'} it on {chess.square_name(kmove.from_square)} (E. Bourd, 14 Oct 2026)"
                    + (f"; the capture 1...{', '.join(unprov)} has no set mate" if unprov else '; the capture is provided in the set play'))
        add('minor', 'attacked key piece', msg)
    # E. Bourd (session 29): "the key piece is always in play; the issue is that on the initial diagram it
    # has no role - not guarding, not delivering mates, not blocking pieces. So its only role is to come out
    # of thin air and place itself obviously on the key square" (his 1.Rf1 from h1). Three checks in the
    # diagram: does it guard a square of the black king's field, give a set-play mate, or block a line of
    # any other line piece (either colour)? None of the three: an idle key piece. Softer when the key piece
    # also plays thematic tries (his 1.Re7 with 1.Rh8?/1.Re5?/1.Ree3?): then its moves are the content.
    kp = board.piece_at(kmove.from_square)
    if kp and board.king(chess.BLACK) is not None and kp.piece_type != chess.KING:
        own_tries = [t for t in tries if t['first_move']['uci'][:2] == key['first_move']['uci'][:2]]
        if idle_key_piece(board, kmove, res['phases']):
            add('minor' if own_tries else 'major', 'idle key piece',
                f"1.{key['first_move']['san']}: in the diagram the key piece guards nothing near the king, gives no set mate and blocks no line" +
                (' (its tries make the move thematic)' if own_tries else ' - it comes out of thin air onto the key square (E. Bourd)'))
    # E. Bourd (session 29): when every non-threat variation after the key is already set with the same mate, the
    # key "lowers the complexity a bit, as no new play is generated by the key"; not that bad in a single-phase
    # problem, but "a more dynamic key that changes or introduces the play is more interesting".
    setv = {v['defence']['uci']: {c['uci'] for c in v['continuations']}
            for ph in res['phases'] if ph['type'] == 'set' for v in ph['variations'] if v['continuations']}
    keyv = [v for v in key['variations'] if not v.get('threat_repeat') and v['continuations']]
    if keyv and all(setv.get(v['defence']['uci']) == {c['uci'] for c in v['continuations']} for v in keyv):
        add('minor', 'static key', 'every variation is already set with the same mate: the key only adds the threat, '
            'no new or changed play (E. Bourd: a more dynamic key that changes or introduces play is more interesting)')
    b = board.copy(); b.turn = chess.BLACK
    flights_before = set(m.to_square for m in b.legal_moves if m.from_square == b.king(chess.BLACK)) if b.is_valid() else set()
    after = board.copy(); after.push(kmove)
    flights_after = set(m.to_square for m in after.legal_moves if m.from_square == after.king(chess.BLACK))
    # E. Bourd (s30): count the flights, not the squares - 1.Qc8-c2 trades e4 for e6 (1 -> 1) and takes nothing
    gained = ', '.join(chess.square_name(s) for s in flights_after - flights_before)
    lost = ', '.join(chess.square_name(s) for s in flights_before - flights_after)
    if len(flights_after) > len(flights_before):
        add('plus', 'flight-giving key', f'key gives flight(s): {gained} ({len(flights_before)} -> {len(flights_after)})')
    elif len(flights_after) < len(flights_before):
        add('minor', 'flight-taking key', f'key takes flight(s): {lost} ({len(flights_before)} -> {len(flights_after)})')
    elif gained:
        add('plus', 'flight exchange', f'key changes the flight: {lost} -> {gained}')
    # E. Bourd (7 Oct 2026, on daily No. 2): a key by a piece out of play makes the solution obvious - fatal.
    # Out of play: a knight or bishop on the edge of the board, three or more squares from the Black king,
    # guarding no square of the king's field. Queens and rooks too (E. Bourd, 8 Oct 2026, on 1.Qb1 from h1: "very
    # bad key, queen completely out of play").
    if out_of_play_key(board, kmove):
        add('major', 'out-of-play key', f"the key piece {_pname(board, kmove.from_square)} stands out of play "
                                        "(edge, far from the king, guarding nothing near it): the key is obvious (fatal, E. Bourd)")
    dist = chess.square_distance(kmove.from_square, kmove.to_square)
    if dist >= 4:
        add('plus', 'long key', f'long key move ({dist} squares)')

    # --- king escapes (taught): a flight in the diagram makes solving easy
    if flights_before:
        prov = {v['defence']['uci'][2:4] for v in next((p for p in res['phases'] if p['type'] == 'set'), {'variations': []})['variations']
                if v['defence']['uci'][:2] == chess.square_name(board.king(chess.BLACK)) and v['continuations']}
        add('minor' if len(flights_before) == len(prov) else 'major', 'king escape in diagram',
            'Black king has flight(s) in the diagram: ' + ', '.join(chess.square_name(s) for s in flights_before)
            + ('' if prov else ' (unprovided: makes the key easy to find)'))

    # --- refutations of tries (taught)
    key_piece_sq = key['first_move']['uci'][:2]
    key_threat = {t['id'] for t in key['threat']}
    same_threat = [t for t in tries if {x['id'] for x in t['threat']} == key_threat and key_threat]
    diff_threat = [t for t in tries if t not in same_threat]
    if len(same_threat) >= 2:
        rr = [r['uci'] for t in same_threat for r in t['refutations']]
        add('plus', 'try set', f"{len(same_threat)} tries carry the key's threat "
                               f"({', '.join('1.' + t['first_move']['san'] + '?' for t in same_threat)})"
                               + ('; each refuted differently' if len(set(rr)) == len(rr) else ''))
    refs = [(t['first_move']['san'], r['uci'], r['san']) for t in tries for r in t['refutations']
            if t['first_move']['uci'][:2] == key_piece_sq]
    ksq = chess.square_name(board.king(chess.BLACK))
    for tr, u, s in refs:
        if u[:2] == ksq:
            add('major', 'king refutes try', f'1.{tr}? is refuted by a king move (1...{s}!)')
    from collections import Counter
    # a try refuted by a king move is no try (CLAUDE.md fatal flaws): a White interference try that only gives a flight
    # is not content (19 Oct 2026, his 1.Bh2!: 1.Sg3? Kg2! had passed the single-phase gate as a thematic try)
    king_refuted = {f"try {t['first_move']['san']}" for t in tries
                    if any(r['uci'][:2] == ksq for r in t['refutations'])}
    themed = {x['phases'][0] for x in res['relations'].get('patterns', []) if 'interference try' in x['name']} - king_refuted
    thematic_label = lambda t: f"try {t['first_move']['san']}" in themed
    pool = same_threat if len(same_threat) >= 2 else [t for t in tries if t['first_move']['uci'][:2] == key_piece_sq
                                                      and (not themed or thematic_label(t))]
    them_refs = [(t['first_move']['san'], r['uci'], r['san']) for t in pool for r in t['refutations']]
    rc = Counter(u for _, u, _ in them_refs)
    wc_done = False                                  # one white correction: the random stage is the largest group
    for u, n in sorted(rc.items(), key=lambda x: -x[1]):
        if n > 1:
            s_ = next(x[2] for x in them_refs if x[1] == u)
            # tries by the key piece where some fail to u and another fails to something else are the random stage of a
            # white correction, not a flaw (E. Bourd, 13 Oct 2026: "B~ Bd6! Bf5!? Rd6! Bc2!")
            # judged among the key piece's own tries: king tries in the same threat pool (his 1.Kb7?/Ka7? Sd5!) do not
            # turn B~ Qg2+! Bd5!? Sxf6! Be4!? Sxe5! Bb7! into a 'same refutation' flaw (E. Bourd, 18 Oct 2026)
            kp_pool = [t for t in pool if t['first_move']['uci'][:2] == key_piece_sq]
            sharing = [t for t in pool if u in {r['uci'] for r in t['refutations']}]
            others = [t for t in kp_pool if u not in {r['uci'] for r in t['refutations']} and t['refutations']]
            if wc_done and all(t['first_move']['uci'][:2] == key_piece_sq for t in sharing):
                add('minor', 'same refutation', f'1...{s_}! refutes {n} corrections of the white correction')
                continue
            if u[:2] != ksq and others and all(t['first_move']['uci'][:2] == key_piece_sq for t in sharing):
                wc_done = True
                add('plus', 'white correction', f"1.{key['first_move']['san'][0]}~? {s_}! ({n} moves); "
                    + '; '.join(f"1.{t['first_move']['san']}? {'/'.join(r['san'] for r in t['refutations'])}!" for t in others)
                    + f"; 1.{key['first_move']['san']}!")
                continue
            add('major' if n > 2 or u[:2] == ksq else 'minor', 'same refutation', f'1...{s_}! refutes {n} thematic tries')
    if themed:
        other = Counter(u for _, u, _ in refs) - rc
        for u, n in other.items():
            if n > 1:
                s_ = next(x[2] for x in refs if x[1] == u)
                add('minor', 'mechanism refutation', f'1...{s_}! refutes {n} non-thematic tries by the key piece (forcing mechanism)')
    thematic_tries = [t for t in tries if t['first_move']['uci'][:2] == key['first_move']['uci'][:2]]
    if themed:
        add('plus', 'thematic tries', 'White interference tries: ' + '; '.join(x['defence'] for x in res['relations']['patterns']
                                                                                if 'interference try' in x['name'] and x['phases'][0] in themed))
    if len(thematic_tries) >= 2 and len({r['uci'] for t in thematic_tries for r in t['refutations']}) == len(thematic_tries):
        add('plus', 'distinct refutations', f'{len(thematic_tries)} tries by the key piece, each refuted differently')

    # --- defences
    real = [v for v in key['variations'] if not v['threat_repeat'] and v['continuations']]
    duals = [v for v in real if v['dual']]
    for v in duals:
        add('major' if len(real) <= 2 else 'minor', 'dual', f"1...{v['defence']['san']} allows {'/'.join(c['san'] for c in v['continuations'])}")
    # non-defences (the threat still works) that also allow other mates: duals outside the thematic play.
    # report hides them under 'further moves allow the threat' (E. Bourd's knight-cuts scheme, 10 Oct 2026)
    loose = [v for v in key['variations'] if v['threat_repeat'] and len(v['continuations']) > 1]
    if loose:
        ex = loose[0]
        add('minor', 'random-move duals', f"{len(loose)} move(s) that allow the threat also allow other mates "
            f"(1...{ex['defence']['san']} {'/'.join(c['san'] for c in ex['continuations'])})")
    nk = [v for v in real if v['defence']['uci'][:2] != ksq]
    kv = [v for v in real if v['defence']['uci'][:2] == ksq]
    if len(nk) < 2:
        add('major', 'thin play', f'only {len(nk)} non-king defence(s)')
    # a flight GIVEN by the key is the flight-giving theme (constitution: a plus), not an easy variation;
    # only a flight the king already had in the diagram is 'easy to see'
    for v in kv:
        if chess.parse_square(v['defence']['uci'][2:4]) in flights_after - flights_before:
            continue
        add('minor', 'king flight variation', f"1...{v['defence']['san']} is a king flight (easy to see)")
    # E. Bourd (14 Oct 2026): "I didn't like the recapture of the queen on the defense squares" - a defence that lands on a
    # square where the mate then captures it (1...Se6 2.Qxe6#): he looks for defences away from the thematic squares
    recap = [f"1...{v['defence']['san']} 2.{v['continuations'][0]['san']}" for v in real
             if len(v['continuations']) == 1 and v['continuations'][0]['uci'][2:4] == v['defence']['uci'][2:4]]
    if recap:
        add('minor', 'mate captures defender', 'the mate captures the defender on its arrival square: ' + ', '.join(recap) +
            ' (E. Bourd, 14 Oct 2026: defences away from the thematic squares are cleaner)')
    mates = {c['id'] for v in real for c in v['continuations']}
    if len(real) >= 3 and len(mates) >= 3:
        add('plus', 'varied play', f'{len(real)} defences, {len(mates)} different mates')
    for rule, sev, msg in simplicity(board, res, key, real, ksq):
        add(sev, rule, msg)

    # --- content: guard/unguard-only play is uninteresting (E. Bourd s2) - in a single-phase problem. When the mates change
    # between phases the change is the content and a plain guard is a pure single-purpose defence (E. Bourd, 14 Oct 2026, on
    # 1.Qc7! Rh3/Sf1 both guarding e3: "I don't think it's a flaw, it's somewhat pure single moves")
    try:
        from .motives import explain_key_phase
        ex = explain_key_phase(problem, res)
        if ex and all(all('guard' in w for w in e['why_defends']) and
                      all(all('unguard' in w or 'available anyway' in w for w in m['why_works']) for m in e['mates'])
                      for e in ex):
            if res.get('relations', {}).get('changed'):
                add('note', 'pure guard defences', 'the defences only guard the threat square: pure single-purpose moves, '
                    'the changed mates carry the content (E. Bourd, 14 Oct 2026)')
            else:
                add('minor', 'guard/unguard play', 'defences only guard the threat square and mates only exploit the unguard (not interesting)')
        kinds = {('self-block' if any('self-block' in w for m in e['mates'] for w in m['why_works']) else
                  'interference' if any('interference' in w for m in e['mates'] for w in m['why_works']) else
                  'line opening' if any('line opening' in w for m in e['mates'] for w in m['why_works']) else 'other') for e in ex}
        if len(kinds - {'other'}) >= 2:
            add('plus', 'varied motives', 'mates exploit different black errors: ' + ', '.join(sorted(kinds - {'other'})))
    except Exception:
        pass

    # --- self-pinning tries (E. Bourd s15)
    try:
        from .motives import self_pin_tries
        sp = self_pin_tries(problem, res)
        if sp and sp['tries']:
            add('plus', 'self-pinning tries',
                '; '.join(f"1.{x['try']}? pins {x['pinned']} -> 1...{x['refutation']}! (2.{x['mate_denied']} impossible)"
                          for x in sp['tries'])
                + ('; the key pins nothing' if sp['key_pins_nothing'] else ''))
    except Exception:
        pass

    # --- key extras: switchback / unpinning key (E. Bourd s11)
    try:
        from .motives import key_extras
        ke = key_extras(problem, res)
        for sb in ke['switchback']:
            add('plus', 'switchback', sb)
        for u in ke['unpins']:
            if u['new_defences']:
                add('plus', 'unpinning key', f"the key unpins {u['unit']}, creating "
                                             + ', '.join('1...' + d for d in u['new_defences']))
            else:
                add('minor', 'unpinning key', f"the key unpins {u['unit']} without gain")
    except Exception:
        pass

    # --- dual avoidance unity (E. Bourd s6)
    try:
        from .motives import dual_avoidance_after
        import chess as _c
        _k = _c.Move.from_uci(key['first_move']['uci'])
        _r = dual_avoidance_after(problem.board, _k)
        da = [{'defence': v['defence'], 'avoided': v['avoided']} for v in _r['variations']]
        kinds = set(_r['thematic_kinds'])
        if any(x['kind'] == 'DUAL' for it in da for x in it['avoided']):
            add('major', 'dual avoidance', 'a sibling mate is also mate: no dual avoidance')
        elif len(kinds) == 1:
            nth = len([v for v in _r['variations'] if v.get('by_half_battery', True)])
            where = f'the {nth} thematic defence(s)' if _r.get('half_batteries') else f'all {len(_r["variations"])} defences'
            add('plus', 'dual avoidance', f'unified across {where}: every sibling mate fails the same way ({list(kinds)[0]})')
        if _r.get('extras'):
            add('minor', 'extra play',
                'not by a half-battery unit: ' + ', '.join('1...' + e for e in _r['extras'])
                + ' (usually unavoidable; a cost unless it carries something of its own)')
        elif len(kinds) > 1:
            add('minor', 'dual avoidance', 'reasons differ (' + '; '.join(sorted(kinds)) + '): second-layer unity missing')
    except Exception:
        pass

    # --- set play: unprovided moves make the key obvious (taught)
    sp = next((p for p in res['phases'] if p['type'] == 'set'), None)
    if sp:
        unprov = sp.get('unprovided', [])
        checks = [u for u in unprov if u.endswith('+')]
        if checks:
            add('major', 'unprovided check', 'unprovided CHECK in the set play: ' + ', '.join(checks) + ' (fatal, E. Bourd)')
        if unprov and len(unprov) <= 2:
            add('minor', 'unprovided move', 'unprovided in diagram: ' + ', '.join(unprov) + ' (hints at the key)')

    # --- participation (taught: every piece should take part) + necessity
    use = mate_participation(problem, res)
    nec = piece_necessity(problem, res) if necessity else {}
    for sq in chess.SQUARES:
        p = board.piece_at(sq)
        if not p or p.color != chess.WHITE:
            continue
        name = chess.square_name(sq)
        if name in use:
            continue
        verdict = nec.get(name, '')
        own = [t['first_move']['san'] for t in tries if t['first_move']['uci'][:2] == name]
        for_soundness = verdict.startswith('needed') and 'CONTENT' not in verdict and 'SET PLAY' not in verdict
        if p.piece_type != chess.KING and sq != kmove.from_square and own and not for_soundness:
            # E. Bourd: a unit in no mate of the solution that only plays tries was fatal on 7 Oct 2026, a drawback
            # weighed against what the try buys since 11 Oct (24 Oct: he kept wPc2 for 1.cxd3?, the try that
            # "proves" the knight is unpinned before the key pins it). A unit the solution needs (a plug, a
            # cook-stopper) is not "only for a try" (18 Oct 2026: wPd7 cut Be8 from c6 in his Kc5 battery)
            add('major', 'try-only unit', f"{_pname(board, sq)} takes part in no mate of the solution; it only plays "
                                          + ', '.join('1.' + t + '?' for t in own) + ' (a drawback weighed against what the try buys, E. Bourd)')
            continue
        if p.piece_type == chess.KING:
            anchors = king_pin_anchor(problem, res)
            if anchors:
                add('plus', 'thematic king', f"{_pname(board, sq)} takes part in no mate but anchors a pin the defence creates: "
                                             + ', '.join(anchors))
            elif _king_stops_cooks(problem, res, sq):
                # E. Bourd (s30): "king specifically as cook-stopper is not a flaw, it's ok"
                add('note', 'cook-stopping king', f"{_pname(board, sq)} takes part in no mate but stops cooks where it stands")
            else:
                # E. Bourd (mentor issue #4): "passive king is ok, it's usually a piece that is hard to give a role
                # when many black pieces exist" - a note, not a flaw
                add('note', 'passive king', f"{_pname(board, sq)} takes part in no mate (acceptable, E. Bourd)")
        elif sq == kmove.from_square:
            # E. Bourd (8 Oct 2026): "it's more that it's a pawn compared to a rook. A completely useless
            # rook/bishop/knight/queen is usually fatal." A pawn that only plays the key is cheap; an officer is not.
            if p.piece_type == chess.PAWN:
                add('minor', 'passive piece', f"{_pname(board, sq)} takes part in no mate (forgivable: a pawn that plays the key)")
            else:
                add('major', 'useless key piece', f"{_pname(board, sq)} takes part in no mate: an officer whose only job is "
                                                  "the key is usually fatal (E. Bourd); a pawn would be forgivable")
        elif verdict.startswith('needed'):
            if 'SET PLAY' in verdict:
                add('major', 'set-play filler', f"{_pname(board, sq)} takes part in no mate; it only completes the set play "
                                                f"({verdict.split('SET PLAY: ', 1)[1]})")
            elif 'CONTENT' in verdict:
                add('plus', 'thematic unit', f"{_pname(board, sq)} takes part in no mate but carries content: "
                                             + verdict.split('CONTENT: ', 1)[1])
            else:
                why = verdict.replace('needed', '').strip(' ()')
                why = 'no solution without it' if why.startswith('no solution') else why
                # a unit that PLAYS a try taking part in a changed-mate relation is thematic, not a cook-stopper
                changed_phases = {ph for c in res.get('relations', {}).get('changed', []) for ph in c['phases']}
                my_tries = [t['first_move']['san'] for t in tries if t['first_move']['uci'][:2] == chess.square_name(sq)
                            and f"try {t['first_move']['san']}" in changed_phases]
                if my_tries and not why.startswith('no solution'):
                    add('major', 'try-only unit', f"{_pname(board, sq)} takes part in no mate of the solution; it only plays "
                                                  + ', '.join('1.' + t + '?' for t in my_tries) + ' (a drawback weighed against what the try buys, E. Bourd)')
                else:
                    also = (' and also plays ' + ', '.join('1.' + t + '?' for t in my_tries)) if my_tries else ''
                    add('minor', 'cook-stopper', f"{_pname(board, sq)} takes part in no mate; needed for soundness ({why}){also}")
        elif [t for t in tries if t['first_move']['uci'][:2] == name]:
            own = [t['first_move']['san'] for t in tries if t['first_move']['uci'][:2] == name]
            add('major', 'try-only unit', f"{_pname(board, sq)} takes part in no mate of the solution; it only plays "
                                          + ', '.join('1.' + t + '?' for t in own) + ' (a drawback weighed against what the try buys, E. Bourd)')
        else:
            add('major', 'superfluous piece', f"{_pname(board, sq)} takes part in no mate and is not needed for soundness")
    for name in set_play_only_units(problem, res):
        if name in use:     # in the key mates only as a duplicate guard
            sq = chess.parse_square(name)
            verdict = nec.get(name, '')
            msg = f"{_pname(board, sq)} gives set-play mates only; in every mate after the key its guards are duplicated"
            if verdict.startswith('needed (stops the dual'):
                # it also works in the solution: it keeps a thematic variation single (not a set-play-only unit)
                add('minor', 'set play + dual stopper', f"{_pname(board, sq)} gives set-play mates; after the key it "
                                                         + verdict[len('needed ('):-1])
            elif verdict.startswith('needed') and 'SET PLAY' not in verdict:
                # not completely redundant: it also holds soundness or the tries
                add('minor', 'set-play-only unit', msg + ' (still ' + verdict + ')')
            elif verdict:
                add('major', 'set-play-only unit', msg + ' and nothing else needs it (big flaw, E. Bourd)')
            else:
                add('minor', 'set-play-only unit', msg + ' (necessity not checked)')
    for sq, verdict in nec.items():
        p = board.piece_at(chess.parse_square(sq))
        if p.color == chess.BLACK and verdict.startswith('not needed'):
            add('minor', 'black piece role', f"{_pname(board, chess.parse_square(sq))}: {verdict}")

    # --- economy
    n = bin(board.occupied).count('1')
    pawns = len(board.pieces(chess.PAWN, True)) + len(board.pieces(chess.PAWN, False))
    add('plus' if n <= 9 else 'minor' if n > 16 else 'plus', 'economy', f'{n} units ({pawns} pawns)')

    # --- themes
    for p in res['relations'].get('patterns', []):
        if p['name'].startswith('Bristol') or p['name'] in ('Le Grand', 'Threat reversal', 'Pseudo Le Grand') or p['name'].startswith('Zagoruiko'):
            add('plus', 'theme', f"{p['name']}: {p.get('defence') or ', '.join(p.get('defences', []))}")
    if res['relations'].get('reciprocal'):
        add('plus', 'theme', 'reciprocal change')

    # --- second phase (E. Bourd, 18 Oct 2026): "anything that is a single phase without tries or changes is not pass
    # for publication unless the single phase is very complicated or pretty". A phase counts when a mate changes
    # (set or try against the key) or the tries form a thematic set; the exception is the judge's, not the gate's.
    # random tries do not count (E. Bourd, 18 Oct 2026: "i meant no thematic tries or changes. random tries dont
    # count"): a try set or distinct refutations alone are not a second phase
    second = {'thematic tries', 'white correction', 'self-pinning tries'}
    defences = {v['defence']['uci'] for v in real if not v['refutes']}
    refuted_by_defence = [t for t in tries if not t['first_move']['san'].endswith('+') and len(t['refutations']) == 1
                          and t['refutations'][0]['uci'] in defences]   # a try refuted by a thematic defence
    # a change counts only against the key, as the rule says (daily No. 19: a black pawn added to a single-phase
    # flight-giving key changed 1...e4 between the tries 1.Sf5? and 1.Sa6? and the gate passed it)
    # nor against a try refuted by a king move, which is no try (daily No. 20: 1.Scd4? Ke5! changed both self-block mates
    # against 1.Qc8! and the gate passed a single phase)
    vs_key = [c for c in res['relations'].get('changed') or [] if any(p.startswith('key ') for p in c['phases'])
              and not any(p in king_refuted for p in c['phases'])]
    if not vs_key and not refuted_by_defence \
            and not any(f['severity'] == 'plus' and f['rule'] in second for f in F):
        add('major', 'single phase', 'one phase: no changed mates and no thematic tries (random tries do not count); '
            'publishable only if the '
            'play is very complicated or pretty (E. Bourd, 18 Oct 2026)')
    # the second layer must reach every thematic variation (E. Bourd, mentor issue #21, 25 Oct 2026: "if the thematic
    # content consists of 2 variations, only 1 is not enough, its too short and usually spoils a lot. the extention has
    # to be aligned with both thematic variations somehow (tries, transfers and so on)"). Thematic variation here: a
    # key-phase defence whose single mate answers no other defence (random moves sharing one mate are not thematic).
    elif not any(f['severity'] == 'plus' and f['rule'] in second for f in F):
        mate_of = {v['defence']['san'].rstrip('+#'): v['continuations'][0]['san'] for v in real
                   if not v['refutes'] and len(v['continuations']) == 1}
        mates = Counter(mate_of.values())
        thematic = {d for d, m in mate_of.items() if mates[m] == 1 and not d.startswith('K')}   # a flight is the key's
        san_of = {v['defence']['uci']: v['defence']['san'].rstrip('+#') for v in real}
        covered = {san_of.get(t['refutations'][0]['uci']) for t in refuted_by_defence} | \
                  {c.get('defence', '').rstrip('+#') for c in vs_key}
        if len(thematic) >= 2 and len(covered & thematic) < 2:
            add('major', 'one-sided extension',
                f"the second layer reaches {len(covered & thematic)} of {len(thematic)} thematic variations "
                f"({', '.join(sorted(covered & thematic)) or 'none'} of {', '.join(sorted(thematic))}): "
                "it must be aligned with both (E. Bourd, mentor issue #21)")
    return {'findings': F, 'participation': use, 'necessity': nec}


_REFLECTIONS = {'file': lambda dx, dy: (-dx, dy), 'rank': lambda dx, dy: (dx, -dy),
                'diagonal': lambda dx, dy: (dy, dx), 'anti-diagonal': lambda dx, dy: (-dy, -dx)}


def _reflect(sq, k, t):
    dx, dy = t(chess.square_file(sq) - chess.square_file(k), chess.square_rank(sq) - chess.square_rank(k))
    f, r = chess.square_file(k) + dx, chess.square_rank(k) + dy
    return chess.square(f, r) if 0 <= f < 8 and 0 <= r < 8 else None


def simplicity(board, res, key, real, ksq):
    """E. Bourd (15 Oct 2026), on claude-type2-rooks-light/full: "this is too symmetrical and simple. The zugzwang and the
    piece moving from capture is bad. The random moves by the knights are annoying. ... the gate of passing needs to
    slightly increase." Yields (rule, severity, message). 'simple block' (major, fatal in the gate): a zugzwang whose
    thematic defences are all random moves of their units, or whose key piece only escapes a capture the set leaves
    unprovided."""
    from collections import Counter
    out = []
    zz = not key.get('threat')
    if zz:
        out.append(('zugzwang key', 'minor', 'the key threatens nothing (a block): zugzwang is limited and less '
                    'interesting than a threat (E. Bourd)'))
    groups = {}
    for v in real:
        if v['defence']['uci'][:2] != ksq:
            groups.setdefault(v['defence']['uci'][:2], []).append(frozenset(c['id'] for c in v['continuations']))
    rnd = {}
    for sq, ms in groups.items():
        top, n = Counter(ms).most_common(1)[0]
        if n >= 3:
            rnd[sq] = n
    if rnd:
        out.append(('random defences', 'minor', 'one mate answers many moves of the same unit ('
                    + ', '.join(f"{board.piece_at(chess.parse_square(s)).symbol().upper().replace('N', 'S')}{s}: {n} moves"
                                for s, n in rnd.items())
                    + '): random moves, not defences (E. Bourd: "the random moves by the knights are annoying")'))
    # symmetric play: the thematic mates (all phases) map onto themselves under a reflection through the black king
    k = board.king(chess.BLACK)
    mv = set()
    for ph in res['phases']:
        if ph['type'] in ('set', 'key'):
            for v in ph['variations']:
                if v['continuations'] and not v.get('threat_repeat') and v['defence']['uci'][:2] != ksq:
                    mv |= {(c['uci'][:2], c['uci'][2:4]) for c in v['continuations']}
    mvs = {(chess.parse_square(a), chess.parse_square(b)) for a, b in mv}
    for name, t in _REFLECTIONS.items():
        img = {(_reflect(a, k, t), _reflect(b, k, t)) for a, b in mvs}
        moved = [m for m in mvs if (_reflect(m[0], k, t), _reflect(m[1], k, t)) != m]
        if len(moved) >= 4 and img == mvs:
            out.append(('symmetric play', 'minor', f'the mates map onto each other in the {name} through the king '
                        '(E. Bourd: "too symmetrical")'))
            break
    escape = False
    kmove = chess.Move.from_uci(key['first_move']['uci'])
    if board.piece_type_at(kmove.from_square) != chess.KING and black_captures(board, kmove.from_square):
        escape = bool(key_piece_captures_unprovided(board, kmove, res['phases']))
    allrandom = bool(groups) and all(sq in rnd for sq in groups)
    if zz and (allrandom or escape):
        out.append(('simple block', 'major', 'a zugzwang ' + ('whose defences are random moves of their units'
                    if allrandom else 'whose key piece escapes a capture the set leaves unprovided')
                    + ': too simple to publish (E. Bourd, 15 Oct 2026: "the gate of passing needs to slightly increase")'))
    return out


def black_captures(board, sq):
    """Squares of the Black units that can legally capture on sq (Black to move). A king attack on a protected
    unit is no attack, nor is one by a pinned unit (E. Bourd, bench 10 Oct 2026: 1.Se6-f4 with Bg4 guarding e6
    was flagged as an attacked key piece)."""
    b = board.copy(stack=False); b.turn = chess.BLACK; b.ep_square = None
    return sorted({chess.square_name(m.from_square) for m in b.legal_moves if m.to_square == sq})


def key_piece_set_roles(board, kmove, phases):
    """Set mates that need the key piece on its diagram square: it gives the mate, or without it the position after
    the mate is no mate. Returns {mate SAN: [defence SANs]} in set-play order."""
    fsq, roles = kmove.from_square, {}
    for ph in phases:
        if ph['type'] != 'set':
            continue
        for v in ph['variations']:
            for c in v['continuations']:
                b = board.copy(stack=False); b.turn = chess.BLACK; b.ep_square = None
                d = chess.Move.from_uci(v['defence']['uci'])
                if d.to_square == fsq or d not in b.legal_moves:
                    continue
                b.push(d)
                m = chess.Move.from_uci(c['uci'])
                if m not in b.legal_moves:
                    continue
                b.push(m)
                need = m.from_square == fsq
                if not need and b.piece_at(fsq) is not None:
                    b.remove_piece_at(fsq)
                    need = not b.is_checkmate()
                if need:
                    roles.setdefault(c['san'], []).append(v['defence']['san'])
    return roles


def key_piece_captures_unprovided(board, kmove, phases):
    """Black captures of the key piece on its diagram square that have no set mate."""
    fsq = kmove.from_square
    return [v['defence']['san'] for ph in phases if ph['type'] == 'set' for v in ph['variations']
            if chess.Move.from_uci(v['defence']['uci']).to_square == fsq and not v['continuations']]


def format_critique(c):
    order = {'major': 0, 'minor': 1, 'note': 2, 'plus': 3}     # 'note': a cook-stopping king (E. Bourd), no flaw
    icon = {'major': '✗✗', 'minor': '✗ ', 'note': '· ', 'plus': '✓ '}
    lines = [f"{icon[f['severity']]} [{f['rule']}] {f['msg']}" for f in sorted(c['findings'], key=lambda f: order[f['severity']])]
    return '\n'.join(lines)


def idle_key_piece(board, kmove, phases):
    """E. Bourd (session 29): in the diagram the key piece guards no square of the black king's field, gives
    no set mate and blocks no line of another line piece. phases: the analysis phases (for the set play)."""
    fsq, bk = kmove.from_square, board.king(chess.BLACK)
    field = chess.SquareSet(chess.BB_KING_ATTACKS[bk]) | chess.SquareSet.from_square(bk)
    if board.attacks(fsq) & field:
        return False
    if any(c['uci'][:2] == chess.square_name(fsq) for ph in phases if ph['type'] == 'set'
           for v in ph['variations'] for c in v['continuations']):
        return False
    # E. Bourd (8 Oct 2026, 1.d7! in 8/4K3/2pP1P2/2rpk3/1Qbp1RP1/2np4/6N1/8): a key piece that stands on the
    # line or the square of the threat or of a mate after the key has a role - it vacates it (the d6 pawn blocks
    # Qb8-e5 and occupies d6 for Qd6#)
    for ph in phases:
        if ph['type'] != 'key':
            continue
        conts = list(ph.get('threat') or []) + [c for v in ph['variations'] for c in v['continuations']]
        for c in conts:
            m = chess.Move.from_uci(c['uci'])
            if fsq == m.to_square or fsq in chess.SquareSet(chess.between(m.from_square, m.to_square)) \
                    or fsq in chess.SquareSet(chess.between(m.to_square, bk)):
                return False
    empty = board.copy(); empty.remove_piece_at(fsq)
    for sq in chess.SquareSet(board.occupied):
        if sq != fsq and board.piece_type_at(sq) in (chess.BISHOP, chess.ROOK, chess.QUEEN) and empty.attacks(sq) != board.attacks(sq):
            return False
    return True


def out_of_play_key(board, kmove):
    """E. Bourd (7 Oct 2026, daily No. 2): a piece on the edge, three or more squares from the black king,
    guarding no square of its field, makes the key obvious (fatal). Knights and bishops first; queens and rooks
    since 8 Oct 2026 ("very bad key, queen completely out of play", on 1.Qb1 from h1)."""
    bk = board.king(chess.BLACK)
    kfield = chess.BB_KING_ATTACKS[bk] | chess.BB_SQUARES[bk]
    f0, r0 = chess.square_file(kmove.from_square), chess.square_rank(kmove.from_square)
    return (board.piece_type_at(kmove.from_square) in (chess.KNIGHT, chess.BISHOP, chess.ROOK, chess.QUEEN) and (f0 in (0, 7) or r0 in (0, 7))
            and chess.square_distance(kmove.from_square, bk) >= 3 and not int(board.attacks(kmove.from_square)) & kfield)
