"""Round 4: does the move-change view (tools/move_delta.py) catch departure effects? 40 claims "1...d 2.m - mate?",
half true mates, half traps whose only escapes come from a departure effect; low effort; four conditions.

    python harness4.py make OUTDIR KEYDIR
    python harness4.py score KEYDIR answers4/
"""
import json, os, random, sys
sys.path.insert(0, '/home/user/ChessProblemHelper/tools')
import chess
import board_pictures as bp
import move_delta as md

CONDITIONS = ['fen', 'pic_plain', 'pic_after', 'text_delta', 'pic_delta']
REAL = [  # the six false mates of round 2 (base FEN with Black to move, defence, check)
    ('P4 after 1.Qe6', '8/2p3p1/2b1Q1B1/r1r5/p1Pk2P1/3NN3/3K4/8 b - - 1 1', 'Rxc4', 'Qe5'),
    ('P4 after 1.Qe6', '8/2p3p1/2b1Q1B1/r1r5/p1Pk2P1/3NN3/3K4/8 b - - 1 1', 'Rxc4', 'Nf5'),
    ('P4 set', '8/2p1Q1p1/2b3B1/r1r5/p1Pk2P1/3NN3/3K4/8 b - - 0 1', 'Re5', 'Qxe5'),
    ('P4 set', '8/2p1Q1p1/2b3B1/r1r5/p1Pk2P1/3NN3/3K4/8 b - - 0 1', 'Bb7', 'Qe4'),
    ('P4 set', '8/2p1Q1p1/2b3B1/r1r5/p1Pk2P1/3NN3/3K4/8 b - - 0 1', 'Ba8', 'Qe4'),
    ('P1 set', '3N1r1B/3R4/2P2q2/1K1pnp2/3k1p2/3B2p1/3PQ3/8 b - - 0 1', 'Qf7', 'Qxe5'),
]


def explain(after_d, d, m):
    """Why each escape after 1...d 2.m exists: 'opened' (d vacated the line), 'dropped' (m's piece left that guard),
    'kept' (the defender still covers it), or None."""
    b = after_d.copy(); b.push(m)
    dm = md.delta(after_d, m)
    out = []
    for r in b.legal_moves:
        why = None
        if r.from_square == d.to_square:
            why = 'kept'
        elif d.from_square in chess.SquareSet(chess.between(r.from_square, r.to_square)):
            why = 'opened'
        elif r.to_square in dm['side_loses']:
            why = 'dropped'
        out.append((b.san(r), why))
    return out


def candidates():
    probs = json.load(open('/home/user/ChessProblemHelper/knowledge/problems.json'))['problems']
    traps, mates = [], []
    for p in sorted(probs, key=lambda p: p['id']):
        ks = p.get('keys') or []
        if len(ks) != 1 or p.get('cooked'):
            continue
        try:
            diag = chess.Board(p['fen'] + ' b - - 0 1')
            pk = chess.Board(p['fen'] + ' w - - 0 1'); pk.push_san(ks[0])
        except Exception:
            continue
        if not diag.is_valid() or not pk.is_valid():
            continue
        for label, base in (('set', diag), ('after the key', pk)):
            for d in list(base.legal_moves):
                a = base.copy(); a.push(d)
                for m in a.legal_moves:
                    if not a.gives_check(m):
                        continue
                    a.push(m); mate = a.is_checkmate(); a.pop()
                    item = (f"{p['id']} {label}", base.fen(), base.san(d), a.san(m).rstrip('+#'))
                    if mate:
                        mates.append(item)
                    else:
                        why = explain(a, d, m)
                        if 1 <= len(why) <= 2 and all(w for _, w in why):
                            traps.append(item + (sorted({w for _, w in why}),))
    return traps, mates


