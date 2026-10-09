import chess, sys
from same_sq_lib import m1
for fen in sys.argv[1:]:
    b = chess.Board(fen + ' b - - 0 1')
    w = b.copy(); w.turn = chess.WHITE
    print(fen, 'valid' if b.is_valid() else 'INVALID', '| threat', [w.san(x) for x in m1(w)])
    for m in list(b.legal_moves):
        s = b.san(m); b.push(m); ms = [b.san(x) for x in m1(b)]; b.pop()
        if len(ms) != 1 or 'e4' in s: print('  ', s, ms)
