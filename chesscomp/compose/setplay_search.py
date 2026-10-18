"""Set-play search for a battery scheme (E. Bourd, 18 Oct 2026, battery series: "at first i just finished the scheme"):
Black to move in the diagram, each named defence answered by its own mate in one only, all wanted mates different,
no flight, no check on either king, the core fixed; every other unit is added, removed or moved. The threat comes
after the scheme works (a key and a threat the defences parry), so nothing here asks for one.

    python3 -m chesscomp.compose.setplay_search CORE SEED WANT_JSON BUDGET_S RNG
    e.g. CORE=8/8/8/4k3/8/2R5/1B4r1/8 WANT='{"Rg6":"c3c6","Rg4":"c3f3"}'   (black rook g2 holds the battery Bb2/Rc3)
WANT maps a defence (python-chess SAN, N for knights) to a mate pattern (fnmatch on uci, "c3*" = any discharge).
Env EMPTY=d4: squares that must stay empty (the battery line). Env NOFLIGHT=0 allows king moves in the diagram.
Env NODOUBLE=1: a double-check mate does not count as the wanted mate (E. Bourd: watch out for double-check mates).
Env NORECAP=1 (with HOLDER): a mate that captures the holder on its arrival square does not count (E. Bourd, 18 Oct
2026: "1...Sxc5 2.Bxc5# is bad, need a non recapturing thematic move").
Env HOLDER=c2: WANT is then a list of mate patterns ('["e3c5","e3g5"]') and any moves of the unit on c2 may supply them:
for each pattern some move of the holder must be answered by that mate only (distinct moves), so the search chooses
which defences carry the scheme (18 Oct 2026, rook-bishop battery).
"""
from chesscomp.core import illegal_position as _illegal
import sys, os, random, time, json, fnmatch, chess

EMPTY = {chess.parse_square(x) for x in os.environ.get('EMPTY', '').split(',') if x}
NOFLIGHT = os.environ.get('NOFLIGHT', '1') == '1'
NODOUBLE = os.environ.get('NODOUBLE', '0') == '1'
HOLDER = chess.parse_square(os.environ['HOLDER']) if os.environ.get('HOLDER') else None
NORECAP = os.environ.get('NORECAP', '0') == '1'   # a wanted mate may not land on the holder's arrival square
CSQ, WANT = {}, {}


def promoted(b):
    if _illegal(b):
        return True
    for col in (chess.WHITE, chess.BLACK):
        w = lambda t: len(b.pieces(t, col))
        if w(chess.QUEEN) > 1 or w(chess.ROOK) > 2 or w(chess.KNIGHT) > 2:
            return True
        bs = list(b.pieces(chess.BISHOP, col))
        if len(bs) > 2 or (len(bs) == 2 and sum(divmod(bs[0], 8)) % 2 == sum(divmod(bs[1], 8)) % 2):
            return True
    return False


def mates_in_one(b):
    out = []
    for m in list(b.legal_moves):
        b.push(m)
        if b.is_checkmate():
            out.append(m.uci() + ('+' if len(b.checkers()) > 1 else ''))
        b.pop()
    return out