def make(out, keydir):
    rng = random.Random(20261107)
    traps, mates = candidates()
    real = []
    for src, fen, d, m in REAL:
        b = chess.Board(fen); dd = b.parse_san(d); a = b.copy(); a.push(dd)
        real.append((src + ' (round-2 error)', fen, d, m, sorted({w or 'other' for _, w in explain(a, dd, a.parse_san(m))})))
    used_src = {r[0].split()[0] for r in REAL}
    rng.shuffle(traps); rng.shuffle(mates)
    pick_t, seen = [], set()
    by_kind = {}
    for t in traps:
        if len(t[4]) == 1:                              # one clear cause per trap
            by_kind.setdefault(t[4][0], []).append(t)
    order = ['opened', 'dropped', 'kept']
    while len(pick_t) < 14 and any(by_kind.get(k) for k in order):
        for k in order:                                 # round robin over kinds, one trap per problem
            while by_kind.get(k):
                t = by_kind[k].pop()
                pid = t[0].split()[0]
                if pid not in seen:
                    seen.add(pid); pick_t.append(t)
                    break
            if len(pick_t) == 14:
                break
    pick_m, seen_m = [], set()
    for t in mates:
        pid = t[0].split()[0]
        if pid in seen_m:
            continue
        seen_m.add(pid); pick_m.append(t + (['mate'],))
        if len(pick_m) == 20:
            break
    claims = [dict(zip(('source', 'fen', 'd', 'm', 'why'), c), mate=False) for c in real + pick_t] + \
             [dict(zip(('source', 'fen', 'd', 'm', 'why'), c), mate=True) for c in pick_m]
    random.Random(99).shuffle(claims)
    for i, c in enumerate(claims):
        c['id'] = f'C{i + 1:02d}'
    os.makedirs(out, exist_ok=True); os.makedirs(keydir, exist_ok=True)
    json.dump(claims, open(os.path.join(keydir, 'keys4.json'), 'w'), indent=1)
    head = ("Blind test of chess intuition. Each item is a position with BLACK to move. Black plays the first move "
            "named, then White the second, which gives check. Is White's move MATE? Answer Y or N. Go by your first "
            "impression; do not work it out square by square. English letters (N = knight).")
    legend = ("Each item is ONE PICTURE with two boards: the position after Black's move, and after White's move. "
              "Drawn on each: the move (grey arrow); lines the move OPENS for other units (thick, blue White / red Black); "
              "lines it CLOSES (dashed grey); guards the moving side loses altogether (orange crosses); squares next to "
              "the black king the moving piece still guards (green rings); pins (purple ring) and unpins (dashed purple); "
              "squares the black king can newly step to or capture on (yellow) or loses (blue).")
    for cond in CONDITIONS:
        parts = [head]
        if cond == 'pic_plain':
            parts.append("Each position is a PICTURE: read every PNG named below with the Read tool (one Read per file).")
        if cond == 'pic_delta':
            parts.append(legend + " Read every PNG named below with the Read tool (one Read per file).")
        if cond == 'text_delta':
            parts.append("Under each position you get, for both moves, what the move changes: lines it opens and closes, "
                         "what the moving piece stops and starts guarding (and which of those its side no longer covers "
                         "at all), what it still guards next to the black king, pins, and the black king's flights.")
        for c in claims:
            b = chess.Board(c['fen'])
            parts.append(f"=== {c['id']} === Moves: 1...{c['d']} 2.{c['m']}")
            if cond in ('fen', 'text_delta'):
                parts.append(f"FEN: {b.fen()}")
            if cond == 'text_delta':
                parts.append('\n'.join(md.text(x) for x in md.deltas(c['fen'], [c['d'], c['m']])))
            if cond == 'pic_plain':
                png = os.path.join(out, 'png', f"{c['id']}_plain.png")
                os.makedirs(os.path.dirname(png), exist_ok=True)
                bp.render(f'<html><body style="margin:0;background:#fff">{bp.svg(b, "plain", 360)}</body></html>', png, 360, 360)
                parts.append(f"Picture: {png}")
            if cond == 'pic_delta':
                png = os.path.join(out, 'png', f"{c['id']}_delta.png")
                os.makedirs(os.path.dirname(png), exist_ok=True)
                md.png(md.deltas(c['fen'], [c['d'], c['m']]), png, size=360)
                parts.append(f"Picture: {png}")
        parts.append('Reply with ONE JSON object and nothing else: {"C01": "Y", "C02": "N", ...}')
        open(os.path.join(out, f'prompt_{cond}.txt'), 'w').write('\n\n'.join(parts) + '\n')
    from collections import Counter
    print(f'claims {len(claims)}: mates {sum(c["mate"] for c in claims)}, traps {sum(not c["mate"] for c in claims)}',
          Counter(w for c in claims if not c['mate'] for w in c['why']), '| candidates', len(traps), 'traps', len(mates), 'mates')


def score(keydir, ans_dir):
    claims = json.load(open(os.path.join(keydir, 'keys4.json')))
    res = {}
    for cond in CONDITIONS:
        p = os.path.join(ans_dir, f'{cond}.json')
        if not os.path.exists(p):
            continue
        a = json.load(open(p))
        rows = {'true mate': [0, 0], 'trap (round-2 error)': [0, 0], 'trap (generated)': [0, 0]}
        wrong = []
        for c in claims:
            k = 'true mate' if c['mate'] else ('trap (round-2 error)' if 'round-2' in c['source'] else 'trap (generated)')
            said = (a.get(c['id']) or '').upper()[:1]
            ok = said == ('Y' if c['mate'] else 'N')
            rows[k][0] += ok; rows[k][1] += 1
            if not ok:
                wrong.append(f"{c['id']} 1...{c['d']} 2.{c['m']} said {said or '-'} ({k}; {','.join(c['why'])}; {c['source']})")
        res[cond] = (rows, wrong)
    print(f'{"":24}' + ''.join(f'{c:>12}' for c in res))
    for k in ('true mate', 'trap (round-2 error)', 'trap (generated)'):
        print(f'{k:24}' + ''.join(f'{res[c][0][k][0]:>7}/{res[c][0][k][1]:<4}' for c in res))
    print(f'{"total":24}' + ''.join(f'{sum(v[0] for v in res[c][0].values()):>7}/{sum(v[1] for v in res[c][0].values()):<4}' for c in res))
    for c, (_, w) in res.items():
        print(f'\n{c}:'); [print('  ' + x) for x in w]
    json.dump({c: {'rows': r, 'wrong': w} for c, (r, w) in res.items()}, open(os.path.join(keydir, 'scores4.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'make': make, 'score': score}[sys.argv[1]](*sys.argv[2:])
