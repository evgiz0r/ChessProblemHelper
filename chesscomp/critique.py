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
from .core import Problem, san
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
        for v in ph['variations']:
            if v['threat_repeat'] or not v['continuations']:
                continue
            for c in v['continuations']:
                b2 = b1.copy(); b2.push(chess.Move.from_uci(v['defence']['uci']))
                om = after(c['uci'], b2)
                yield f"1...{v['defence']['san']} 2.{c['san']}", b2, om


def mate_participation(problem, res):
    """For each White piece (by diagram square): the mates in which it takes part.
    Takes part = gives check, guards a square of the king's field (incl. the square of an adjacent
    White piece), or pins a Black piece. Also records squares guarded more than once (impurity)."""
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
        for sq in chess.SquareSet(b.occupied_co[chess.WHITE]):
            att = int(b.attacks(sq))
            if (att & fmask) or (sq in checkers) or (chess.BB_SQUARES[sq] & pinned_lines and b.piece_type_at(sq) != chess.PAWN):
                use.setdefault(chess.square_name(om.get(sq, sq)), []).append(label)
    return use


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
        if keys == [key]:
            k0 = [ph for ph in r['phases'] if ph['type'] == 'key'][0]
            real = [v for v in k0['variations'] if not v['threat_repeat'] and v['continuations']]
            duals = [v for v in real if v['dual']]
            base_k = [ph for ph in res['phases'] if ph['type'] == 'key'][0]
            base_real = [v for v in base_k['variations'] if not v['threat_repeat'] and v['continuations']]
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
            if lost_tries:
                out[chess.square_name(sq)] = ('needed for the CONTENT: without it the tries '
                                              + ', '.join('1.' + t + '?' for t in sorted(lost_tries)) + ' are lost')
            elif lost_changes:
                out[chess.square_name(sq)] = ('needed for the CONTENT: without it the changed mate(s) after '
                                              + ', '.join(sorted({'1...' + d for d, _ in lost_changes})) + ' are lost')
            elif duals:
                out[chess.square_name(sq)] = ('needed for the CONTENT: without it ' +
                    ', '.join(f"1...{v['defence']['san']} allows {'/'.join(c['san'] for c in v['continuations'])}" for v in duals[:2]))
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


