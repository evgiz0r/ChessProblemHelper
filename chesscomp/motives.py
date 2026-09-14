"""Motives: explain, in composer vocabulary, WHY a Black defence defeats the threat and WHY the White
answer works. This is the layer that lets an AI talk about a problem the way a composer does
(self-block, interference, unguard, line opening, flight, guard of the mating square...), and the
building block for theme detectors such as Grimshaw.
"""
from __future__ import annotations
import chess
from .core import san

N = {chess.KING: 'K', chess.QUEEN: 'Q', chess.ROOK: 'R', chess.BISHOP: 'B', chess.KNIGHT: 'S', chess.PAWN: ''}


def nm(b, sq):
    p = b.piece_at(sq)
    return f"{N[p.piece_type] or 'P'}{chess.square_name(sq)}" if p else chess.square_name(sq)


def between(a, c):
    return chess.SquareSet(chess.between(a, c))


def _escapes(b):
    """Black to move and in check: how does Black get out? (king moves, captures of checker, blocks)"""
    out = []
    k = b.king(chess.BLACK)
    chk = list(b.checkers())
    for m in b.legal_moves:
        if m.from_square == k:
            out.append(('flight', m))
        elif chk and m.to_square in chk:
            out.append(('capture', m))
        else:
            out.append(('block', m))
    return out


def defence_motives(b_key: chess.Board, d: chess.Move, threats: list[chess.Move]) -> list[str]:
    """b_key: position after the key (Black to move). Why does defence d stop the threat(s)?"""
    mot = []
    b1 = b_key.copy(); dn = nm(b1, d.from_square); dsan = san(b1, d); b1.push(d)
    if b1.is_check():
        mot.append('check')
    if b_key.piece_at(d.to_square) and b_key.color_at(d.to_square) == chess.WHITE:
        cap = d.to_square
        for t in threats:
            if b_key.is_attacked_by(chess.WHITE, t.to_square):
                bb = b_key.copy(); bb.remove_piece_at(cap)
                if not bb.is_attacked_by(chess.WHITE, t.to_square) or chess.square_distance(cap, t.to_square) == 1:
                    mot.append(f'captures {nm(b_key, cap)}, the guard of the threat square {chess.square_name(t.to_square)}')
    for t in threats:
        tn = nm(b_key, t.from_square)
        if t not in b1.legal_moves:
            if d.to_square == t.from_square:
                mot.append(f'captures the threat piece {tn}')
            elif d.to_square in between(t.from_square, t.to_square):
                mot.append(f'blocks the threat line of {tn} (on {chess.square_name(d.to_square)})')
            elif b1.is_pinned(chess.WHITE, t.from_square):
                mot.append(f'pins {tn}')
            elif not b1.is_check():
                mot.append(f'stops {san(b_key, t)}')
            continue
        b2 = b1.copy(); b2.push(t)
        if b2.is_checkmate():
            continue
        for kind, e in _escapes(b2):
            es = chess.square_name(e.to_square)
            if kind == 'flight':
                if e.to_square == d.from_square:
                    mot.append(f'vacates {es} as a flight')
                else:
                    b0 = b_key.copy(); b0.push(chess.Move.null()) if b0.turn == chess.BLACK else None
                    mot.append(f'creates flight {es}')
            elif kind == 'capture' and b_key.is_pinned(chess.BLACK, e.from_square) and not b1.is_pinned(chess.BLACK, e.from_square):
                how = 'captures the pinner' if b_key.piece_at(d.to_square) else 'interposes on the pin line'
                mot.append(f'unpins {nm(b2, e.from_square)} ({how}), which can then take on {es}')
            elif kind == 'capture':
                cap = nm(b2, e.from_square)
                if e.from_square == d.to_square:
                    mot.append(f'guards the threat square: {dn[0]}{chess.square_name(d.to_square)} now covers {es}')
                else:
                    mot.append(f'opens {cap} to the mating square {es}')
            elif kind == 'block':
                mot.append(f'prepares interposition {san(b2, e)}')
    # dedupe keep order
    if any(m.startswith('captures ') and 'guard of the threat' in m for m in mot):
        mot = [m for m in mot if not m.startswith('creates flight')]
    seen, res = set(), []
    for m in mot:
        if m not in seen:
            seen.add(m); res.append(m)
    return res


