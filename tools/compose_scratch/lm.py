import chess, sys
def m1(b):
    r = []
    for m in list(b.legal_moves):
        if not b.gives_check(m): continue
        b.push(m)
        if b.is_checkmate(): r.append(m)
        b.pop()
    return r
b = chess.Board(sys.argv[1] + ' b - - 0 1')
w = b.copy(); w.turn = chess.WHITE
print('valid' if b.is_valid() else 'INVALID', '| White to move mates:', [w.san(m) for m in m1(w)], '| flights:', [b.san(m) for m in b.legal_moves if m.from_square == b.king(chess.BLACK)])
for m in list(b.legal_moves):
    s = b.san(m); b.push(m); print(f'{s:7}', [b.san(x) for x in m1(b)]); b.pop()
