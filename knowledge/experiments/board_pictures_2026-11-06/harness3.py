"""Round 3 (E. Bourd: "limit the reasoning, to feel the intuition ... spam the agent with many positions"): ~40 positions,
three yes/no claims each ("does 1.X give check?"), low reasoning effort. Half the claims copy the old errors.

    python harness3.py make OUTDIR KEYDIR
    python harness3.py score KEYDIR answers3/
"""
import json, os, random, sys
sys.path.insert(0, '/home/user/ChessProblemHelper/tools')
import chess
import board_views as bv
import board_pictures as bp

TEXT = {'fen': bv.v_fen, 'grid_list': bv.v_grid_list, 'annotated': bv.v_annotated}
PICS = {'pic_plain': 'plain', 'pic_rays': 'rays'}
CONDITIONS = list(TEXT) + list(PICS)
FORCED = {'A': ['Bc4'], 'B': ['Qxe4'], 'C': ['Qe4'], 'D': ['fxe5']}      # the recorded errors


def line_with(a, b):
    fa, ra, fb, rb = chess.square_file(a), chess.square_rank(a), chess.square_file(b), chess.square_rank(b)
    if fa == fb or ra == rb:
        return 'orth'
    if abs(fa - fb) == abs(ra - rb):
        return 'diag'
    return None


def kind(b, m, check):
    """Label a claim by the error it imitates (false) or the miss it tests (true)."""
    p = b.piece_at(m.from_square)
    k = b.king(chess.BLACK)
    t = m.to_square
    if check:
        if p.piece_type == chess.KNIGHT:
            return 'true: knight'
        if p.piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP) and chess.square_distance(t, k) >= 3:
            return 'true: long line'
        if b.is_capture(m):
            return 'true: capture'
        return 'true: near'
    ln = line_with(t, k)
    if p.piece_type == chess.BISHOP and ln == 'orth':
        return 'false: bishop on the king\'s rank/file'
    if p.piece_type == chess.ROOK and ln == 'diag':
        return 'false: rook on the king\'s diagonal'
    if p.piece_type == chess.PAWN and chess.square_distance(t, k) <= 1:
        return 'false: pawn next to the king'
    if p.piece_type == chess.KNIGHT and chess.square_distance(t, k) <= 2:
        return 'false: knight near the king'
    if p.piece_type in (chess.QUEEN, chess.ROOK, chess.BISHOP) and ln and \
            ((ln == 'diag' and p.piece_type != chess.ROOK) or (ln == 'orth' and p.piece_type != chess.BISHOP)):
        return 'false: blocked line'
    if chess.square_distance(t, k) <= 2:
        return 'false: near the king'
    return None


def claims_for(pid, fen, rng, idx):
    """3 claims: forced ones first; then about half true (alternating 1 and 2 per position), false ones rotating kinds."""
    b = chess.Board(fen + ' w - - 0 1')
    out = []
    for san in FORCED.get(pid, []):
        m = b.parse_san(san)
        out.append((san, b.gives_check(m), kind(b, m, b.gives_check(m))))
    trues, falses = [], {}
    for m in b.legal_moves:
        c = b.gives_check(m)
        k = kind(b, m, c)
        if not k or any(b.san(m).rstrip('+#') == o[0] for o in out):
            continue
        item = (b.san(m).rstrip('+#'), c, k)
        if c:
            trues.append(item)
        else:
            falses.setdefault(k, []).append(item)
    rng.shuffle(trues)
    prio = {'true: long line': 0, 'true: knight': 1, 'true: capture': 2, 'true: near': 3}
    trues.sort(key=lambda x: prio[x[2]])
    for v in falses.values():
        rng.shuffle(v)
    want_true = (1 if idx % 2 else 2) - sum(1 for o in out if o[1])
    out += trues[:max(0, want_true)]
    kinds = sorted(falses)
    kinds = kinds[idx % len(kinds):] + kinds[:idx % len(kinds)] if kinds else []
    while len(out) < 3 and any(falses.values()):
        for k in kinds:
            if falses[k] and len(out) < 3:
                out.append(falses[k].pop())
    rest = trues[max(0, want_true):]
    out += rest[:3 - len(out)]
    rng.shuffle(out)
    return out[:3]


def positions():
    cases = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'cases.json')))[:4]
    probs = json.load(open('/home/user/ChessProblemHelper/knowledge/problems.json'))['problems']
    seen = {c['fen'] for c in cases}
    pool = []
    for p in sorted(probs, key=lambda p: p['id']):
        f = p['fen']
        n = sum(ch.isalpha() for ch in f)
        try:
            b = chess.Board(f + ' w - - 0 1')
        except ValueError:
            continue
        if f in seen or not (9 <= n <= 18) or not b.is_valid() or b.is_check():
            continue
        seen.add(f); pool.append(f)
    rng = random.Random(2026_11_06)
    rng.shuffle(pool)
    return [(c['id'], c['fen']) for c in cases] + [(f'P{i + 1:02d}', f) for i, f in enumerate(pool[:36])]