def mate_motives(b_key: chess.Board, d: chess.Move, mate: chess.Move) -> list[str]:
    """Why does `mate` work after defence d (and what did d give away)?"""
    mot = []
    b1 = b_key.copy(); dn = nm(b1, d.from_square); b1.push(d)
    after = b1.copy(); after.push(mate)
    if b1.is_check() and mate.to_square == d.to_square:
        mot.append('cross-check: the checking piece is captured with mate')
    k = after.king(chess.BLACK)
    # 1) line opening: d vacated a square on the mating move's path or on the checking line
    path = between(mate.from_square, mate.to_square) | between(mate.to_square, k)
    if d.from_square in path:
        mot.append(f'black line opening: {dn} vacated {chess.square_name(d.from_square)} for {nm(b1, mate.from_square)}')
    # 2) self-block: the defender stands next to its king and would otherwise be a flight
    if d.to_square in chess.SquareSet(chess.BB_KING_ATTACKS[k]) and mate.to_square != d.to_square:
        t = after.copy(); t.remove_piece_at(d.to_square)
        if not t.is_checkmate():
            mot.append(f'self-block on {chess.square_name(d.to_square)}')
    # 3) compare with the same mate attempted without the defence: what did d take away?
    b0 = b_key.copy(); b0.push(chess.Move.null())
    if mate in b0.legal_moves:
        a0 = b0.copy(); a0.push(mate)
        if a0.is_checkmate():
            mot.append('mate available anyway (threat-like)')
        elif a0.is_check():
            for kind, e in _escapes(a0):
                if e in after.legal_moves:
                    continue
                piece = nm(a0, e.from_square)
                es = chess.square_name(e.to_square)
                if e.from_square == d.from_square:
                    mot.append(f'unguard: {piece} left its post (no longer {kind}s via {es})')
                elif d.to_square in between(e.from_square, e.to_square):
                    mot.append(f'black interference: {dn[0]}{chess.square_name(d.to_square)} cuts {piece} from {es}')
                elif kind == 'flight' and e.to_square == d.to_square:
                    pass  # covered by self-block
                elif after.is_pinned(chess.BLACK, e.from_square) and not a0.is_pinned(chess.BLACK, e.from_square):
                    mot.append(f'self-pin: {piece} pinned')
    else:
        mot.append(f'mate made possible by the defence (square/line given by {dn})')
    seen, res = set(), []
    for m in mot:
        if m not in seen:
            seen.add(m); res.append(m)
    return res or ['(no specific motive found)']


def defence_strength(board, d_uci, dmot):
    """E. Bourd s1: simple pawn defences opening lines for the king are weak; pieces moving/leaving squares better."""
    b = board
    mv = chess.Move.from_uci(d_uci)
    pt = b.piece_type_at(mv.from_square)
    if pt == chess.KING:
        return 'king flight (weak)'
    flighty = any('flight' in m for m in dmot)
    if pt == chess.PAWN:
        return 'simple pawn defence' + (' opening a flight (weak)' if flighty else '')
    if pt in (chess.QUEEN, chess.ROOK):
        return 'heavy-piece defence'
    return 'piece defence'


def explain_key_phase(problem, res) -> list[dict]:
    """For the key phase: each real defence with its defence motives, mate, mate motives, strength."""
    out = []
    for ph in res.get('phases', []):
        if ph['type'] != 'key':
            continue
        b = problem.board.copy(); b.push(chess.Move.from_uci(ph['first_move']['uci']))
        threats = [chess.Move.from_uci(t['uci']) for t in ph['threat']]
        for v in ph['variations']:
            if v['threat_repeat'] or not v['continuations']:
                continue
            d = chess.Move.from_uci(v['defence']['uci'])
            dm = defence_motives(b, d, threats)
            item = {'defence': v['defence']['san'], 'defence_uci': v['defence']['uci'], 'why_defends': dm,
                    'strength': defence_strength(b, v['defence']['uci'], dm), 'mates': []}
            for c in v['continuations']:
                item['mates'].append({'mate': c['san'], 'why_works': mate_motives(b, d, chess.Move.from_uci(c['uci']))})
            out.append(item)
    return out