def score(fen):
    b = chess.Board(fen + ' b - - 0 1')
    w = chess.Board(fen + ' w - - 0 1')
    if not b.is_valid() or not w.is_valid() or promoted(b) or any(b.piece_at(x) for x in EMPTY):
        return -1e9, ''
    s, ok, got = 0.0, True, {}
    if HOLDER is not None:
        if not b.piece_at(HOLDER) or b.piece_at(HOLDER).color != chess.BLACK:
            return -1e9, ''
        per = {}
        for mv in [m for m in b.legal_moves if m.from_square == HOLDER]:
            b.push(mv); per[mv.uci()] = mates_in_one(b); b.pop()
        used, mates = set(), set()
        for i, want in enumerate(WANT):
            key = f'{i}:{want}'
            cands = [u for u, ms in per.items() if u not in used and len(ms) == 1 and fnmatch.fnmatch(ms[0].rstrip('+'), want)
                     and not (NODOUBLE and ms[0].endswith('+')) and ms[0] not in mates
                     and not (NORECAP and ms[0][2:4] == u[2:4])]
            near = [u for u, ms in per.items() if u not in used and any(fnmatch.fnmatch(m.rstrip('+'), want) for m in ms)]
            if cands:
                s += 12; used.add(cands[0]); mates.add(per[cands[0]][0]); got[key] = cands[0] + '->' + per[cands[0]][0]
            else:
                ok = False; s += -3 * min(len(per[u]) - 1 for u in near) if near else -16
                got[key] = None
        flights = [b.san(m) for m in b.legal_moves if b.piece_type_at(m.from_square) == chess.KING] if NOFLIGHT else []
        m1 = mates_in_one(w)
        s -= 8 * len(flights) + 8 * len(m1) + 0.6 * len(b.piece_map())
        ok = ok and not flights and not m1
        return s + (100 if ok else 0), f"defs={got} flights={flights} m1={m1}"
    for san, want in WANT.items():
        try:
            mv = b.parse_san(san)
        except ValueError:
            s -= 30; ok = False; got[san] = None; continue
        b.push(mv); ms = mates_in_one(b); b.pop()
        got[san] = ms
        hit = [m for m in ms if fnmatch.fnmatch(m.rstrip('+'), want) and not (NODOUBLE and m.endswith('+'))]
        if len(ms) == 1 and hit:
            s += 12
        else:
            ok = False
            s += (-3 * (len(ms) - 1)) if hit else -16
    one = [v[0] for v in got.values() if v and len(v) == 1]
    if len(set(one)) < len(one):
        s -= 10; ok = False
    flights = [b.san(m) for m in b.legal_moves if b.piece_type_at(m.from_square) == chess.KING] if NOFLIGHT else []
    s -= 8 * len(flights)
    m1 = mates_in_one(w)                               # White to move: no mate in one in the diagram
    s -= 8 * len(m1)
    s -= 0.6 * len(b.piece_map())
    ok = ok and not flights and not m1
    return s + (100 if ok else 0), f"defs={got} flights={flights} m1={m1}"


def mutate(fen):
    b = chess.Board(fen + ' b - - 0 1')
    free = [s for s in chess.SquareSet(b.occupied) if s not in CSQ]
    empty = [s for s in chess.SQUARES if not b.piece_at(s) and s not in EMPTY]
    if not empty:                                      # a walk from an invalid seed can fill the board
        return fen
    op = random.random()
    if op < .35:
        sym = random.choice('NBRQPPPpppnbr'); sq = random.choice(empty)
        if sym in 'Pp' and chess.square_rank(sq) in (0, 7):
            return fen
        b.set_piece_at(sq, chess.Piece.from_symbol(sym))
    elif op < .55 and free:
        s = random.choice(free)
        if b.piece_type_at(s) != chess.KING:
            b.remove_piece_at(s)
    elif free:
        s = random.choice(free); p = b.piece_at(s); b.remove_piece_at(s); b.set_piece_at(random.choice(empty), p)
    return b.board_fen()


def main(argv=None):
    global CSQ, WANT
    a = argv or sys.argv[1:]
    core = chess.Board(a[0] + ' b - - 0 1'); CSQ = {s: core.piece_at(s) for s in chess.SQUARES if core.piece_at(s)}
    WANT = json.loads(a[2]); budget = float(a[3]); random.seed(int(a[4]))
    cur = a[1]; cs, _ = score(cur); best = []
    t0, n, T = time.time(), 0, 3.0
    while time.time() - t0 < budget:
        cand = mutate(cur)
        if random.random() < .3:
            cand = mutate(cand)
        sc, info = score(cand); n += 1
        if sc > cs or random.random() < pow(2.718, (sc - cs) / T):
            cur, cs = cand, sc
            if sc > 50 and all(f != cand for _, f, _ in best):
                best.append((sc, cand, info)); best.sort(reverse=True); best[:] = best[:12]
        if (n % 400 == 0 and cs < -20) or (n % 20 == 0 and cs < -1e8):   # invalid current: back to the seed
            cur, cs = a[1], score(a[1])[0]                 # restart from the seed when lost
    for sc, f, info in best:
        print(f'TOP {sc:.1f} {f} {info}')
    print('evaluated', n)


if __name__ == '__main__':
    main()
