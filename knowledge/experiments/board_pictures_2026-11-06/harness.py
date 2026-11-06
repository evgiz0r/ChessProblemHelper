"""Geometry probes on positions Claude once misread: ground truth, subject prompts per view, scoring.

    python harness.py make cases.json OUTDIR      # keys.json + one prompt per condition (+ PNGs)
    python harness.py score OUTDIR answers/       # answers/<condition>.json -> table
"""
import json, os, re, sys
sys.path.insert(0, '/home/user/ChessProblemHelper/tools')
import chess
import board_views as bv
import board_pictures as bp

PROBES = ['checks', 'mates', 'pins', 'black_captures']
QUESTIONS = {
    'checks': 'every White move that gives check (SAN, e.g. "Qd5+")',
    'mates': 'every White move that mates at once (SAN)',
    'pins': 'every unit of either colour pinned to its own king (squares, e.g. "d5")',
    'black_captures': 'every capture Black could make if it were Black to move (SAN)',
}
TEXT = {'fen': bv.v_fen, 'grid_list': bv.v_grid_list, 'annotated': bv.v_annotated, 'selfdraw': bv.v_fen}
PICS = {'pic_plain': 'plain', 'pic_rays': 'rays', 'pic_arrows': 'arrows'}
CONDITIONS = list(TEXT) + list(PICS)
GLANCE = ("Answer at a glance, the way you would in the middle of a conversation about the position: no square-by-square "
          "reconstruction, no move generation tables, a few lines of notes per position at most.")
SELFDRAW = ("Before answering each position, DRAW it yourself first: write the 8x8 board as text, then write out every "
            "file, rank and diagonal through the black king and through each White line piece, with what stands on them. "
            "Then answer from your drawing.")


def _canon(board, s):
    s = s.strip().rstrip('+#!?')
    try:
        return board.san(board.parse_san(s)).rstrip('+#')
    except Exception:
        return '?' + s


def truth(fen):
    b = chess.Board(fen)
    checks = sorted(b.san(m).rstrip('+#') for m in b.legal_moves if b.gives_check(m))
    mates = []
    for m in b.legal_moves:
        b.push(m)
        if b.is_checkmate():
            mates.append(m)
        b.pop()
    mates = sorted(b.san(m).rstrip('+#') for m in mates)
    pins = sorted(chess.square_name(s) for s, p in b.piece_map().items()
                  if p.piece_type != chess.KING and b.is_pinned(p.color, s))
    bb = b.copy(); bb.turn = chess.BLACK; bb.ep_square = None
    caps = sorted(bb.san(m).rstrip('+#') for m in bb.legal_moves if bb.is_capture(m))
    return {'checks': checks, 'mates': mates, 'pins': pins, 'black_captures': caps}


def make(cases_path, out):
    cases = json.load(open(cases_path))
    os.makedirs(out, exist_ok=True)
    keys = {c['id']: dict(truth(c['fen'] + ' w - - 0 1'), fen=c['fen']) for c in cases}
    json.dump(keys, open(os.path.join(out, 'keys.json'), 'w'), indent=1)
    qs = '\n'.join(f'- "{k}": {v}' for k, v in QUESTIONS.items())
    for cond in CONDITIONS:
        parts = [f"You are a subject in a blind test of how a chess position is best presented to a model. White is to move "
                 f"in every position. For each position give:\n{qs}\nUse English letters (N = knight). {GLANCE}"]
        if cond == 'selfdraw':
            parts.append(SELFDRAW)
        if cond in PICS:
            parts.append("Each position is given as a PICTURE: read every PNG file named below with the Read tool (one Read per "
                         "file), and use only what you see in it." + {
                             'pic_plain': '',
                             'pic_rays': ' Blue lines are White lines of sight, red Black, ending at the first unit; dashed = '
                                         'the continuation behind that unit; short lines = knight jumps and pawn captures.',
                             'pic_arrows': ' Each arrow goes from a unit to a unit it attacks or defends (blue White, red Black).'}[cond])
        for c in cases:
            b = chess.Board(c['fen'] + ' w - - 0 1')
            parts.append(f"=== {c['id']} ===")
            if cond in PICS:
                png = os.path.join(out, 'png', f"{c['id']}_{PICS[cond]}.png")
                os.makedirs(os.path.dirname(png), exist_ok=True)
                bp.render(f'<html><body style="margin:0;background:#fff">{bp.svg(b, PICS[cond], 480)}</body></html>',
                          png, 480, 480)
                parts.append(f"Picture: {png}")
            else:
                parts.append(TEXT[cond](b))
        parts.append('Reply with ONE JSON object and nothing else: {"<position id>": {"checks": [...], "mates": [...], '
                     '"pins": [...], "black_captures": [...]}, ...}. Empty list when there is none.')
        open(os.path.join(out, f'prompt_{cond}.txt'), 'w').write('\n\n'.join(parts) + '\n')
    print('positions', len(cases), '| conditions', ' '.join(CONDITIONS))


def f1(gold, got):
    g, a = set(gold), set(got)
    if not g and not a:
        return 1.0
    tp = len(g & a)
    return 0.0 if tp == 0 else 2 * tp / (len(g) + len(a))


def score(out, ans_dir):
    keys = json.load(open(os.path.join(out, 'keys.json')))
    table, errors = {}, {}
    for cond in CONDITIONS:
        p = os.path.join(ans_dir, f'{cond}.json')
        if not os.path.exists(p):
            continue
        ans = json.load(open(p))
        row, errs = {k: [] for k in PROBES}, []
        for pid, key in keys.items():
            b = chess.Board(key['fen'] + ' w - - 0 1')
            bb = b.copy(); bb.turn = chess.BLACK
            a = ans.get(pid, {})
            for k in PROBES:
                raw = a.get(k, [])
                got = sorted({m[-1] for m in (re.findall(r'[a-h][1-8]', s.lower()) for s in raw) if m}) if k == 'pins' else \
                      sorted({_canon(bb if k == 'black_captures' else b, s) for s in raw})
                row[k].append(f1(key[k], got))
                miss, extra = sorted(set(key[k]) - set(got)), sorted(set(got) - set(key[k]))
                if miss or extra:
                    errs.append(f'{pid} {k}: missed {miss} extra {extra}')
        table[cond] = {k: round(sum(v) / len(v), 2) for k, v in row.items()}
        table[cond]['mean'] = round(sum(table[cond][k] for k in PROBES) / len(PROBES), 3)
        errors[cond] = errs
    json.dump({'table': table, 'errors': errors}, open(os.path.join(out, 'scores.json'), 'w'), indent=1)
    print('condition    ' + ' '.join(f'{k[:9]:>9}' for k in PROBES) + '      mean')
    for cond, r in table.items():
        print(f'{cond:12} ' + ' '.join(f'{r[k]:9.2f}' for k in PROBES) + f'  {r["mean"]:8.3f}')
    for cond, errs in errors.items():
        print(f'\n{cond}:'); [print('  ' + e) for e in errs]


if __name__ == '__main__':
    {'make': make, 'score': score}[sys.argv[1]](*sys.argv[2:])