def detect_half_pin(board: chess.Board, explained: list[dict]) -> list[dict]:
    """Half-pin: two Black pieces on one line between a White line piece and the Black king; when one
    moves, the other is left pinned, and the mates exploit that self-pin (both pieces defend)."""
    k = board.king(chess.BLACK)
    found = []
    for sq in chess.SquareSet(board.occupied_co[chess.WHITE]):
        if board.piece_type_at(sq) not in (chess.QUEEN, chess.ROOK, chess.BISHOP) or not (board.attacks(sq) | chess.BB_SQUARES[sq]):
            continue
        ray = chess.SquareSet(chess.between(sq, k))
        if not ray or chess.square_file(sq) != chess.square_file(k) and chess.square_rank(sq) != chess.square_rank(k) \
                and abs(chess.square_file(sq) - chess.square_file(k)) != abs(chess.square_rank(sq) - chess.square_rank(k)):
            continue
        pt = board.piece_type_at(sq)
        diag = chess.square_file(sq) != chess.square_file(k) and chess.square_rank(sq) != chess.square_rank(k)
        if (diag and pt == chess.ROOK) or (not diag and pt == chess.BISHOP):
            continue
        occ = [x for x in ray if board.piece_at(x)]
        if len(occ) == 2 and all(board.color_at(x) == chess.BLACK for x in occ):
            a, b = [chess.square_name(x) for x in occ]
            used = {a: 0, b: 0}
            for e in explained:
                frm = e['defence_uci'][:2]
                other = b if frm == a else a if frm == b else None
                if other and any('self-pin' in w and other in w for m in e['mates'] for w in m['why_works']):
                    used[frm] += 1
            if used[a] and used[b]:
                found.append({'name': 'Half-pin', 'line': f"{nm(board, sq)}-{chess.square_name(k)}",
                              'pieces': [nm(board, occ[0]), nm(board, occ[1])], 'variations': sum(used.values())})
    return found


def detect_grimshaw(explained: list[dict]) -> list[dict]:
    """Two defences on the same square by different Black pieces, each mate exploiting interference
    with the OTHER piece (Grimshaw, or Novotny-type if White forced it)."""
    found = []
    by_sq = {}
    for e in explained:
        by_sq.setdefault(e['defence_uci'][2:4], []).append(e)
    for sq, es in by_sq.items():
        for i in range(len(es)):
            for j in range(i + 1, len(es)):
                a, b = es[i], es[j]
                if a['defence_uci'][:2] == b['defence_uci'][:2]:
                    continue
                ia = any('interference' in w and b['defence_uci'][:2] in w for m in a['mates'] for w in m['why_works'])
                ib = any('interference' in w and a['defence_uci'][:2] in w for m in b['mates'] for w in m['why_works'])
                if ia and ib:
                    found.append({'name': 'Grimshaw', 'square': sq, 'defences': [a['defence'], b['defence']],
                                  'mates': [a['mates'][0]['mate'], b['mates'][0]['mate']]})
    return found


def format_explained(explained):
    lines = []
    for e in explained:
        lines.append(f"1...{e['defence']}  [{e['strength']}]")
        lines.append(f"     defends: {'; '.join(e['why_defends']) or '-'}")
        for m in e['mates']:
            lines.append(f"     2.{m['mate']}: {'; '.join(m['why_works'])}")
    return '\n'.join(lines)


