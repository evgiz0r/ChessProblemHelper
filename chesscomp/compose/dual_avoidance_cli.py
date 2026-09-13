import sys, chess
sys.path.insert(0,'/home/claude/chesscomp')
from chesscomp import *
from chesscomp.motives import nm

def da_after(fen, first, squares=None):
    """Dual avoidance among thematic defences after `first` (works for tries as well as keys)."""
    b0 = chess.Board(fen+' w - - 0 1')
    try:
        mv = chess.Move.from_uci(first)
        assert mv in b0.legal_moves
    except Exception:
        mv = b0.parse_san(first.replace('S','N'))
    fs = san(b0, mv); b0.push(mv)
    # thematic defences: unique mate, optionally restricted to arrivals on given squares
    defs={}
    for d in b0.legal_moves:
        if squares and chess.square_name(d.to_square) not in squares: continue
        t=b0.copy(); dn=san(t,d); t.push(d)
        ms=[]
        for m in list(t.legal_moves):
            t.push(m)
            if t.is_checkmate(): ms.append(m)
            t.pop()
        if len(ms)==1: defs[d]=(dn, ms[0])
    mates={m.uci() for _,(_,m) in defs.items()}
    print(f'1.{fs} :')
    for d,(dn,m) in defs.items():
        t=b0.copy(); t.push(d); mn=san(t,m)
        marks=[]
        for o in sorted(mates-{m.uci()}):
            ov=chess.Move.from_uci(o); tt=b0.copy(); tt.push(d)
            if ov not in tt.legal_moves: continue
            osan=san(tt,ov); tt.push(ov)
            esc=list(tt.legal_moves)
            if not esc: marks.append(f'(2.{osan}? also mate - DUAL)'); continue
            e=esc[0]
            who = 'the defender itself' if e.from_square==d.to_square else nm(tt,e.from_square)
            if e.to_square==ov.to_square: kind=f'{who} captures on {chess.square_name(ov.to_square)}'
            elif e.from_square==tt.king(chess.BLACK): kind=f'king to {chess.square_name(e.to_square)}'
            elif not tt.is_check(): kind='no check'
            else: kind=f'{who} interposes'
            marks.append(f'(2.{osan}? {san(tt,e)}!  {kind})')
        print(f'   1...{dn} 2.{mn}  '+' '.join(marks))
