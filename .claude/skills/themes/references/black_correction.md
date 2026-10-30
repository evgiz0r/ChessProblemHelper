# Black correction (knight)

Reference: `claude-knight-correction`, b3N3/8/ppn1p3/4k3/3R2P1/4P3/7K/2Q5 #2 (6+6), session 26,
built in E. Bourd's order.

1.Qc4! (2.Re4#)  1...S~ 2.Qc7#  1...Sxd4! 2.Qxd4#.  Try 1.Qc2? (2.Qe4#) S~ 2.Qc7# but 1...Sxd4!

## A set-play correction counts (E. Bourd, 26 Oct 2026)
Velimirović, Wola Gulowska 2002, 4th Prize (K7/3N4/Q2nP3/3kB3/8/3pR2B/1p6/3Nb3): set S~ 2.Bg2#, Sb5! 2.Qxb5#,
Se4! 2.Rxd3#; 1.Re4! closes the long diagonal, and the correction moves become plain defences with changed mates
(Sb5 2.Qb7#, Sf5 2.Qc4#, Sxe4 2.Se3#). His reading: "its both. the correction does exist, and its part of the
problem. correction moves becomes defenses, and mates on them change". The correction need not survive the key: a
set-play correction whose moves change their mates after the key is correction AND changed mates.

## The order (E. Bourd)
1. **Threat.** Re4#: the rook leaves d4, the queen on c4 keeps e4 and f4 covered along the rank.
2. **Random defence.** The knight on c6 sits on two lines: the black bishop's a8-e4 (opening it lets
   Bxe4 parry the threat, so EVERY knight move is a defence) and the white queen's c-file (opening it
   gives Qc7#, the error). A line opening is the easy way to make "any" move a defence; the same move
   must carry an error, here a second line opening for White.
3. **Correction.** A knight cannot re-guard what it guarded (colour parity), so it corrects by
   capture: 1...Sxd4 removes the rook whose rank cover of e4 Qc7 needed (2.Qc7+ Ke4). Its minus: it
   stands on d4 where the queen captures it with mate, Qxd4 covering d5/d6/e4/f4 itself.

## What the units do
- bPe6 attacks d5: without it Qd5# and Rd5# are extra threats. bPa6/bPb6 guard b5/c5 against the
  queen's rank checks. wPe3 blocks the e-file (Qe1/Qe3 mates) and protects d4 for Qxd4. wPg4
  covers f5. wSe8 covers d6 and f6 and cannot mate. wKh2 stands on the b8-h2 diagonal so the queen
  never mates on h2.
- The try 1.Qc2? shows why the key square is c4: the queen must be able to take on d4.

## Dead ends, in order
- Bd6# as the random mate with bishop f8 behind e7: the knight's other squares (c8, d5) also guard or
  block, and interpositions on the e-file kill Qe8#.
- Mate A on a square the black line also guards (Qa5 through d5 with a bishop on a8) fails: the
  defence line parries the mate too. Mate A must avoid the black line.
- Qc3 behind Rd4: battery, cooked by every rook move. Qc4: Qd5/Rd5 double threat until bPe6.
- Sb4 interference on the b-file killed a b-file mate (Qb8): choose a mating line the knight cannot
  cross.

## Adjacent knight, self-block correction (session 27, unsolved; the rules)
Cell: bK e5, bS d6, wPd3, 1...Se4 2.d4# (the pawn gives up e4, the knight fills it).
- Every destination of the knight attacks d6, so any white line through d6 is interposed by every
  knight move (Qb8/Qc7 on b8-h2 never mate). The far squares also interpose on e3 (c4, f5), c5
  (b7, e4) and g5 (e4, f5, f7). The one mating line no far move touches is h2-e5: Bg3/Bh2/Qg3/Qh2,
  parried by the adjacent squares e4 and f5 (they guard g3). Pair the e4 self-block with that mate.
- The random mate must be created by the knight's departure. Opening a white ROOK line does not
  work here: a d-file rook covering d4/d5 gives Bd4# (bishop f2) and Rd5# (any second d5 guard);
  a 6th-rank rook gives Re6#. Opening the queen's f8-c5 diagonal fails when the threat is Qe7#
  defended by Ba3: the bishop takes on c5. A 6th-rank queen mate on f6 is parried by Se8 too.
- Bishop f2 mating on g3 (it covered d4, so the mate fails in the diagram on d4) means every flight
  is covered in the diagram; then any queen check is mate and each of the queen's lines needs a
  blocker. A 7th-rank threat from a7 and a key rook arriving on d7 exclude each other.
- Small: bPd7 jumps to d5 through the emptied d6 and interposes on 5th-rank checks; an 8th-rank
  queen reaches d5# once d5 is protected.
- Open directions: enable the random mate by an UNGUARD (d6 guards c4 and f7, both knight-mate
  squares), or use the other cell (knight on d5, self-blocks on the diagonal squares f4/f6).

## The one that worked: E. Bourd's adjacent knight (session 27)
`bourd-knight-double-correction`, BQ2R3/3K4/2N5/1np2p2/2k2P2/p4R1b/4P3/3Nb3 #2 (9+7).
1.Re7! (2.Qg8#) 1...S~ 2.Qb3#, 1...Sd4 2.Se5#, 1...Sc3 2.Se3#. Tries 1.Rh8? Kd5!, 1.Re5? Sd4!,
1.Ree3? Sc3!
- The knight on b5 stands NEXT to the king. Its departure gives the king b5, so every knight move
  defends against Qg8#: no line through the knight is needed. The error is leaving the b-file.
- Two self-block corrections with different correction motives: Sd4 guards b3 (Se5# also unmasks
  Ba8 on d5); Sc3 cuts the f3 rook's protection of b3 (Qb3+ Kxb3).
- The mirror: the key rook has no true random move (Rh8 loses e4 and fails to Kd5), its aggressive
  corrections Re5/Ree3 are refuted by the black corrections Sd4/Sc3, and Re7 is the correction with
  no negative effect. Two correction plays, one from each side; each could be a problem alone.
- How it was built: random move + one mate on three units; the threat; option 1; cleared and rebuilt
  as option 2 with a second correction; cooks (Re4+ by a discovered-check battery Kd7/Bh3/f5, f4
  against the by-product f4+; a3, Be1) and economy last. Rook e6 -> e8 saved a pawn and turned four
  same-refutation tries into three distinct ones.

## Bishop correction by line opening (daily No. 2, 7 October 2026)
`claude-bishop-correction-e3`, 3R4/8/6K1/4P3/3bk3/N1p3Q1/8/8 #2 (5+3).
1.Sc4! (zugzwang) B~ 2.Qg4#, 1...Bxe5 2.Qe3#, 1...Be3 2.Qxe3#, 1...c2 2.Sd2#. Tries 1.Sb5?/1.Sb1? B~ 2.Sxc3#
but 1...Bxe5!
- Random error: the bishop on d4 sits between the king and the white rook's file; any move opens d3-d5,
  so the queen may leave the third rank (it guarded d3 and e3; the key knight takes e3 and e5).
- Correction motive, one for both: guard f4, so that 2.Qg4+ is met by Bf4.
- Dual avoidance read from the random squares: all five (a7, b6, c5, f2, g1) lie on a7-g1 and keep e3,
  so Qe3 never mates after a random move; Bxe5 leaves that line and allows it. Be3 errs by standing where
  the queen takes with mate (as Sxd4 Qxd4 in the knight setting above).
- Weak point: both corrections are answered on e3. Next: a second correction whose mate is elsewhere.
- Rook version (no key found): bK e4, bR d4, wB a7 behind it, wQ b5, wS f3: R~ 2.Sg5# (a7-e3 opened),
  Rd5 2.Qe2#, Rc4 2.Qxc4#, Rd3 2.Qe5# - three corrections, but the error needs e3 open, i.e. a diagram
  flight, and every attempt to give e3 with the key failed (8/B7/8/1Q3p2/3rk3/2p2NK1/8/8 is a zugzwang
  set refuted only by pawn tempo moves).
- Tool: `CORR=d4 NCORR=2 DEFS= SEED=<hand sketch> python -m chesscomp.compose.evolve JOB OUT` (see docstring).

## Rook beside the king (daily No. 17, 22 October 2026, no sound threat version)
- Scheme: bK e4, bR d4, wB a7 behind it on a7-e3, wQ on b5 (5th rank and b5-d3 diagonal), wS f3. Every rook move opens
  the bishop to d4 and e3 (the random error). Rd5 cuts the queen's rank to e5, Rc4 her diagonal to d3, Rd3 pins Sf3
  against a king on h3. The key Qb3-b5 gives the flight e3 (the queen held it along the third rank).
- Block: 8/B7/8/4PpP1/3rkp2/1Q3N2/3p4/3K3B, 1.Qb5! R~ Sxd2# (double check with Bh1), Rd5 Qe2#, Rc4 Qxc4#. Sound, but the
  gate fails a block whose only mobile unit is the corrector ('simple block').
- Capture threat: 8/B7/8/5p2/2Prkp2/1Q3N1K/6P1/8, 1.Qc3! (2.Qxd4#) R~ Sg5#, Rd3 Qe5#, Rxc4 Qxc4#. Sound, but a rook moving
  along its lines still guards d4 from its new square: the threat is parried by arrival, no random move (E. Bourd, 17 Oct;
  analysis.py `_corrections` drops it).
- Open: a threat parried by the rook's DEPARTURE, i.e. a black line through d4 (bB b6 -> e3/f2, threat 2.Sf2#), with the
  white line through d4 (Rd8 on the d-file) giving the random mate. Sketch 1Q1R4/8/1b6/5p2/3rkp2/... never got its guards.
- Search: `CORR=d4 CTRY=1` (evolve refuses simple blocks by default; CTRY wants a try refuted by a correction).

## Study: Velimirovic, Wola Gulowska 2002, 4th Prize (psis-6398733b04)
K7/3N4/Q2nP3/3kB3/8/3pR2B/1p6/3Nb3. Set: S~ 2.Bg2#, Sb5 2.Qxb5#, Se4 2.Rxd3#. Key 1.Re4! (2.Rd4#) Sb5 Qb7#, Sf5 Qc4#,
Sxe4 Se3#, Kxe4 Qc6#. The knight d6 interposes on e4 and shields e6 from Qa6: two jobs, so the random move's error is
double. The key shuts the random mate's line and changes all three mates; the correction itself lives only in the set.

## Rook correction on a crossing square (28 Oct 2026, sound, single phase so far)
- 6N1/6K1/1b1p1R1P/3rk3/2Q1b3/B2p4/8/8, 1.Se7! (2.Sc6#). Set and solution: R~ (Rb5/Ra5) 2.Bxd6#, 1...Rc5! 2.Bb2#,
  1...Rd4! 2.Qe6#. Every rook move opens bBe4-d5-c6 against the threat (defence by departure).
- Errors: off the d-file the rook no longer guards d6 (Bxd6) and can no longer interpose on d4 (Bb2+). After Rb5/Ra5
  Bb2+ fails to Rxb2 / Bd4 (bBb6 through c5). 1...Rc5 stands on both diagonals: it cuts Ba3-d6 (no Bxd6) and its own
  b6-d4 (no Bd4), so Bb2# - a Novotny-like self-interference. 1...Rd4 keeps the file (d6 guarded) and blocks d4, so
  the queen may leave c4 (Qe6#); after a random move Qe6 leaves d4 free. The queen on c4 is the only square that covers
  d4 and d5 and reaches e6 through d5.
- How it was found: the flight version (bK e4, bR d4, bPd3 guarded along the file, wQc5, 1...Rd5 Qe3#) had the hole
  1...dxc5 from the blocker pawn d6; flipping the board top to bottom points the blocker's captures away from the
  queen (black pawns do not flip), and the flip created Bb2# through the d4 square that a black pawn cannot step back
  to. The black bishop b6 then made Bb2 the correction's mate; its own 1...Bd4 was a hole until the threat moved to
  the knight (2.Sc6#, masked by the rook on bBe4's diagonal).
- Flaws: the key only adds the threat (gate 'single phase', 'static key'); wPh6 stops 1.Sh6 (Sf7/Sg4); the bBe4
  random moves have duals. retract gives only flight-taking keys (1.Kg7, 1.Rf6); evolve CTRY=1 and CHANGED=1 found no
  second layer in 280 s each.
- Dead ends of the day: a white queen behind the rook on the d-file (cs3: R~ Qd5#, Rd3 Qg4# x-ray) always leaves the
  moves toward the line piece (Rd2, Rxd1) without an error; the rook guarding d4 along the 4th rank (R~ Qd4#, Rc4
  cuts bBb3-d5: Qd5#) gives Ra4 no error and a post-key full of other solutions.

## His bench scheme: rook beside the king, corrections on its own rank (29 Oct 2026)
- His kernel (bench steps 331-341): bK d4, bR e5, bPf5 and bPb5 closing the 5th rank, wBb8 (threat Bxe5#), wSh6
  (R~ off the rank unguards f5: Sxf5#), wPf4 (protects e5; 2.fxe5 is no check, a white pawn on e5 attacks d6/f6).
  Corrections 1...Rd5! and 1...Rc5! keep the f5 guard and self-block a flight.
- Dual avoidance it needs: Sxf5 needs c5 and d5 guarded after R~, so the guard of each self-block square must be the
  unit that mates after that self-block and leaves the square doing it. Sb4 guards d5 and mates Sc6# after Rd5
  (Sc6 after R~ leaves d5); Qc2 guards c5 down the c-file and mates Qd3# after Rc5 (Qd3 after R~ leaves c5).
  (A knight CAN guard d5 and check d4 in one move: b4 -> c6; my parity argument was wrong.)
- Sound: 1B6/2Q3p1/1P5N/1p2rp2/1N1k1P2/5K2/5P2/8, 1.Qc2! (2.Bxe5#): the queen unmasks b8-e5 and stays on the c-file;
  set R~ Sxf5#, after the key also Rd5 Sc6#, Rc5 Qd3#, Re3+ fxe3#. bPg7 stops 1.fxe5 (1...g6 guards f5), wPb6 stops
  the dual Ba7#. Zugzwang version without the bishop: 8/8/2Qp3N/1p2rp2/1N1k1P2/5K2/5P2/8, 1.Qc2! zz (bPd6 protects e5).
- Not working: the threatening bishop on the long diagonal pins the rook (every mate becomes a threat); on g3 the
  pawn f5 interposes 1...f4; the queen's other c-file squares (Qc8/Qc6/Qc1) all fail to both corrections, since only
  c2 lets the queen guard d3 for Sc6 and mate on d3. Second layer still open (gate: single phase).
- His second change (bench steps 342-547): set 1...Rd5 2.Sc2#, 1...Rc5 2.Qf4# (queen c7), after 1.Qc2! Sc6# / Qd3#.
  Step 383 (1B6/2Q3p1/1P5N/1p2rp2/1N1k1P2/4pP2/1P2P3/1n4bK) is sound with the first change only. Guard table, bare frame:
  set R~ Sxf5 leaves e4, set Sc2 d3+e4, set Qf4 c3, threat Bxe5 e3 and needs an e5 protector, post Sc6 e3; Kf3 + Pd2 + Pe2
  cover them. The protector is the problem: Qf4 needs f4 free, so after the key only an e-file rook can protect e5,
  and it cooks (1.Rxe5; 1.Sxf5+ Rxf5 2.Re4#; 1.Sc2+ Kd5 2.Rxe5#). His pin of Re7 by bBh4 against Kd8 (Pd7 shielding
  Rd5+) stops those, but the pinner takes the rook with check: 1...Bxe7+ is an unprovided check (step 544 solves only
  by 1.e3+). A two-phase beam with the solver's cook count (scratch twophase2/3.py) bottomed out at three checking
  cooks (Sxf5+, Sc2+, e3+).

## His finished version (29 Oct 2026, bench step 581): bourd-rook-correction-changes-qc2
- 1B6/2Q1p3/1p5N/1p2rp2/1N1k4/4R3/5K2/b7, set R~ Sxf5#, Rd5 Sc2#, Rc5 Qf4#; 1.Qc2! (2.Bxe5#) Rd5 Sc6#, Rc5 Qd3#. The
  e5 protector is a rook BELOW on e3 (it also covers c3/d3/e4, the guard table's free squares); bPe7 closes the file
  upward and refutes 1.Rxe5 (e6!), bPb6 kills Qc5, bBa1 Sc2+. Gate PASS, 13 units.
- 1...Re4 2.Sxf5#/Rd3# is no flaw for him: the move keeps the random error and adds another, it corrects nothing
  (critique: 'random move with a second error', a note). Same for moves that do not defend the threat.

## Knight correction on his bench scheme (30 Oct 2026): bourd-knight-correction-bf7
- His kernel (bench mvu6ww43): bK d4, bS e5, wQ e8, wR a3 (+bPg4): threat Qxe5#, S~ Qe3# (Ra3 protects e3), Sd3! cuts
  Ra3's guard of e3, Sc4! guards e3 itself; both self-block. Two different correction reasons from five units.
- The guard rule again: the random mate needs d3 and c4 guarded, so the mate after each self-block must be given by the
  square's guard leaving it. A rook on c5 does both: Rd5# after Sc4 (leaves the c-file), Rc4# after Sd3 (leaves the
  5th rank) - one unit, two mates.
- 9 units: 6K1/4Q3/8/2RBn3/3k2p1/R7/8/5b2, 1.Bf7! (2.Qxe5#): the bishop unblocks c5-e5 (the rook protects e5), keeps
  d5/c4 from f7 and gives e4. Gate PASS; the tries 1.Rb5?/Rca5? (both corrections 2.Qe4#) fail only to the cook-stopper
  bBf1, so the second layer is still to be built. Found by specbeam.py (spec-bound post-key beam: named threat, random
  mate and corrections, solver cook count) then evolve CORR=e5 from the cooked 1.Bd5-f7 retraction.

## Self-blocks that free a guard (30 Oct 2026): claude-knight-selfblock-kh5
- His meaning of "both corrections are self-blocks" (bench mvu6ww43 steps 41-51: bK e4, bS f5, Qf7, Ra3, Ba6, Se2):
  the self-block makes a White guard of that square free to mate - 1...Se3 2.Bd3# (the bishop cuts Ra3's guard of e3),
  1...Sd4 2.Sg3# (Se2 leaves d4). Random S~ 2.Qf3# (Ra3 protects f3): Se3 cuts that protection, Sd4 guards f3.
- On his squares 1...Sh4 also guards f3 (a third correction). One file right it would be on i4: bK f4, bS g5, Rb3,
  Bb6, Sf2, queen on the g-file; Sf3! Be3#, Se4! Sh3#, S~ Qg3#.
- Post-key 6Q1/8/1B1pp3/5pnK/2N2k2/1R6/5N2/8: bPf5 blocks f5 and kills Qf6/Qg4 (fxg4); Sc4 guards e5 for the threat;
  Qg8 rather than Qg7 (Qe5/Qd4 duals); bPd6 stops Bc7+, bPe6 stops 1.Qd5 (both black cook-stoppers). Bishops checking
  f4 and bishops protecting g5 share a colour (e3-f4-g5 is one diagonal), so g5 needs a non-bishop protector.
- Key 1.Kh5! from g6 (opens the file, protects g5). Gate PASS, 11 units. Tries 1.Qd8?/Qh8? Sf3! (Be3 needs the queen
  on the g-file for g3), 1.Kh6? Sf7+! (a check). Alternatives: 1.h4! with Ph3 blocking Sh3 (set play S~ Qg3, Sf3 Be3;
  cooked by 1.Re3, a bBh1 stops it, 13 units); Bc5 masking Ra5-e5 (Ba7?/Bb6? d5!, but the diagram gives e5).
- Thematic tries for 1.Kh5! (E. Bourd: "tries that dont hit f3/e5"; the queen tries only take g3 away). From the guard
  table: Sh3#'s field shares every guard with the other mates except g4 (the queen covers it from the file), so 1...Se4
  alone refutes only if h3 is occupied or Sf2 bound; 1...Sf3 alone only if e3/c5/d4 is occupied or the bishop leaves
  a7-g1. No unit found that does either AND creates 2.Qxg5#. evolve CORR=g5 DEFS=Se4,Sf3 DEFTRIES=1 NOTRYFROM=g8
  (new option) from two seeds: nothing in 5 minutes. Bg7-d4 (opening the file) gives 1.Bf6?/Bh8?/Bf8? Sf3! but
  1.Be5+ dxe5 2.Qxg5# is built in (the route g7-d4 passes e5).
- Geometry with the knight on d2 (no e6 square): 8/4R3/8/5p1K/3B1k2/3R4/Q2n3P/8 (after the key): 2.Qxd2+; S~ (4) Qf2#;
  Se4! Be5# (cuts Re7's e-file guard of e4), Sf3! Be3# (cuts Rd3's guard of f3). One bishop, two guard-freeing
  interferences; a bishop on a7-g1 fails only to Se4, on a1-h8 only to Sf3, but a key Bd4 comes along one diagonal,
  so its tries are one-sided. Many queen cooks in the post-key position; no key yet.
- E. Bourd on the try pair (30 Oct 2026): "as long as the motivation might be something unified, ideally somehow the
  try has an error, which doesnt allow the mate in the solution. it could be just a random try, but if its just too
  random and unrelated, its worse." Tries by different units are allowed.
- What blocks it in these settings: every try must create the same threat as the key, so a try can only come from a
  unit that supplies what the diagram lacks. When that unit also serves both correction mates, its absence spoils both
  (double refutation); when a static unit replaces it, the try becomes a cook. In 1.Kh5! only the king creates the
  threat, and no king move occupies h3 or binds Sf2.
- Geometry of a clean pair: a bishop whose two diagonals each reach one interference square fails to the opposite
  correction (crossing d4: from c5/b6/a7 the tries Bb6/Ba7 reach only e3, Bd6 only e5), but c5/b6/a7 must lie on the
  threat line (knight g5 + queen on the 5th rank: 2.Qe5 becomes a second threat). Knight wheel (Sc2 opening Qa2's rank,
  Sd4 for Se6/Se2): after a self-block nearly every knight check mates, so the tries become cooks.
- Crossed rook mates (Re3 guarding e4 and f3: Se4 Rf3#, Sf3 Re4#) cannot work: the unit protecting one mating square
  covers it as a flight and makes the other mate a dual after the random moves.

## Bishop correction with two self-blocks (30 Oct 2026): claude-bishop-selfblock-corrections
- A bishop that moves along a diagonal still sees the squares behind it on that diagonal, so its random moves can still
  reach a self-block square on that line (and interpose there). Put both self-block squares on ONE diagonal, let the
  random moves run on the OTHER diagonal, and close the self-block diagonal behind the bishop with a black pawn BELOW the
  bishop (a pawn above it protects the bishop against the threat capture: bPg7 for Bf6, bPg4 for Bf3, bPb4 for Bc3 all
  failed that way). The far end must be the edge.
- Setting: bK e8, bB d6, bP c5; self-blocks e7, f8; random squares c7, e5, f4, g3, h2 (b8 taken by bSb8).
  1nK1k2r/8/1R1b2P1/2pN1R2/8/8/3N4/8, 1.Se4! (2.Sxd6#) B~ 2.Re6# (Rb6 through d6), 1...Be7! 2.Sc7# (Sd5 guarded e7),
  1...Bf8! 2.Sef6# (the knight cuts Rf5's guard of f8; the key adds this mate). Try 1.Sc4? Bf8! (no Sf6 from c4).
  bSb8 and bRh8 are black cook-stoppers (Rxd6, Rf7 / Sc7+, Se6). Gate: one-sided extension (no try for Be7).
- Found by hand (geometry) plus evolve CORR=d6 for the cook-stoppers; Rf5 rather than f1-f4 so Bf4 does not cut the
  file, a pawn g6 for f7 instead of a light bishop (Bf7 would be a second interference mate after Bf8).

## His simpler bishop scheme: the knight makes the threat and the random mate (30 Oct 2026): claude-bishop-correction-sf5
Core (his bench, sitting mvvfuofc): bKe6, bBd4, bPc3, bPg7, wSf5. Threat Sxd4; random moves along a7-g1 unguard g7
(Sxg7#); Be5 and Bf6 keep g7 and self-block. Sound: 5R2/4p1pb/2K1k3/3p3B/3b2P1/2pN2N1/8/8, 1.Sf5! - Be5 2.Sc5# (Sd3 was
the only e5 guard, and c5 is free because both corrections leave a7-g1), Bf6 2.Bf7# (Bh5 cuts Rf8 from f6), Bxf5 2.gxf5#.
How it was found: a queen or rook that can reach d6/e7 (both protected by Sf5) always mates in one there, so the e5 guard
is a knight and the f6 guard a rook cut on f7 by a light bishop. Kc6 covers d5/d6/d7 and bPe7 fills e7. No retraction gives a key
(the threat depends only on Kc6, Sd3 and Rf8), so the key is the knight arriving. From h6 only 1.Rf5 cooked. The single
black unit that refutes it is Bh7 (...Bxf5), whose ...Be4+ on Kc6 is fatal, so bPd5 blocks it. From g3 the key is not an escape.
Gate: FAIL. No thematic try: the tries 1.Rf5? and 1.Be8? are refuted by the cook-stopper. The second layer is still to do.
His bench, rotated (sitting mvvg7rz1, 30 Oct 2026): bKe3, bBd1, wSf2 (threat Sxd1, random Sxg4, Be2/Bf3). Rc6 masks Ba8's guard
of e4, so every rook move makes the threat. His rook tries were already thematic: 1.Rc7?/Rd6? cut Bb8-f4 (1...Bf3!) and 1.Rc5?
cuts the queen's b6-e3 line (1...Be2!). Sound fix of his step 310: BB6/8/1pR5/1Qb2R2/1n2P1p1/2P1k3/3p1N2/3b2K1, 1.Rxb6!
(Be2 2.Qxc5#). His bPd2 from step 301 replaces Sb1+Bc1, which frees Black's dark bishop for c5. Conflict: 1.Qc4 guards e4
through d4, and only a black unit that can reach d4 stops it, but such a unit also interposes on b6-c5-d4-e3, where the Be2
mates run. So Be2 refutes every rook try and the Bf3/Be2 split of the tries is lost.