def _no_check_reason(after: chess.Board, mate: chess.Move) -> str:
    """The sibling mate gives no check here. Say why when it is a battery whose line is still closed
    (E. Bourd s21: 2.Sxg3? after 1...Qxe5 fails because Bd4 still closes the c4-f4 line, not because
    a knight can capture on g3)."""
    k = after.king(chess.BLACK)
    if k is None:
        return 'no check'
    for x in chess.SquareSet(after.occupied_co[chess.WHITE]):
        pt = after.piece_type_at(x)
        if pt not in (chess.ROOK, chess.BISHOP, chess.QUEEN):
            continue
        between = chess.SquareSet.between(x, k)
        if mate.from_square not in between:
            continue
        orth = chess.square_file(x) == chess.square_file(k) or chess.square_rank(x) == chess.square_rank(k)
        if (orth and pt == chess.BISHOP) or (not orth and pt == chess.ROOK):
            continue
        blockers = [nm(after, s) for s in between if after.piece_at(s)]
        if blockers:
            return f"no check (the battery {nm(after, x)}-{chess.square_name(k)} is still closed by {', '.join(blockers)})"
    return 'no check'


def _avoid_kind(before: chess.Board, d: chess.Move, mate: chess.Move, after: chess.Board, esc: chess.Move):
    """Classify WHY a sibling mate fails: the composer's 'second layer' of unity (E. Bourd, s6/s7)."""
    who_sq = esc.from_square
    who = nm(after, who_sq)
    # did the defence OPEN a line for this piece? (put the defender back and see if the escape dies)
    opened = False
    if who_sq != d.to_square:
        t = after.copy()
        t.remove_piece_at(d.to_square)
        pc = before.piece_at(d.from_square)
        if pc and not t.piece_at(d.from_square):
            t.set_piece_at(d.from_square, pc)
            opened = esc not in t.legal_moves
    # a move that gives no check is not refuted by anything Black does: say so first, or the first legal
    # capture of the "mating" unit is reported as the reason (a battery whose line is still closed)
    if not after.is_check():
        return _no_check_reason(after, mate), who
    if esc.to_square == mate.to_square:
        act = f'captures on {chess.square_name(mate.to_square)}'
    elif who_sq == after.king(chess.BLACK):
        return f'king flight to {chess.square_name(esc.to_square)}', who
    else:
        act = f'interposes on {chess.square_name(esc.to_square)}'
    if who_sq == d.to_square:
        return f'defender retains control ({act})', who
    if opened:
        return f'line opened by the defence ({who} {act})', who
    return f'another unit ({who} {act})', who


RANK = ['defender retains control', 'line opened by the defence', 'another unit', 'interposition',
        'king flight', 'no check', 'DUAL']


def _rank(kind):
    k = kind.split(' (')[0].split(' to ')[0]
    return RANK.index(k) if k in RANK else len(RANK)


