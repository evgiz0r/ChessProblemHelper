"""A map of the mechanism space, to answer "how do I look for NEW motivations?".

A thematic variation of a battery/half-pin problem is described by three independent choices:

  1. HOW the thematic unit leaves the line   - advance / capture / piece move / interference
  2. HOW the pin is exploited                - capture prevention / interposition prevention / none
  3. WHY the sibling mate fails (avoidance)  - defender retains control / line opened by the defence /
                                               another unit / king flight / no check

Every known problem occupies one cell per variation. Cells with examples are solved territory; EMPTY cells
are candidate ideas nobody in this catalogue has built yet. `gaps()` lists them, so the search for new
motivations becomes enumeration plus a targeted core search instead of inspiration.

The catalogue lives in knowledge/motifs.json and grows as positions are classified.
"""
from __future__ import annotations
import json, os
import chess
from ..core import Problem, Stipulation, san
from ..motives import dual_avoidance_after
from .scheme_search import pin_exploited, mates_after

DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'knowledge')
PATH = os.path.join(DIR, 'motifs.json')

LEAVE = ['advance', 'capture', 'piece move']
EXPLOIT = ['capture prevention', 'interposition prevention', 'none']
AVOID = ['defender retains control', 'line opened by the defence', 'another unit', 'king flight', 'no check']


def _leave_kind(board: chess.Board, d: chess.Move) -> str:
    p = board.piece_at(d.from_square)
    if p and p.piece_type == chess.PAWN:
        return 'capture' if board.is_capture(d) else 'advance'
    return 'piece move'


def classify(board: chess.Board, pinner: str, halfpin: tuple[str, str], label: str = '') -> dict:
    """board: post-key position, Black to move. Returns one record per thematic variation."""
    pin = chess.parse_square(pinner)
    hp = tuple(chess.parse_square(x) for x in halfpin)
    da = dual_avoidance_after(board, None, only_from=set(halfpin))
    out = []
    for it in da['variations']:
        d = None
        for m in board.legal_moves:
            if san(board, m) == it['defence']:
                d = m; break
        if d is None:
            continue
        mate = None
        t = board.copy(); t.push(d)
        for m in t.legal_moves:
            if san(t, m) == it['mate']:
                mate = m; break
        ex = pin_exploited(board, pin, hp, d, mate) if mate else None
        exploit = ('capture prevention' if ex and 'capture' in ex else
                   'interposition prevention' if ex else 'none')
        th = it.get('thematic') or {}
        avoid = (th.get('kind') or 'none').split(' (')[0].split(' to ')[0]
        out.append({'defence': it['defence'], 'mate': it['mate'], 'leave': _leave_kind(board, d),
                    'exploit': exploit, 'avoid': avoid, 'label': label,
                    'fen': board.fen().split()[0]})
    return {'unified': da['unified'], 'variations': out}


def load():
    return json.load(open(PATH, encoding='utf-8')) if os.path.exists(PATH) else {'cells': {}}


def add(board, pinner, halfpin, label, source=''):
    cat = load()
    res = classify(board, pinner, halfpin, label)
    for v in res['variations']:
        key = f"{v['leave']} | {v['exploit']} | {v['avoid']}"
        cell = cat['cells'].setdefault(key, [])
        if not any(e['fen'] == v['fen'] and e['defence'] == v['defence'] for e in cell):
            cell.append({'label': label, 'source': source, 'fen': v['fen'],
                         'defence': v['defence'], 'mate': v['mate']})
    json.dump(cat, open(PATH, 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
    return res


def gaps(leave=None, exploit=None, avoid=None):
    """List cells with no example yet - candidate mechanisms to try building."""
    cat = load()
    out = []
    for L in (leave or LEAVE):
        for E in (exploit or EXPLOIT):
            for A in (avoid or AVOID):
                if E == 'none':
                    continue                      # not a half-pin variation at all
                key = f'{L} | {E} | {A}'
                if not cat['cells'].get(key):
                    out.append(key)
    return out


def report():
    cat = load()
    lines = ['MOTIF MAP   (leave the line | pin exploited by | sibling mate fails because)']
    for L in LEAVE:
        for E in EXPLOIT:
            if E == 'none':
                continue
            for A in AVOID:
                key = f'{L} | {E} | {A}'
                ex = cat['cells'].get(key, [])
                mark = f'{len(ex)} ex.' if ex else '  --  '
                tag = f"  {ex[0]['label']}: 1...{ex[0]['defence']} 2.{ex[0]['mate']}" if ex else ''
                lines.append(f'  [{mark}] {key}{tag}')
    n = sum(1 for L in LEAVE for E in EXPLOIT if E != 'none' for A in AVOID
            if cat['cells'].get(f'{L} | {E} | {A}'))
    total = len(LEAVE) * (len(EXPLOIT) - 1) * len(AVOID)
    lines.append(f'filled {n}/{total} cells')
    return '\n'.join(lines)
