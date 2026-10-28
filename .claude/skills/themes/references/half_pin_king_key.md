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

## Bishop + knight half-pin on the e-file, Ke4 (27 Oct 2026, unfinished, a new scheme with E. Bourd)
Re8-Be6-Se5-Ke4. After a knight move the bishop cannot interpose on d5/f5: mates Qc6/Qb7 (via d5), Qg6 (via f5).
After a bishop move the knight cannot interpose on d3/f3 or take on c4/g4/c6/g6: mates Qc2/Bc2, Bg2/Qg2, Qc4, Qg4.
Sound basic setting (unmask_search um1): 1Q2R3/8/2p1bP1N/2R1n3/4k1p1/2Pn2K1/1B2NP2/1r3B2, 1.Qd6! (2.Qd4#) Bd5 2.Bg2#,
Sf3 2.Qxc6#; try 1.Qd8? Sf3! - one-sided (fatal since issue #21), 18 units. What blocks the second layer:
- With the threat Qd4#, 1...Bd5 defends only by blocking the queen's path from above (d6-d8). Every mate after Bd5
  that does not itself cover d4 needs another d4 guard, and that guard protects Qd4: Bd5 stops defending. So the
  Bd5 mate must cover d4 itself: a rank-4 check from the right (Qg4/Rg4, x-ray d4) or an adjacent Qd3/Qe3.
- A queen on d7 or c8 reaches f5 through the vacated e6 after Bd5: 2.Qf5# ignores the pin of the knight (the knight
  cannot touch f5), a half-pin variation in name only; 2.Qg4# uses it. A queen on d7 is en prise to Se5 (escape key).
- Mates on c6 and g6 from the 6th rank (either side of e6): after a knight move 2.Qxe6+ (check down the opened
  e-file) mates whenever Qc6 does, unless Black defends e6, and a pawn f7 that does guards g6.
- The pinner takes the pinned knight with mate (2.Rxe5#) after a bishop move whenever e5 is guarded for the
  knight-move mates (the king's new e5 flight). A Black recapture on e5 (a knight on d3, as in um1) cures it.
- With the queen able to reach d3 and d3 guarded (Qc6 needs d3 covered), 2.Qd3# is a dual of Qc6 after every
  knight move: block d3 with a Black unit (um1's Nd3) or let Black guard it (a knight on c5).
- A knight on e6 never reaches d5/f5: with Se6 over Be5 the self-blocks are on d4/f4 (Sd4, Sf4, Bd4, Bf4).
Known concept, do not repeat it bare: queen posts on a black half-pin (Delobel, Problemesis 2003, psis-aba981b8d6:
1.Qd1/Qb5? Rd2!, 1.Qb3/Qd7? Se5!, 1.Qa6!), interference tries by the key knight (Kapros 2002, psis-0dd597ba62).
Blind searches from a bare core (evolve, an add-only beam over post_spec) lock onto a mask on e7 or capture mates:
seed them with a planned guard scheme.
Second layer for the 12-unit setting 1Q2R3/8/2p1b2N/2R1n3/4k3/2Pn2K1/5P2/8 (28 Oct, E. Bourd: "either 2 changes, or 2
tries. just 1 is almost ruining it"): structurally blocked in this frame. After 1...Bd5 every queen mate on the
f5-g6-h7 line works too, so any queen post that answers 1...Sf3 that way also answers 1...Bd5; only d6 avoids it (it
reaches g6 only through e6). Sweeps of every single change around it (and from the queen on c7, f8, d8) found no try
refuted by 1...Bd5 alone and no two distinct set mates; the only two-change form is a split: queen f8 with bPg4, set
1...Sf3/Bd5 2.Qf5# -> 2.Qxc6#/2.Qg6# (4RQ2/8/2p1b2N/2R1n3/4k1p1/2Pn2K1/5P2/8, gate PASS). The crossing idea (d6 = d-file
x 6th rank, 2.Qd5#/2.Qg6#, tries 1.Qd8? Bd5!, 1.Qb6? Sf3!) dies on the diagram flight d5: any guard of d5 also
protects 2.Qxd5# after 1...Bd5. E. Bourd rotated it on the bench (4th-rank pin Rh4-Bf4-Se4-Kd4, queen f5): there both
mates pass the vacated square (1...Sg5 2.Qd3# through e4, 1...Be5 2.Qf2# down the f-file through f4), so f5 is the
crossing of the f-file and the b1-h7 diagonal and the one-line posts (f8, g6/h7) separate the mates.
E. Bourd's rotated setting (bench, 28 Oct 19:08): b7/3p1K2/Q4pB1/R1bnkN2/7R/q1np4/5N2/3r4, half-pin Ra5-Bc5-Sd5-Ke5. Set
S~ 2.Qd6#, B~ 2.Qxf6#; 1.Qc4! (2.Sg4#) Se3 2.Qd4#, Bxf2 2.Qf4#, Bd4 2.Qxd4#. Why the changes work here and not on the
file: with the pin along a rank, each pinned unit guards a square on both sides of the pin line (Bc5: d6 and d4; Sd5: f6
and f4), so the queen mates from the 6th rank in the set and from the 4th after the key, every mate using the pin.
His dual avoidance (he had to point it out): after a knight move the d5 flight forces the mate onto the d-file (2.Qd6#,
2.Qd4#); after a bishop move bQa3 sees d6 through the vacated c5 in the set, and after the key the bishop stays on the
a7-g1 line guarding d4, so the mate goes to f6/f4. bQa3 is the mechanism, not a cook-stopper; bPf6 keeps 1...Se3 the
knight's only defence (without it 1...Sf6 2.Qd4# repeats). His lighter version (21:13, 16 units, gate PASS):
b7/3p1K2/Q4pB1/R1bnkN2/7R/q2p4/3n1N2/8: bQa3 also guards d3 along the 3rd rank (bRd1 and bSc3 gone), bSd2 guards e4 and
c4, so 1.Qc4! is a sacrifice (1...Sxc4 2.Re4#); bBa8 holds d5 against 2.Rxd5#/Qxd5#.