def dual_avoidance_after(board: chess.Board, first: chess.Move | None, only_squares=None, only_from=None):
    """Dual avoidance among the thematic defences after ANY first move (key OR try).

    Returns a list of {'defence','mate','avoided':[{'mate','refutation','kind'}]} plus a unity verdict.
    only_squares: restrict to defences ARRIVING on these squares (e.g. {'f6'}) - the usual unity device.
    only_from: restrict to defences BY units standing on these squares.
    """
    b0 = board.copy()
    if first is not None:
        b0.push(first)          # board was White to move (a diagram): play the key/try
    # else: board is already the post-key position with Black to move
    # the threat: moves answered by it are not defences and must not enter the avoidance analysis
    t0 = b0.copy(); t0.push(chess.Move.null())
    threat = set()
    for m in list(t0.legal_moves):
        t0.push(m)
        if t0.is_checkmate():
            threat.add(m.uci())
        t0.pop()
    defs = {}
    for d in b0.legal_moves:
        if only_squares and chess.square_name(d.to_square) not in only_squares:
            continue
        if only_from and chess.square_name(d.from_square) not in only_from:
            continue
        t = b0.copy(); dn = san(t, d); t.push(d)
        ms = []
        for m in list(t.legal_moves):
            t.push(m)
            if t.is_checkmate():
                ms.append(m)
            t.pop()
        if len(ms) == 1 and ms[0].uci() not in threat:
            defs[d] = (dn, ms[0])
    mates = {m.uci() for _, (_, m) in defs.items()}
    out, kinds = [], set()
    for d, (dn, m) in defs.items():
        t = b0.copy(); t.push(d)
        item = {'defence': dn, 'mate': san(t, m), 'avoided': []}
        for o in sorted(mates - {m.uci()}):
            ov = chess.Move.from_uci(o)
            tt = b0.copy(); tt.push(d)
            if ov not in tt.legal_moves:
                continue
            osan = san(tt, ov); tt.push(ov)
            if tt.is_checkmate():
                item['avoided'].append({'mate': osan, 'refutation': None, 'kind': 'DUAL'})
                kinds.add('DUAL'); continue
            esc = list(tt.legal_moves)
            if not esc:
                continue
            # classify EVERY escape and keep the most thematic one - taking the first legal move
            # hides the real motive (e.g. 2.Qe5? Kd3 listed before the thematic Bxe5!)
            options = []
            for e in esc:
                k, w = _avoid_kind(b0, d, ov, tt, e)
                options.append((_rank(k), k, w, e))
            options.sort(key=lambda x: x[0])
            _, kind, who, best = options[0]
            item['avoided'].append({'mate': osan, 'refutation': san(tt, best), 'kind': kind,
                                    'all': [f'{san(tt, e)} ({k})' for _, k, _, e in options]})
            kinds.add(kind.split(' (')[0])
        out.append(item)
    # the THEMATIC reason per defence is the most specific one (defender's own retained control,
    # or a line it opened), not the incidental guard by a unit that never moved
    hb = find_half_batteries(board)
    hb_units = set()
    for h in hb:
        hb_units |= set(h['units'])
    for it in out:
        av = sorted(it['avoided'], key=lambda x: _rank(x['kind']))
        it['thematic'] = av[0] if av else None
        d = next((m for m in b0.legal_moves if san(b0, m) == it['defence']), None)
        it['by_half_battery'] = bool(hb_units) and d is not None and chess.square_name(d.from_square) in hb_units
    core = [it for it in out if it['by_half_battery']] if hb_units else out
    tk = {it['thematic']['kind'].split(' (')[0].split(' to ')[0] for it in core if it.get('thematic')}
    return {'first': san(board, first) if first is not None else '(post-key)', 'variations': out,
            'kinds': sorted(kinds), 'thematic_kinds': sorted(tk),
            'half_batteries': hb, 'extras': [it['defence'] for it in out if not it['by_half_battery']] if hb_units else [],
            'unified': len(tk) == 1 and 'DUAL' not in tk}


def format_dual_avoidance_after(res):
    lines = [f"1.{res['first']} :"]
    if res.get('half_batteries'):
        h = res['half_batteries'][0]
        lines.append(f"   half-battery {h['pinner']}: {h['names'][0]} + {h['names'][1]}")
    for it in res['variations']:
        marks = ' '.join(f"(2.{x['mate']}? {x['kind']})" if x['kind'].startswith('no check')
                         else f"(2.{x['mate']}? {x['refutation']}!  {x['kind']})" if x['refutation']
                         else f"(2.{x['mate']}? also mate - DUAL)" for x in it['avoided'])
        tag = '' if it.get('by_half_battery', True) else '   [extra play - not a half-battery unit]'
        lines.append(f"   1...{it['defence']} 2.{it['mate']}  {marks}{tag}".rstrip())
    lines.append('   [unified avoidance across the thematic defences: ' + res['thematic_kinds'][0] + ']'
                 if res['unified'] else
                 '   [avoidance motives differ: ' + '; '.join(res['thematic_kinds']) + ']')
    return '\n'.join(lines)


