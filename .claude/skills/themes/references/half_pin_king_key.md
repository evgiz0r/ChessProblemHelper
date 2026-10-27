# Half-pin, pawn half-battery, White-king key

Half-pin (yacpdb 2753 and the session-2 settings): a mate that captures the pinned unit, or merely needs
the half-pinner as a guard, does not use the pin. Only defences by the half-pinned units are thematic.
Order: a clean dual-avoidance scheme first, then tries. Content is measured per PIECE: each half-pinned
unit should provoke its own mate.
Pawn half-battery: impossible on a diagonal (the rear pawn guards a square on the pin line); on a file
the pawns cannot advance so the defences are captures of units essential to the threat; on a rank they
can advance and the mate may capture the advanced pawn.
White-king key: the king stands on a White line and blocks it; every king move opens it, so the choice
of destination is free; tries are destinations that close another White line. Evgeni's order: lines and
possible king moves, then simple mates, then extend so the defences themselves open White lines
(b5BQ/8/4pK1B/1N6/1p2P3/1P1krpN). A third interfering line earns a try only if its square is not guarded
by another unit already. Searches for it failed (150k positions): with little Black material every try
dies to a king flight.

## Black half-pin in a #2 (daily No. 7, 12 Oct 2026)
Mechanism: a White line piece, two Black units, the Black king on one line. Each unit's defence leaves the
other pinned, and the mate is one the pinned unit would otherwise stop (capture the mating piece, interpose,
or land on its square). List, for each unit, the squares it covers and the lines it could block: those are the
mating squares and check lines the OTHER unit's defences make available.
Reference: Barnes, StrateGems 2002, 1st Prize (psis-25e8021eff) 7b/8/1K1p2Q1/3N4/1Nknr2R/P6R/2rp4/B7, Rh4
half-pins Re4 and Sd4: 1.Qf7! (2.Se3#) Re6 2.Qc7# (Sd4 pinned), Se6 2.Qf1# (Re4 pinned).
Detector: the solver's Patterns list prints `Half-pin: <defence> [key]` for each defence whose mate uses the
pin of the other unit (`motives.detect_half_pin`); claim the theme only when it does. Evolve can aim at it
with `PATTERN=Half-pin DEFS= NPAT=3`.
Archive: `python -m chesscomp.db list --stip '#2' --orthodox --text half-pin` (13 records, 7-14 White units).

## Bishop + rook half-pin on a diagonal (12 Oct 2026, claude-halfpin-br-sg8)
Pin line Bh7-Rg6-Bf5-Ke4. A pinned bishop can only be used on g4 (it would capture there, or interpose against a
check from h4); knight checks never use it, because no knight checking square is a bishop square. So the rook's
mate is a line mate through g4 (Rxg4# from g1), and the bishop's mate is a knight check the pinned rook would take
(Sf6#, Sd6#, Sg5#, Sg3#). Two blocks on e6 against an e-file threat separate themselves: Re6 covers f6, Be6 covers
g4 through f5. Key: the mask on e7 goes to g8 (it reaches f6, and if it stood on f6's reach in the diagram,
1.Sf6+ Rxf6 2.Rg4# cooks). The e7 knight attacks f5: 1.Sexf5 is a double-threat cook that no single unit stops;
bRh5 retakes and then guards e5, at the price of every bishop move defending (B~ Sf6#) and a Bg4 dual, which bPg4 removes.
A pure pair is out with this key: no knight landing spoils Rxg4#, so no try fails to Re6. Plan the try piece
from the rook's mate line (g1-g4) before choosing the mask. Result: 4R3/4N1NB/6r1/3ppb1r/3Bk1p1/2P1P3/4P3/3K2R1,
1.Sg8! Re6 2.Rxg4#, B~ 2.Sf6#; try 1.Sc8? B~ 2.Sd6#, but 1...Bxc8!.

## Half-pin with set mates changed (27 Oct 2026, with E. Bourd, unfinished)
evolve CHANGED=1 PATTERN=Half-pin DEFS=Sf4,Rc5 from the Qf7 family found 8/2BN2Q1/8/8/4k3/3nN1K1/1prP4/1Br1n3 (7+6, gate
PASS): set 1...S~ 2.Sc5# (Rc2 pinned), 1...Rc5 2.Qg4# (Sd3 pinned); 1.Qf7! (2.Qd5#) Sf4/Sb4 2.Qc4#, Rc5 2.Qf4#, Kd4 (flight
given). The key play is the 13 Oct Qf7 problem's; the set play is the addition. bRc1 stops 1...Rc5 2.Sxc5# in the set.
Conflict with his pure pair (1.Qg8? Rc5!, 1.Qd7? Sf4!): 1.Qg8? fails to Rc5 only if the g-file is shut (no Qg4), and the
set mate after Rc5 is Qg4 from g7 down the same file. evolve CHANGED=1 + DEFTRIES=1 (4 jobs, 5 min) found nothing.
A knight cannot do a type-1 change around Ke4: no two knight squares a move apart reach two different pairs of check squares.
