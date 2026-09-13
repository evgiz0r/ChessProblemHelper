import sys, chess, time
sys.path.insert(0,'/home/claude/chesscomp')
from chesscomp import *
from chesscomp.motives import explain_key_phase, detect_half_pin
base='3N1r1B/3R4/2P2q2/1K1pn3/3k1p2/6p1/3PQ3/8'   # f5 pawn and Bd3 removed
res=[]; t0=time.time()
for bsq in ['d3','c2','b1','e4','f5','g6','h7']:
    extras=[None]+[(pc,chess.square_name(s)) for pc in 'PBSR' for s in chess.SQUARES]
    for ex in extras:
        if time.time()-t0>250: break
        b=chess.Board(base+' w - - 0 1')
        if b.piece_at(chess.parse_square(bsq)): continue
        b.set_piece_at(chess.parse_square(bsq),chess.Piece(chess.BISHOP,True))
        if ex:
            s=chess.parse_square(ex[1])
            if b.piece_at(s) or (ex[0]=='P' and ex[1][1] in '18'): continue
            b.set_piece_at(s,chess.Piece(chess.Piece.from_symbol(ex[0].replace('S','N')).piece_type,False))
        if not b.is_valid(): continue
        p=Problem(b,Stipulation.parse('#2'))
        r=analyse(p,include_tries=False,include_set=False,time_limit=10)
        k=r.get('keys',[])
        if len(k)!=1: continue
        ph=[x for x in r['phases'] if x['type']=='key'][0]; km=chess.Move.from_uci(ph['first_move']['uci'])
        if km.from_square!=chess.parse_square(bsq) or b.is_capture(km) or ph.get('check_key'): continue
        ex_=explain_key_phase(p,r); bb=b.copy(); bb.push(km)
        hp=detect_half_pin(bb,ex_)
        nv=len([v for v in ph['variations'] if not v['threat_repeat'] and v['continuations']])
        duals=len([v for v in ph['variations'] if not v['threat_repeat'] and v['dual']])
        res.append((hp[0]['variations'] if hp else 0, nv-duals, bsq, ex, k[0], '/'.join(t['san'] for t in ph['threat'])))
res.sort(key=lambda x:(-x[0],-x[1]))
for x in res[:10]: print(f"B{x[2]} + black {x[3]}: 1.{x[4]}! ({x[5]})  half-pin vars {x[0]}, clean vars {x[1]}")
print(len(res),'quiet bishop keys found', round(time.time()-t0),'s')