def dual_avoidance(problem, res) -> list[dict]:
    """For each thematic variation, WHY does each of the sibling mates fail there? (E. Bourd, session 6)

    This is the underlying motive of a dual-avoidance problem and is often marked explicitly in solutions:
        1...Rg3 2.Qxd4#  (2.Qxe6? Rxe6!)
        1...Sg3 2.Qxe6#  (2.Qxd4? Kf5!)
    The KIND of reason matters for unity: if one mate is refuted by a capture from the freed unit and the
    other by a king flight, the second layer of unity is missing.
    """
    out = []
    for ph in res.get('phases', []):
        if ph['type'] != 'key':
            continue
        b0 = problem.board.copy(); b0.push(chess.Move.from_uci(ph['first_move']['uci']))
        thematic = [v for v in ph['variations']
                    if not v['threat_repeat'] and len(v['continuations']) == 1]
        mates = {v['continuations'][0]['uci'] for v in thematic}
        for v in thematic:
            mine = v['continuations'][0]
            item = {'defence': v['defence']['san'], 'mate': mine['san'], 'avoided': []}
            b = b0.copy(); b.push(chess.Move.from_uci(v['defence']['uci']))
            for other in sorted(mates - {mine['uci']}):
                mv = chess.Move.from_uci(other)
                if mv not in b.legal_moves:
                    item['avoided'].append({'mate': other, 'kind': 'not playable', 'refutation': None,
                                            'text': 'not playable'})
                    continue
                a = b.copy(); msan = san(a, mv); a.push(mv)
                if a.is_checkmate():
                    item['avoided'].append({'mate': msan, 'kind': 'DUAL', 'refutation': None, 'text': 'also mate (dual!)'})
                    continue
                esc = list(a.legal_moves)
                if not esc:
                    continue
                e = esc[0]
                if not a.is_check():
                    kind = _no_check_reason(a, mv)
                elif e.to_square == mv.to_square:
                    kind = f'capture of the mating unit by {nm(a, e.from_square)}'
                elif e.from_square == a.king(chess.BLACK):
                    kind = f'king flight to {chess.square_name(e.to_square)}'
                else:
                    kind = 'interposition'
                item['avoided'].append({'mate': msan, 'kind': kind, 'refutation': None if kind.startswith('no check') else san(a, e),
                                        'text': f"2.{msan}? {kind}" if kind.startswith('no check') else f"2.{msan}? {san(a, e)}!"})
            out.append(item)
    return out


def format_dual_avoidance(da):
    lines = []
    for it in da:
        marks = ' '.join(f"({x['text']})" for x in it['avoided'] if x['text'] != 'not playable')
        lines.append(f"   1...{it['defence']} 2.{it['mate']}  {marks}".rstrip())
    kinds = {x['kind'].split(' to ')[0].split(' by ')[0] for it in da for x in it['avoided'] if x['refutation']}
    if len(kinds) == 1 and da:
        lines.append(f"   [unified avoidance: every sibling mate fails the same way - {kinds.pop()}]")
    elif len(kinds) > 1:
        lines.append('   [avoidance reasons differ: ' + '; '.join(sorted(kinds)) + ' - second-layer unity missing]')
    return '\n'.join(lines)


