"""Round 2: solve #2 diagrams by sight; every claimed mate is checked (legal? check? mate?), defences missed are counted.

    python harness2.py make solve_cases.json OUTDIR KEYDIR
    python harness2.py score KEYDIR answers2/
"""
import json, os, re, sys
sys.path.insert(0, '/home/user/ChessProblemHelper/tools')
import chess
import board_views as bv
import board_pictures as bp

TEXT = {'fen': bv.v_fen, 'annotated': bv.v_annotated, 'selfdraw': bv.v_fen}
PICS = {'pic_plain': 'plain', 'pic_rays': 'rays'}
CONDITIONS = list(TEXT) + list(PICS)
SELFDRAW = ("Before solving each problem, DRAW it yourself first: write the 8x8 board as text, then write out every file, "
            "rank and diagonal through the black king and through each White line piece, with what stands on them. "
            "Solve from your drawing.")


def mates_after(b):
    out = []
    for m in b.legal_moves:
        b.push(m)
        if b.is_checkmate():
            out.append(m)
        b.pop()
    return out


def truth(fen, key):
    b = chess.Board(fen + ' w - - 0 1')
    pk = b.copy(); pk.push_san(key)
    nb = pk.copy(); nb.push(chess.Move.null())
    threat = sorted(nb.san(m).rstrip('#+') for m in mates_after(nb))
    tset = {m for m in mates_after(nb)}
    var = {}
    for d in pk.legal_moves:
        pk.push(d)
        ms = mates_after(pk)
        if not any(m in pk.legal_moves and m in ms for m in tset):        # the threat no longer mates: a defence
            var[d.uci()] = sorted(pk.san(m).rstrip('#+') for m in ms)
        pk.pop()
    sb = b.copy(); sb.turn = chess.BLACK
    setp = {}
    for d in sb.legal_moves:
        sb.push(d)
        ms = mates_after(sb)
        if ms:
            setp[d.uci()] = sorted(sb.san(m).rstrip('#+') for m in ms)
        sb.pop()
    return {'fen': fen, 'key': key, 'threat': threat, 'variations': var, 'set': setp}


def make(cases_path, out, keydir):
    cases = json.load(open(cases_path))
    os.makedirs(out, exist_ok=True); os.makedirs(keydir, exist_ok=True)
    json.dump({c['id']: truth(c['fen'], c['key']) for c in cases}, open(os.path.join(keydir, 'keys2.json'), 'w'), indent=1)
    for cond in CONDITIONS:
        parts = ["You are a subject in a blind test of how a chess problem is best presented to a model. Each position is a "
                 "mate-in-2 problem (#2), White to move. Solve each one by sight, as a composer reads a diagram (you have no "
                 "tools): give the key, the threat, Black's defences that stop the threat with White's mate after each (write "
                 "concrete moves; for a piece with several defending moves list each move you consider), and the set play "
                 "(Black moves in the diagram position that already have a mate ready, with that mate). Use English letters "
                 "(N = knight)."]
        if cond == 'selfdraw':
            parts.append(SELFDRAW)
        if cond in PICS:
            parts.append("Each problem is given as a PICTURE: read every PNG file named below with the Read tool (one Read "
                         "per file) and use only what you see." + (
                             ' Blue lines are White lines of sight, red Black, ending at the first unit; dashed = the '
                             'continuation behind that unit; short lines = knight jumps and pawn captures.'
                             if cond == 'pic_rays' else ''))
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
        parts.append('Reply with ONE JSON object and nothing else: {"<problem id>": {"key": "Bxf5", "threat": ["Qe4"], '
                     '"variations": [["<black move>", "<white mate>"], ...], "set": [["<black move>", "<white mate>"], ...]}, ...}')
        open(os.path.join(out, f'prompt_{cond}.txt'), 'w').write('\n\n'.join(parts) + '\n')
    print('problems', len(cases), '| conditions', ' '.join(CONDITIONS))


def _judge(b, d_san, m_san):
    """b: position with Black to move. Returns 'mate', 'check', 'nocheck', 'illegal-defence' or 'illegal-mate'."""
    try:
        d = b.parse_san(d_san.strip().rstrip('+#!?'))
    except Exception:
        return 'illegal-defence', None
    b.push(d)
    try:
        m = b.parse_san(m_san.strip().rstrip('+#!?'))
    except Exception:
        b.pop()
        return 'illegal-mate', d
    b.push(m)
    r = 'mate' if b.is_checkmate() else ('check' if b.is_check() else 'nocheck')
    b.pop(); b.pop()
    return r, d


def score(keydir, ans_dir):
    keys = json.load(open(os.path.join(keydir, 'keys2.json')))
    rows = {}
    for cond in CONDITIONS:
        p = os.path.join(ans_dir, f'{cond}.json')
        if not os.path.exists(p):
            continue
        ans = json.load(open(p))
        tot = dict(keys_ok=0, claims=0, mate=0, check=0, nocheck=0, illegal=0, defences=0, found=0)
        notes = []
        for pid, k in keys.items():
            a = ans.get(pid, {})
            b = chess.Board(k['fen'] + ' w - - 0 1')
            ok = False
            try:
                ok = b.parse_san(a.get('key', '').strip().rstrip('!+#?')) == b.parse_san(k['key'])
            except Exception:
                pass
            tot['keys_ok'] += ok
            pk = b.copy(); pk.push_san(k['key'])
            seen = set()
            for d, m in a.get('variations', []) if ok else []:
                r, dm = _judge(pk.copy(), d, m)
                tot['claims'] += 1
                tot[r if r in ('mate', 'check', 'nocheck') else 'illegal'] += 1
                if r != 'mate':
                    notes.append(f'{pid} after key: 1...{d} 2.{m} -> {r}')
                if dm:
                    seen.add(dm.uci())
            sb = b.copy(); sb.turn = chess.BLACK
            for d, m in a.get('set', []):
                r, _ = _judge(sb.copy(), d, m)
                tot['claims'] += 1
                tot[r if r in ('mate', 'check', 'nocheck') else 'illegal'] += 1
                if r != 'mate':
                    notes.append(f'{pid} set: 1...{d} 2.{m} -> {r}')
            if ok:
                tot['defences'] += len(k['variations'])
                tot['found'] += len(seen & set(k['variations']))
                miss = sorted(set(k['variations']) - seen)
                if miss:
                    notes.append(f'{pid} defences missed: {len(miss)} of {len(k["variations"])} ' +
                                 ' '.join(pk.san(chess.Move.from_uci(u)) for u in miss))
            else:
                notes.append(f'{pid} key wrong: {a.get("key")} (is {k["key"]})')
        rows[cond] = (tot, notes)
    print(f'{"condition":11} keys  claims  mate  check-only  no-check  illegal  defences found')
    for cond, (t, _) in rows.items():
        print(f'{cond:11} {t["keys_ok"]}/{len(keys)}  {t["claims"]:6} {t["mate"]:5} {t["check"]:11} {t["nocheck"]:9} '
              f'{t["illegal"]:8}  {t["found"]}/{t["defences"]}')
    for cond, (_, notes) in rows.items():
        print(f'\n{cond}:'); [print('  ' + n) for n in notes]
    json.dump({c: {'totals': t, 'notes': n} for c, (t, n) in rows.items()},
              open(os.path.join(keydir, 'scores2.json'), 'w'), indent=1)


if __name__ == '__main__':
    {'make': make, 'score': score}[sys.argv[1]](*sys.argv[2:])
