# Changed mates

Settings: bourd-changed-mates-3 (8/4p2K/Q2B4/1N1Np3/1pP1k1P1/6P1/2n1P3/8), bourd-changed-mates-4
(1K3b2/1P1p1B2/3r2p1/Q3P1RN/R1n1k2p/3p1p2/4nP2/4Nb2), claude-one-knight-change
(5NR1/8/8/5nQ1/3Pk3/3R1p2/3K4/4N3), bourd-one-knight-change (8/2K2p2/6pB/3p1nQ1/3Pk1P1/2P5/4P3/5r2),
claude-one-bishop-change-2 (7n/6b1/1Np5/R7/3Pk1K1/2Q5/8/8), bourd-two-captures-three-phase
(KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n), claude-two-captures-e5 (2R5/3n1p2/1B6/1K1kP1Q1/1P4B1/4rP2/8/8,
daily No. 3).

Mechanism: one Black effect that yields several mates; a selector per phase; then the threat. Selectors:
Black pawns guarding the mating squares removed one per phase; the queen's post; the key piece giving the
set mates and switching them off by moving; the key piece that moved giving the other mate itself.
Simplest one-defence change: set 1...Sxd4 2.Qe3#, 1.Qf6! 1...Sxd4 2.Qxd4#.
Two units capturing on one square: the capture square on two battery lines (departure opens one, arrival
self-blocks the other); the queen's post selects which departure mates; three phases for one defence.
Fast start for "two pieces defend on the same square": let them CAPTURE a White unit there
(8/3n4/8/3kP3/8/4r3/8/8), then arrange the mates, then the threat.
Two captures of the threat's guard (daily No. 3): Sd7xe5 and Re3xe5 both remove d6's only guard. Set mates by
the lines the departures open (Rd8#, Qd2# through e3); 1.Qe7 leaves the g5-d2 line and the mates change to the
knight's unguard of c5 (Qc5#) and the rook's self-block of e5 (Qxd7#). Evolve CHANGED=1 seeded with the core
8/3n4/8/3kP3/8/4r3/8/8 found it in ten minutes; bare cores found nothing. Its hits put a unit on the board only
for a set mate (Rg8 for Rd8#): give that mate to a unit that also works after the key where you can.
His answer to No. 3 (bourd-e4-selfpins, 8 Oct): the same two captures, but on e4 under the queen's rank, so in the
set they self-pin (pin-mates Rd7#/Rd1#, the pinned unit cannot block again) and after 1.Qe6 they unguard b5/c3
(Sxb5#/Bc3#). One Black error per phase. The reason came from a one-rank shift, not from a new unit. A flight on e4
was not possible: its mate needed d5, the phase selector (lessons.jsonl, 8 Oct).
Traps: the try threat and the key duals coming from the same resource (2Rn1N2/7K/3P4/3k4/pB1p1P2/3n1P2/1p1Q1p2/8);
a set+solution block cooked by any waiting move; a diagram flight that the change needs (queen on g5/h5).
Dead end: blind enumeration for same-piece changes (5M positions, nothing); the composer's 3-unit scheme
plus ONE named changed defence as the criterion succeeded in one pass.

Note (E. Bourd, 15 Oct 2026): "those type 1 - 2 - 3 are just enumerations, not real composition terms" - his way to break
down the implementation stage (unguard, self-block, line play...), separate from the theme (changes, tries...). Never present
them as terms in a post or a source line; name the theme (changed mates) and say how it is implemented.
E. Bourd's three types (bench mv88wzbb, 14 Oct 2026): (1) one White piece mates in both phases on another line, each
Black defender guarding one arrival square on each line; (2) different White pieces mate; (3) one piece has two mates
and each phase excludes one (king flights widen the geometry but make the play rigid).
Type 1, claude-changed-type1-qg8 (8/3BB3/5NQ1/4k1Pp/2pn4/2n1P3/8/7K): Sd4 guards f5+e6, Sc3 guards e4+d5; the queen on
b1-h7 (g6) mates Qf5/Qe4, after 1.Qg8! on a2-g8 Qe6/Qd5. One protector per knight pair (Sf6: e4, d5; Bd7: f5, e6).
Knights next to the king interpose on every rank/file check, so the threat is a diagonal check they cannot reach
(Qb8+ through d6). Evolve on bare cores (8 jobs) found no key; the hand design, one cure per solve, did.
E. Bourd on it: "realistically all knight moves are the same" - one change per knight, not six. Unique defences:
claude-changed-type1-unique-qg8 (8/2pK2nQ/5N2/4k1P1/7p/2nBP3/2r1p3/8): the threat 2.Sg4 is made by the e4/d5 guard
itself, so d5 hangs on the queen's new line and f5 on Bd3 alone; only Se6 cuts g8-d5, only Se4 cuts d3-f5. The f5/e6
knight stands on g7 (not d4), shutting the queen's 7th rank (no twin 1.Qf7). Search: evolve UNIQUE=1.
Type 1 with a rook and a bishop (claude-changed-type1-rook-bishop, 1K6/7b/1N1B4/1p5r/3k1pp1/Q7/nPpNBP2/2r5): impossible with
two whole queen lines (`python -m chesscomp.compose.type1_geometry d4 --types RB` prints the post pairs that work, with
knight threats, the off-line defences and the plugs). Qa3 -> Qa8: Bh7 holds d3/e4, Rh5 holds c5/d5; set Bg8 Qd3#, Rh3 Qc5#;
1.Qa8! (2.Sb3#) Bg8 Qe4#, Rh3 Qd5#. Its set Grimshaw on f5 is fake (E. Bourd: never fulfilled after the key, so
it does not exist). Before anything else check the set escape: the threat piece's vacated
square must not be mated by the set queen (Qg3-g2 and Qc7-b7 died there); a threat square on the queen's own line cures it.
Cost here: six black cook-stoppers.
Two orthogonal lines (claude-changed-type1-ranks, 8/3K4/2p1p3/7Q/N2k1PP1/8/1N3PB1/2r1r3): Qh5 -> Qh3, black rooks c1/e1;
set Rcd1 Qc5#, Red1 Qe5#; 1.Qh3! (2.Qd3#, the line's third square) Rcd1 Qc3#, Red1 Qe3#: both rooks defend on d1. Guard the
field with units that cannot mate there (knights, a bishop off the lines); by-play Rc3/Re3 (Qxc3, Qxe3) is inherent.
Two errors in one defence (E. Bourd, bourd-changed-type1-pawn-errors, 2Q2K2/1B1N4/3p4/1p6/1n1k1P2/1Ppp2R1/2b2N2/2b5):
the defender need not hold one square of each line. 1...d3-d2 opens wRg3 to c3 (set Qxc3#) and closes bBc1 to e3 (Qe3#
after 1.Qe8!). Combine any two errors (unguard, black line closed, white line opened, self-block); the queen's line picks one.
`python -m chesscomp.compose.effects POSTKEY MOVE` lists each move's errors.
Where two errors are possible (claude-changed-type1-qg8-two-errors, 8/3BB1nQ/1nP2N2/p3k1Pp/r7/p2KP1P1/8/8, the first type-1
problem redone): with no diagram flight and the threat needing the set squares guarded, every mate comes from removing a
Black guard, and on the side the queen comes from (f5/e6 for a queen above K e5) no defence can do it twice: each Black line
to one of those squares hits the other or the queen's path. A White line opened onto e6 leaves e6 a flight in the diagram.
So only the far pair (e4/d5) takes two errors: Sf2-d3, Sb6-c4 (used: arrival closes Ra4-e4, departure unguards d5), d5-d4.
E. Bourd's pawn scheme has the same split (d5 double unguard on the near squares, d2 two errors on the far ones).
`python -m chesscomp.compose.errors FEN DEF --key UCI` says which part of the move (departure / arrival) makes each mate.
Type 2 (different White pieces mate), his rook scheme: claude-type2-rooks-light (8/2n5/2B2RK1/4k3/3R4/4P1n1/8/8) and
claude-type2-rooks-full (b7/1pn5/1PB2R2/4k1P1/3R2P1/3K2n1/8/8). Rd4 mates on d5/e4, Rf6 on e6/f5; Sc7 guards d5+e6, Sg3 e4+f5
(not Sd6, which both rooks capture). All four squares touch the king, so the selector is protection: Bc6 (d5, and e4 through
d5) in the set, 1.Bd7! (e6, and f5 through e6). The far square of each pair needs a second guard in the near mate (e4 in
Rd5#: Pd3/Kd3; f5 in Re6#: Kg6/Pg4). A mutate needs a set hole, or every waiting move solves (Kf7, Bb7, Rg6 cooked the
complete block): leave one variation unguarded (light, one change) or let a black pawn take the key piece (full, 2x2, three
units and an escape-looking key). Trim block problems only with the 15 Oct fix of chesscomp.compose.trim.

## Two pieces mate, a third unit selects (E. Bourd, 15 Oct 2026)
"Not the same white piece does all the play, but 2 pieces ... the change is not due to movement of the piece, but rather
other effect which makes only 1 of the 2 mates possible." Model: Ahues, Die Schwalbe 1997 4th Prize (psis-8e536d7627),
1.Sc5? / 1.Sc7! after 1...Se3+: fxe3# needs Bb8-e5 open, Qxe3# needs d5 guarded; Sc7 closes the one and guards the other.
Mates on one square by two pieces: both must check from it (Q+R on a line, Q+B or Q+P or B+P on a diagonal, two knights).
Our scheme, claude-type2-d4-scheme, 3Q1R2/1r6/8/2pNN3/4kP2/2P5/8/3RK3: the knight d5 masks Qd8's file and guards e3, so
1...c4 (unguards d4, guards d3) gives 2.Rd4# in the set and 2.Qd4# after any knight move (Rd4+? Ke3). One departure, two
effects. What it took (session log 15 Oct): every queen square near the king gives mates in one (Qf6, Qd7); the knight's
check squares (c3, f6) must be occupied, or a check by the knight cooks once the file opens; a black bishop as the
defender reaches d6/d7 or checks the White king on a dark diagonal - a quiet pawn defence (c5-c4) away from d4 avoided both
and the mate-captures-defender flaw. All knight moves then solve; chesscomp.compose.keysel found the reason for one key
(Rb7, cut by 1.Sc7!; 1.Se7? Rd7!). Try with the same change: claude-type2-d4-try (+Bf1 masked by e2: 1.e3? (2.Bd3#) c4
2.Rd4#, Rd7!), threats changed on one square d3. On d4 only Q and R can mate, so a third phase needs another square.
His doubling (bench 16 Oct 2026), bourd-type2-doubled, 8/8/2PQ1Br1/2KNP3/4k1P1/2pppR2/3qn1P1/8, 1.Sb4! (2.Qd5#):
1...Qa2 Rxe3# -> Qxd3#, 1...Sf4 Rxf4# -> Qd4#. He listed the guard pairs first (the knight on d5 holds e3/f4 for the
rook; the opened file gives d3/d4 to the queen), then the defences whose geometry yields both, then the key's reason from
the change itself: 1.Sb4 protects d3 (1.S~? Qa2!, 1.Sf4? Rxg4!) - a white correction, better than a cook-stopping guard.
2x2 guard swap by a knight move alone (E. Bourd, 16 Oct 2026: "no need for line opening ... just a knight move can swap 2x2
squares of guards"). Facts found while trying (K e4): knight squares guarding two field squares - b4{d3,d5} c2{e3,d4}
c4{e3,e5} c6{d4,e5} e1{d3,f3} e2{d4,f4} e6{d4,f4} e7{d5,f5} g2{e3,f4} g4{e3,e5} g6{e5,f4} h4{f3,f5}; swaps with disjoint
pairs: g2->h4/e1, e7->c6/g6, b4->c2/c6, c2->e1, h4->g6. A knight attacks one colour only, so the old pair and the new pair
differ in colour: a defence that frees one square of each needs a rook/queen line (orthogonal neighbours) or a self-block,
never a bishop. In every geometry the rook line through one pair runs on into the other pair (2x2 shape), so a block is
needed (his black pawns d3/e3 did it). If the knight protects the square it vacates (d5->b4 protects d5), a black guard
of that square attacks the knight in the diagram. Random searches (scratch swap2.py, 3 rounds) gave single changes only.
Published model of the pure swap: Strebkovs, Vratnica-64 2003, Recommended (psis-c1d0392e2e), b1Q1N3/5p2/5K2/N1PkP3/1n4R1/8/1n2P3/6b1,
1.Sb3! (2.Qd7#) Bxc5 Qxc5#, Bd4 Rxd4# (set Sc7#, e4#): Sa5 covers the flights c4/c6 for the set mates, Sb3 protects the
capture squares c5/d4 for the key mates; one black bishop lands on either square. Our scheme on that model (no threat yet):
claude-knight-swap-2x2-scheme, 5r2/8/2N5/8/2P1k3/4p2Q/1KP3N1/8, Sg2->h4: set Rf5 Qxe3#, Rf3 Qe6#; after Sh4 Rf5 Qxf5#,
Rf3 Qxf3# (each rook landing cuts one queen line h3-e3 / h3-e6 and becomes the other's capture target). Obstacle: the key
gives f4 (the knight's old guard), so a threat must check along the 4th rank, and the f-file rook interposes on f4.
Principle from Strebkovs (why his key gives no flight): the squares the knight gives up are ALSO covered by White line
pieces, and the set mates interfere with those lines themselves (Sc7 shuts the queen's c-file, e4 the rook's 4th rank), so
only they need the knight. Next stage of ours: claude-knight-swap-2x2-qe6, 8/6p1/5p2/7N/2P1k3/7Q/1BP3Nn/K1n5, threat
1.Sh4 (2.Qe6#): Sf3 Sg3# -> Qxf3# (the knight could interpose on e5), f5 Qe3# -> Qxf5# (interference on h3-e6). Faults:
set dual Sg3/Qg4 after Sf3; after the key 1...f5 Qxf5+ Ke3 (Qxf5 cannot cover e3, and a static guard of e3 would also
protect the set mate Qe3 after the key). Way out: both set mates must rely on f4 only and each must remove f4's static
guard itself (the h5 knight's two checks Sg3/Sf6), but Sf6 needs f6 free after 1...f5 and guarded in the diagram.

## One piece, two mates, one excluded per phase (E. Bourd's third way, 16 Oct 2026)
Selector: a unit that stands on one line of the mating piece and steps onto its other line. Queen d1, Ke4: the White
king d2 shuts the d-file in the set; 1.Ke2! opens it and shuts the d1-h5 diagonal, so a defence that frees one square on
each line (f3 or g4 / d3 or d5) gets the diagonal mate in the set and the file mate after the key. The key also creates
the threat Qd4# (the file) and takes over the queen's f3 guard. One Black unit must free a pair: g4+d5 (Sf6, or Be6, but a
bishop move keeps one of them), d3+f3 (Se1, Se5 in the field, or a 3rd-rank rook, which checks with Re3+ once the king is
on e2), f3+d5 (Rf5 through f4/e5). Only {g4,d5} with {d3,f3} gives two different key mates. Se1 also frees c2 and g2:
Qc2/Qb1/Qh1 duals (bPb3 guards c2, Rb1 shuts the first rank, Sg1 protects f3 and blocks h1).
Scheme: claude-type3-queen-lines-scheme, 7b/8/5n2/R7/4k3/1p2P3/3K4/1R1Qn1N1 (both knights random; Bh8 masked by Sf6 reaches
d4). Result: claude-type3-queen-lines, 2B5/8/2N2n2/8/2P1k3/1p2P3/3K4/1R1Qn1N1, 1.Ke2! (2.Qd4#) Sd7 Qd5#, Sc2/Sf3 Qd3#,
Sd3 Qxd3# (set Qg4#, Qf3#); try 1.Kxe1? Sd7!. To make a knight's defence specific, give the threat a flight that only one
landing opens: f5 held by Bc8 alone, cut on d7. The e1 knight stayed with three defences: Sd3 always blocks the file, and
a pin of c2 or f3 is a check in the diagram. Search: `python -m chesscomp.compose.type3` (KEY, MP, FIX; tested).
Pawn selector (E. Bourd: "change the king into a pawn and swap directions"; b1 rook "too bad"; Sd3 annoying): turn the
scheme so the step goes up: claude-type3-pawn-g5, 2B2r2/8/2n3p1/1NNpk3/6PQ/5pK1/8/8, 1.g5! (2.Sd3#) Rxc8 Qf4#, Sb4 Qd4#
(set R~ Qg5#, Sb4 Qe7#). bRf8 holds f5 (the interposition square of Qg5+) and f4, bSc6 holds e7 and d4; Bc8 holds e6/f5 for
the knight threat. A threat by another piece removes the block defences; each unit has one defence. Plugs: bPg6, bPf3, bPd5.
The other direction (Qh5, g4-g5 opening h5-d1) closes the rank that guarded d5/e5/f5 and gave no non-queen threat.
Search: type3 NOQTHR=1 (threat not by MP), QUIET=1 (capturing defences do not count).
His step (bench mva9ts5k): bourd-type3-pawn-g4, 1B6/5r2/1N6/1Kn3p1/2Npk3/6PQ/4P3/8, 1.g4! (2.Sd2#) Rc7 Qf3#, Sb3 Qd3# (set
Qg4#, Qe6#): a one-rank shift and Bb8 turn the capture 1...Rxc8 into the cut 1...Rc7. Left: 1...Rf3 2.Qxf3#. His way out
needs a new structure: threat due to f3, thematic mates on e3/d3; no black unit holds e3 with g4/f5/e6 (colours, knight
squares), so e3 needs a self-block or a line effect.
Other pawn direction (his bench core mvattjff: Qb5, Pc4, Ke4, bSb4; c4-c5 shuts the 5th rank, opens b5-f1): the key
strips d5/e5/f5 and gives flights, so it is a mutate. Scheme claude-type3-c5-flights-scheme, 3N4/8/2RB1p2/1Q5K/1nP1k3/2R5/2P1N3/8:
1.c5 Kd5 Qc4#, Kf5 Sg3#, Sb4~ Qd3# (set Qd5#), f5 Qc4# (set Qe5#); cooked (set hole 1...Sd3 lets Rh3/Rg3 wait), 9+3.
Pairs in this geometry: Sb4 d5/d3, Sb6 or a bishop leaving a2-g8 d5/c4, Sc3 d5/e2, Sg3 f5/e2; Pf6 e5 + the f5 block.
His threat version (bench mvbgkei9): bourd-type3-c5-threat, 4r2r/1p6/1P1P1RNp/bQ6/1nP1kNb1/2p3P1/2p1pBPK/8, 1.c5! (2.Qc4#)
Sc6 Qd3#, Be6 Qxe2# (set Qd5#, Qe5#): the field holds d5/e5/f5 itself, so no flights; Be6 cuts Re8 from e5 in the set and
leaves e2 after the key. 11+11 (wPg3 can go): the price of the threat in this direction is the field.
Reduced: bourd-type3-c5-threat-18, 4r3/3p4/3P1RN1/bQ6/KnP1kNb1/2p5/2p1pBP1/8 (bPd7 for four plugs, Ka4). His one-piece pair
completed: claude-type3-c5-blackqueen, 8/1p1R4/2N2R2/pQ2p2q/1nP1k3/8/4p3/1KB5, 1.c5! (2.Qc4#) Qf7 Qxe2#, Sxc6/Sc2 Qd3# (set
Q~ Qxe5#): bQh5 holds bPe5 on the rank and bPe2 on the diagonal; 7+7, but captures in both queen mates and two defences each.
His Bh5 + Sh4 (1...Sf3 frees f5, cuts h5-e2) gave nothing in two runs.
Knight guard swap, done light: claude-knight-swap-c2, 8/8/5R2/K3p3/1N1Pk3/2Q3p1/5n2/8, 1.Sc2! (2.Qf3#) exd4 Qxd4#, Sd3 Qc6#,
Kd5 Qc6# (set exd4 Qe1#, Sd3 Qxd3#): b4 {d3,d5} -> c2 {e3,d4}, the key gives d5. Found by type3 MP=any BYMOVE=1 (key fixed),
then bPg3 for the search's black bishop. 1.Sc6? fails to Kd5 and Sd3 (no single-refutation try while d5 is given).
Two rooks, two mating pieces (his bench mvbifzbn): Re1 holds e2/e3 (Se2#/Be3#), Rb5 holds e5/f5 (Be5#/Sf5#); e3 guarded ->
bishop mates, e4 guarded -> knight mates. With a threat: claude-two-rooks-c3-scheme, 8/4K3/2R5/1r6/3kPBN1/4p1N1/2P5/4r3,
1.Sf2 (2.c3#) Rb3 Sf5#, Rc1 Se2# (set Be5#, Bxe3#); refuted by Rb7+, Re5+, Rc5, exf2. Obstacle: 1...Re3 guards c3 along the
3rd rank, and only the e1 rook can hold e2+e3. Idea left: knight mates in the set, the key protects e3, so Re3 meets Bxe3#.
Finished by him (bench mvbno7uo): no fxe3 (a black pawn on the square), a rook threat that needs the square the key
piece guards, board turned: bourd-two-rooks-sg6, 8/4NN2/4B3/5p1r/4k3/K1P1pR2/P3P3/3r4, 1.Sg6! (2.Rf4#) Rh4 Sg5#, Rf1 Sd6#
(set Bxf5#, Bd5#). One knight is the selector and the threat's guard: on e7 it holds d5 (bishop mates), on g6 e5 and f4.
Reduced from his 8+7 (-wPe5, Ka3+wPa2 for Ka6+a5+b6). No third pair from any White first move (separate.py).

## Battery key, flight-giving key (17 Oct 2026, "another type of 2x2")
Both basic forms are published, so ours needs a second layer from the start:
- Battery built by the key, mates on the same squares: Cuppini, Problemesis 2003 (psis-2b6418e028),
  8/p1P4K/3P4/pN3Q2/k2N4/P2R3R/1PnB4/1bnn4: set 1...Sxa3 Rxa3#, Sxd4 Rxd4#; 1.Qd7! (Q behind Sb5) Sxa3#, Sxd4#.
- Flight-giving key, the post-key mates by the key piece cover the flight: Marandyuk, Eretria 2005 (psis-d5310cd9be),
  B7/2Q5/6K1/3pN3/4k3/1N4P1/2n2P2/2br4: set Se3 f3#, Sd4 Sc5#; 1.Qf7! (2.Qf5#) gives Kxe5; Se3 Qf4#, Sd4 Qxd5#,
  Kxe5 Qe7#. One knight self-blocks d4 or e3; the set mates need Qc7's guard of e5.
Obstacles found by hand (no sound result in 28 type3 runs, 401-428):
- Knight battery Re8/Se6 with a key that gives d5: only Sc7 (and Sf4) cover d5, so every other discharge needs d5
  blocked by Black; one post-key mate, not two. Discharges also repeat the set mates (Sc5/Sg5 check directly).
- A queen whose set mates cross d5 (Qg8-c4) always has Qd5: any White guard of d5 protects her there.
- Pair holders for squares of different lines rarely exist: no knight, bishop or rook guards both c6 and e5.
Plan: flights as the phase separator in three phases (set Qd7 guards d5 and f5; try 1.Qc8? gives d5, mates cover it;
key 1.Qd6! gives f5) - a Zagoruiko where the flight alone changes the mates. type3 TRY=, MP=key, FLIGHT=1 (tested).
Battery variations (E. Bourd, 17 Oct 2026: "a problem with batteries ... just 2 variations, then tries"): sound scheme
claude-battery-fleck-scheme, 3n1RBB/8/n3P1N1/R7/4k3/6P1/2Pb1P2/7K, 1.Bh7! (2.Se7#/Sh4#) Sc5 Se7#, Sf7 Sh4#: each black knight
cuts one white rook (Ra5 for d5, Rf8 for f3) and the one discharge covering the opened square mates; the other coverer
fails because it shuts a guard line itself (Sf4 shuts Rf8, Se5 shuts Bh8). Double threat: the thematic discharges also
mate before the defence. Why (lessons.jsonl): adjacent landings cannot be selected by an open square (the protector guards
it), so only distance coverers can, and those threaten. Published battery threats are often 2.S~# with variation
discharges that fail in the threat position (his Problemesis 2004, psis-0f9bcf61f7): the missing piece is a square open
before the defence that the defence closes.
Battery held by a black piece (his bench mvcc8z65, 17 Oct 2026): bourd-queen-unguard-battery-scheme, the black queen
interposes on the battery line; her two captures each remove a White guard and leave the line, and one discharge
re-guards the square (Qxg4 Sc3#, Qxf1 Se3#). `python -m chesscomp.compose.battery_guards KING FRONT REAR SQ1 SQ2 [q|r|b]`
enumerates where the piece and the two guards can stand (Kd4/Sd5/Rd8: queen f5 Rc2/Sf2 or b5 Sb2/Re2). Ours:
claude-rook-knight-queen-unguard-scheme, 1B1R4/8/1P6/2pN1q2/3k4/8/2RPPN2/K7, Qxf2 Sf6#, Qxc2 Se3# (Sc3 shuts Rc2); the
threat (2.e3#) is the open problem. His plan next: pawn, bishop-knight, bishop-rook, rook-bishop, distant rook-knight
batteries with the same concept, then tries.
Clean post-key (no key yet): claude-queen-unguard-postkey-c4, K7/2R2N2/4p1B1/1PBk4/R2Npq2/2P5/2P1P3/3Q4, threat c4#, 1...Qxc7
Sb3#, 1...Qxf7 Sf3#, nothing else defends. Got there by turning the scheme 180 degrees (postsearch KMP=d4), rear rook ->
queen, Bg6 behind the black e4 pawn, pawns shutting the queen's lines to c4. Key obstacle: the threat must need the rear piece.
Pawn battery (Qb1/c2 v Ke4; 2.c3 guards d4, 2.c4 guards d5): claude-pawn-battery-rook-holder, 8/B2r1B2/2b5/4p3/1P2k1Kn/4pp2/2P5/1Q4N1,
1.Sh3! (2.Sg5#) Rxa7 2.c3#, Rxf7 2.c4# (bRd7 interposes on d3). The interposed holder is pinned, so 2.c3+/c4+ Rd3 and the
threat cook every key that leaves the threat: bring the threat piece with the key (unmask_search KSQ/FSQ, THREAT=). Dead ends
(lessons.jsonl): a queen-move threat (needs a d2 blocker; none works), a rook pinning c2 on the 2nd rank, a knight holder.
Pure tries planned: 1...Rxa7! when e3 is guarded only by Ba7 and the key piece, 1...Rxf7! when the try blocks c4.