def make(out, keydir):
    rng = random.Random(7)
    os.makedirs(out, exist_ok=True); os.makedirs(keydir, exist_ok=True)
    pos = positions()
    keys = {}
    for i, (pid, fen) in enumerate(pos):
        cl = claims_for(pid, fen, rng, i)
        keys[pid] = {'fen': fen, 'claims': [{'move': s, 'check': c, 'kind': k} for s, c, k in cl]}
    json.dump(keys, open(os.path.join(keydir, 'keys3.json'), 'w'), indent=1)
    for cond in CONDITIONS:
        parts = ["Blind test of chess intuition. For each position (White to move) three moves are named. For each, say "
                 "whether that White move GIVES CHECK to the black king: Y or N. Go by your first impression; do not work "
                 "it out square by square. Use English letters (N = knight)."]
        if cond in PICS:
            parts.append("Each position is a PICTURE: read every PNG named below with the Read tool (one Read per file)." + (
                ' Blue lines are White lines of sight, red Black, ending at the first unit; dashed = the continuation '
                'behind that unit; short lines = knight jumps and pawn captures.' if cond == 'pic_rays' else ''))
        for pid, fen in pos:
            b = chess.Board(fen + ' w - - 0 1')
            parts.append(f"=== {pid} ===")
            if cond in PICS:
                png = os.path.join(out, 'png', f"{pid}_{PICS[cond]}.png")
                os.makedirs(os.path.dirname(png), exist_ok=True)
                if not os.path.exists(png):
                    bp.render(f'<html><body style="margin:0;background:#fff">{bp.svg(b, PICS[cond], 360)}</body></html>',
                              png, 360, 360)
                parts.append(f"Picture: {png}")
            else:
                parts.append(TEXT[cond](b))
            parts.append('Moves: ' + ', '.join(f'({i + 1}) {c["move"]}' for i, c in enumerate(keys[pid]['claims'])))
        parts.append('Reply with ONE JSON object and nothing else, one string of three letters per position in the order '
                     'asked: {"A": "YNY", "B": "NNY", ...}')
        open(os.path.join(out, f'prompt_{cond}.txt'), 'w').write('\n\n'.join(parts) + '\n')
    n = sum(len(v['claims']) for v in keys.values())
    t = sum(c['check'] for v in keys.values() for c in v['claims'])
    print(f'positions {len(pos)} | claims {n} ({t} true, {n - t} false) | conditions {" ".join(CONDITIONS)}')
    from collections import Counter
    print(Counter(c['kind'] for v in keys.values() for c in v['claims']))


def score(keydir, ans_dir):
    keys = json.load(open(os.path.join(keydir, 'keys3.json')))
    from collections import defaultdict
    res = {}
    for cond in CONDITIONS:
        p = os.path.join(ans_dir, f'{cond}.json')
        if not os.path.exists(p):
            continue
        ans = json.load(open(p))
        by = defaultdict(lambda: [0, 0])
        wrong = []
        for pid, k in keys.items():
            a = (ans.get(pid) or '').upper()
            for i, c in enumerate(k['claims']):
                said = a[i] == 'Y' if i < len(a) else None
                ok = said is not None and said == c['check']
                by[c['kind']][0] += ok; by[c['kind']][1] += 1
                if not ok:
                    wrong.append(f'{pid} {c["move"]}: said {"Y" if said else ("N" if said is False else "-")}, '
                                 f'is {"check" if c["check"] else "no check"} ({c["kind"]})')
        res[cond] = (by, wrong)
    kinds = sorted({c['kind'] for v in keys.values() for c in v['claims']})
    print('kind'.ljust(40) + ''.join(f'{c:>11}' for c in res))
    for k in kinds:
        print(k.ljust(40) + ''.join(f'{res[c][0][k][0]:>5}/{res[c][0][k][1]:<5}' for c in res))
    print('TOTAL'.ljust(40) + ''.join(f'{sum(v[0] for v in res[c][0].values()):>5}/{sum(v[1] for v in res[c][0].values()):<5}' for c in res))
    for c, (_, w) in res.items():
        print(f'\n{c}:'); [print('  ' + x) for x in w]
    json.dump({c: {'by_kind': dict(b), 'wrong': w} for c, (b, w) in res.items()},
              open(os.path.join(keydir, 'scores3.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'make': make, 'score': score}[sys.argv[1]](*sys.argv[2:])