def critique(problem: Problem, res: dict | None = None, necessity: bool = True) -> dict:
    res = res or analyse(problem, max_refutations=1)
    F = []
    add = lambda sev, rule, msg: F.append({'severity': sev, 'rule': rule, 'msg': msg})
    board = problem.board
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
        add('minor', 'capture key', 'the key captures')
    b = board.copy(); b.turn = chess.BLACK
    flights_before = set(m.to_square for m in b.legal_moves if m.from_square == b.king(chess.BLACK)) if b.is_valid() else set()
    after = board.copy(); after.push(kmove)
    flights_after = set(m.to_square for m in after.legal_moves if m.from_square == after.king(chess.BLACK))
    if flights_after - flights_before:
        add('plus', 'flight-giving key', 'key gives flight(s): ' + ', '.join(chess.square_name(s) for s in flights_after - flights_before))
    if flights_before - flights_after:
        add('minor', 'flight-taking key', 'key takes flight(s): ' + ', '.join(chess.square_name(s) for s in flights_before - flights_after))
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
    themed = {x['phases'][0] for x in res['relations'].get('patterns', []) if 'interference try' in x['name']}
    thematic_label = lambda t: f"try {t['first_move']['san']}" in themed
    pool = same_threat if len(same_threat) >= 2 else [t for t in tries if t['first_move']['uci'][:2] == key_piece_sq
                                                      and (not themed or thematic_label(t))]
    them_refs = [(t['first_move']['san'], r['uci'], r['san']) for t in pool for r in t['refutations']]
    rc = Counter(u for _, u, _ in them_refs)
    for u, n in rc.items():
        if n > 1:
            s_ = next(x[2] for x in them_refs if x[1] == u)
            add('major' if n > 2 or u[:2] == ksq else 'minor', 'same refutation', f'1...{s_}! refutes {n} thematic tries')
    if themed:
        other = Counter(u for _, u, _ in refs) - rc
        for u, n in other.items():
            if n > 1:
                s_ = next(x[2] for x in refs if x[1] == u)
                add('minor', 'mechanism refutation', f'1...{s_}! refutes {n} non-thematic tries by the key piece (forcing mechanism)')
    thematic_tries = [t for t in tries if t['first_move']['uci'][:2] == key['first_move']['uci'][:2]]
    if themed:
        add('plus', 'thematic tries', 'White interference tries: ' + '; '.join(x['defence'] for x in res['relations']['patterns'] if 'interference try' in x['name']))
    if len(thematic_tries) >= 2 and len({r['uci'] for t in thematic_tries for r in t['refutations']}) == len(thematic_tries):
        add('plus', 'distinct refutations', f'{len(thematic_tries)} tries by the key piece, each refuted differently')

    # --- defences
    real = [v for v in key['variations'] if not v['threat_repeat'] and v['continuations']]
    duals = [v for v in real if v['dual']]
    for v in duals:
        add('major' if len(real) <= 2 else 'minor', 'dual', f"1...{v['defence']['san']} allows {'/'.join(c['san'] for c in v['continuations'])}")
    nk = [v for v in real if v['defence']['uci'][:2] != ksq]
    kv = [v for v in real if v['defence']['uci'][:2] == ksq]
    if len(nk) < 2:
        add('major', 'thin play', f'only {len(nk)} non-king defence(s)')
    for v in kv:
        add('minor', 'king flight variation', f"1...{v['defence']['san']} is a king flight (easy to see)")
    mates = {c['id'] for v in real for c in v['continuations']}
    if len(real) >= 3 and len(mates) >= 3:
        add('plus', 'varied play', f'{len(real)} defences, {len(mates)} different mates')

    # --- content: guard/unguard-only play is uninteresting (E. Bourd s2)
    try:
        from .motives import explain_key_phase
        ex = explain_key_phase(problem, res)
        if ex and all(all('guard' in w for w in e['why_defends']) and
                      all(all('unguard' in w or 'available anyway' in w for w in m['why_works']) for m in e['mates'])
                      for e in ex):
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
        if p.piece_type == chess.KING:
            anchors = king_pin_anchor(problem, res)
            if anchors:
                add('plus', 'thematic king', f"{_pname(board, sq)} takes part in no mate but anchors a pin the defence creates: "
                                             + ', '.join(anchors))
            else:
                add('minor', 'passive king', f"{_pname(board, sq)} takes part in no mate (acceptable if placed only to avoid checks)")
        elif sq == kmove.from_square:
            add('minor', 'passive piece', f"{_pname(board, sq)} takes part in no mate (forgivable: it plays the key)")
        elif verdict.startswith('needed'):
            if 'SET PLAY' in verdict:
                add('minor', 'set-play filler', f"{_pname(board, sq)} takes part in no mate; it only completes the set play "
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
                if my_tries:
                    add('plus', 'thematic unit', f"{_pname(board, sq)} takes part in no mate but plays the thematic try "
                                                 + ', '.join('1.' + t + '?' for t in my_tries) + ' (changed mates)')
                else:
                    add('minor', 'cook-stopper', f"{_pname(board, sq)} takes part in no mate; needed for soundness ({why})")
        else:
            add('major', 'superfluous piece', f"{_pname(board, sq)} takes part in no mate and is not needed for soundness")
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
    return {'findings': F, 'participation': use, 'necessity': nec}


def format_critique(c):
    order = {'major': 0, 'minor': 1, 'plus': 2}
    icon = {'major': '✗✗', 'minor': '✗ ', 'plus': '✓ '}
    lines = [f"{icon[f['severity']]} [{f['rule']}] {f['msg']}" for f in sorted(c['findings'], key=lambda f: order[f['severity']])]
    return '\n'.join(lines)