def key_extras(problem, res) -> dict:
    """Features of the KEY itself that add content (E. Bourd, session 11):

    * switchback  - the key piece returns to its diagram square to give mate
    * unpinning   - the key releases a pinned Black unit, which creates an extra defence
    * self-pin / other line effects of the key on Black units
    """
    out = {'switchback': [], 'unpins': [], 'new_pins': []}
    for ph in res.get('phases', []):
        if ph['type'] != 'key':
            continue
        key = chess.Move.from_uci(ph['first_move']['uci'])
        home = key.from_square
        b0 = problem.board.copy(); b0.push(key)
        for v in ph['variations']:
            for c in v['continuations']:
                m = chess.Move.from_uci(c['uci'])
                if m.to_square == home and m.from_square == key.to_square:
                    out['switchback'].append(f"1...{v['defence']['san']} 2.{c['san']} "
                                             f"(the key piece returns to {chess.square_name(home)})")
        for t in ph['threat']:
            m = chess.Move.from_uci(t['uci'])
            if m.to_square == home and m.from_square == key.to_square:
                out['switchback'].append(f"threat 2.{t['san']} (the key piece returns to {chess.square_name(home)})")
        # pins released / created by the key
        before = problem.board.copy(); before.turn = chess.BLACK
        for sq in chess.SquareSet(before.occupied_co[chess.BLACK]):
            was = before.is_pinned(chess.BLACK, sq)
            now = b0.is_pinned(chess.BLACK, sq)
            if was and not now:
                moves = [v['defence']['san'] for v in ph['variations']
                         if v['defence']['uci'][:2] == chess.square_name(sq)
                         and not v['threat_repeat'] and v['continuations']]
                out['unpins'].append({'unit': nm(before, sq), 'new_defences': moves})
            elif now and not was:
                out['new_pins'].append(nm(before, sq))
    return out


def find_half_batteries(board: chess.Board):
    """Geometric detection: a White line piece with EXACTLY two Black units between it and the Black king.
    Those two units are the half-pinned pair - the only defences that can be thematic (E. Bourd, s11)."""
    k = board.king(chess.BLACK)
    out = []
    if k is None:
        return out
    for sq in chess.SquareSet(board.occupied_co[chess.WHITE]):
        pt = board.piece_type_at(sq)
        if pt not in (chess.QUEEN, chess.ROOK, chess.BISHOP):
            continue
        df, dr = chess.square_file(k) - chess.square_file(sq), chess.square_rank(k) - chess.square_rank(sq)
        diag = abs(df) == abs(dr) and df != 0
        line = (df == 0 or dr == 0) and (df or dr)
        if not (diag or line):
            continue
        if diag and pt == chess.ROOK:
            continue
        if line and pt == chess.BISHOP:
            continue
        between = [x for x in chess.SquareSet(chess.between(sq, k)) if board.piece_at(x)]
        if len(between) == 2 and all(board.color_at(x) == chess.BLACK for x in between):
            out.append({'pinner': chess.square_name(sq),
                        'units': tuple(sorted(chess.square_name(x) for x in between)),
                        'names': tuple(nm(board, x) for x in between)})
    return out


def anticipatory_closing(problem, res):
    """Double-paradox tries (E. Bourd, session 13).

    A try by the key piece fails because it CLOSES a White line that is not even open yet in the diagram:
    the line is blocked by a Black unit, and only that unit's defence opens it. So the try commits a
    self-interference whose cost appears one move later - much more hidden than an ordinary shut-off.

    For each try: take its refutation r, look up the mate m that answers r in the SOLUTION, and check
      (a) after 1.try r, the mate m fails because a White line piece P needed by m is cut by the try square;
      (b) in the diagram that same line of P was blocked anyway by the defending unit's own square.
    """
    out = []
    key_ph = next((p for p in res.get('phases', []) if p['type'] == 'key'), None)
    if not key_ph:
        return out
    key = chess.Move.from_uci(key_ph['first_move']['uci'])
    answers = {}
    bk = problem.board.copy(); bk.push(key)
    for v in key_ph['variations']:
        if not v['threat_repeat'] and len(v['continuations']) == 1:
            answers[v['defence']['uci']] = v['continuations'][0]['uci']
    for ph in res.get('phases', []):
        if ph['type'] != 'try' or ph['first_move']['uci'][:2] != key.uci()[:2]:
            continue
        tmv = chess.Move.from_uci(ph['first_move']['uci'])
        for r in ph['refutations']:
            mate_uci = answers.get(r['uci'])
            if not mate_uci:
                continue
            m = chess.Move.from_uci(mate_uci)
            d = chess.Move.from_uci(r['uci'])
            # position after 1.try, defence
            t = problem.board.copy(); t.push(tmv); t.push(d)
            if m in t.legal_moves:
                a = t.copy(); a.push(m)
                if a.is_checkmate():
                    continue                      # the mate still works: not this mechanism
            # the mate's SAN, taken on the correct board
            sol = problem.board.copy(); sol.push(key); sol.push(d)
            m_san = san(sol, m)
            # case (b): the try square blocks the MATING piece's own path
            if tmv.to_square in chess.SquareSet(chess.between(m.from_square, m.to_square)):
                blocked_before = d.from_square in chess.SquareSet(chess.between(m.from_square, m.to_square))
                out.append({'try': ph['first_move']['san'], 'refutation': r['san'], 'mate_denied': m_san,
                            'line': nm(problem.board, m.from_square) + ' (the mating piece itself)',
                            'anticipatory': bool(blocked_before)})
                continue
            # case (a): the try square cuts a line the mate NEEDS for support
            s = problem.board.copy(); s.push(key); s.push(d); s.push(m)
            for sq in chess.SquareSet(s.occupied_co[chess.WHITE]):
                if s.piece_type_at(sq) not in (chess.QUEEN, chess.ROOK, chess.BISHOP) or sq == m.to_square:
                    continue
                x = s.copy(); x.remove_piece_at(sq)
                if x.is_checkmate():
                    continue                      # P was not needed
                # is P's line to the mate position cut by the try square?
                if tmv.to_square not in chess.SquareSet(chess.between(sq, s.king(chess.BLACK))) and \
                   not any(tmv.to_square in chess.SquareSet(chess.between(sq, y)) for y in chess.SquareSet(s.attacks(sq))):
                    continue
                blocked_before = d.from_square in chess.SquareSet(chess.between(sq, s.king(chess.BLACK))) or \
                                 any(d.from_square in chess.SquareSet(chess.between(sq, y)) for y in chess.SquareSet(s.attacks(sq))) or \
                                 problem.board.piece_at(d.from_square) is not None and \
                                 d.from_square in chess.SquareSet(problem.board.attacks(sq))
                out.append({'try': ph['first_move']['san'], 'refutation': r['san'], 'mate_denied': m_san,
                            'line': nm(problem.board, sq), 'anticipatory': bool(blocked_before)})
                break
    return out


def self_pin_tries(problem, res):
    """Tries by the key piece (usually the King) that fail because the move COMPLETES a pin of one of
    White's OWN units - Black line piece, White unit, and the try square collinear in that order - so the
    mate that unit would deliver after the refuting defence becomes impossible (E. Bourd, session 15)."""
    out = []
    key_ph = next((p for p in res.get('phases', []) if p['type'] == 'key'), None)
    if not key_ph:
        return out
    key = chess.Move.from_uci(key_ph['first_move']['uci'])
    answers = {v['defence']['uci']: v['continuations'][0]
               for v in key_ph['variations']
               if not v['threat_repeat'] and len(v['continuations']) == 1}

    def pinned_after(to_square):
        t = problem.board.copy()
        t.remove_piece_at(t.king(chess.WHITE))
        t.set_piece_at(to_square, chess.Piece(chess.KING, True))
        return {chess.square_name(s) for s in chess.SquareSet(t.occupied_co[chess.WHITE])
                if t.piece_type_at(s) != chess.KING and t.is_pinned(chess.WHITE, s)}

    key_pins = pinned_after(key.to_square)
    for ph in res.get('phases', []):
        if ph['type'] != 'try' or ph['first_move']['uci'][:2] != key.uci()[:2]:
            continue
        tm = chess.Move.from_uci(ph['first_move']['uci'])
        pins = pinned_after(tm.to_square)
        if not pins:
            continue
        for r in ph['refutations']:
            m = answers.get(r['uci'])
            if m and chess.square_name(chess.Move.from_uci(m['uci']).from_square) in pins:
                out.append({'try': ph['first_move']['san'], 'refutation': r['san'],
                            'pinned': chess.square_name(chess.Move.from_uci(m['uci']).from_square),
                            'mate_denied': m['san']})
                break
    return {'tries': out, 'key_pins_nothing': not key_pins}
