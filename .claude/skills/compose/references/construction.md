# Construction rules, with the FEN that taught each

## The box
- Build around a king WITHOUT escapes. With a flight every phase must answer it; the same enumeration
  that needed 10 units with a flight gave 6-unit hits without (7b/8/3K4/8/3Pk3/2Q5/8/5R2).
- Every White line piece near the king's field adds checks and cooks; protect a mating square with a
  unit that has no line to the king, and never with one that can capture there with mate
  (8/7B/p6K/r4N2/1N1Pk3/2P4P/6PQ/5r2: the g2 pawn duals with gxf3).
- When the king is fully boxed, every protected adjacent check is a mate in one: a first-rank rook
  protecting h1 mates on h1; a bishop covering g6 through f5 also mates from e2; Rd4#/Re3# with rooks
  protected by a bishop and a knight (3R4/4P1N1/4bB2/8/4k3/R7/6N1/K7).
- Two free Black rooks reach every rank and file, so no White king square is check-proof by distance:
  shield it with thematic blockers (8/7B/p6K/r4N2/1N1Pk3/2P4P/6PQ/5r2).
- A pinner on the rank + a White pawn on the pin square + a queen nearby = a discovered-check cook
  (1.d5+ in 3rN2b/1p5b/8/2Q5/1R1Pk1P1/4P3/4K3/8). Give Black the blocker before anything else.

## Reasons a capture (or any move) defends - check at scheme time
1. It pins the threat piece against the White king (Rxe4/Qxe4 pin Qe2 in
   q3r3/8/3B4/N1N4Q/p1PkPR1r/6p1/3Pp3/3nK2b). The White king is a construction resource: behind the
   threat piece on a line it turns captures on that line into pins.
2. It removes a guard the threat mate needs.
3. It opens a Black line to the threat's mate square.
4. It closes a White line.
5. It guards the mate square itself.
Only a pawn opens a White line by interposing without being able to close it again; a knight or rook
that interposes can step back (Q1K5/1B6/8/8/5p1p/R1n5/4NN1k/8: f4-f3 opens b8-h2).

## Reasons for a key square
- Bristol: the line piece vacates every square the queen will pass AND keeps protecting the mate square
  from the end of the line; 1.Ba6? clears too but Qg2 hangs, 1...Kg1! (kernel Q7/KB6/6N1/8/8/8/7k/8).
- Underpromotion: the other promotions stalemate (queen pins on file/diagonal, bishop or rook pins on
  one of them) or check too early or have no mate (8/4P3/4bB2/6K1/1N2k3/8/4P1N1/8 and its siblings).
- Two keys with the same threat: give Black a capture on the unwanted square, the cook becomes a try.

## Changed mates
1. Choose squares and the Black EFFECT that creates several mates at once (self-block usually; a self-pin
   by capture: the pinned unit can neither capture the mating piece nor interpose).
2. Choose the DIFFERENTIATION: which mates each phase allows. Selectors seen: Black pawns guarding the
   mating squares, each first move removing one guard; the queen's post holding one pair of squares per
   phase; the key piece giving the set mates itself and switching them off by moving (Se8-c7, Qh5-e2);
   the key piece that moved just giving the other mate itself (Qg5-f6).
3. Only then the threat that the thematic defences parry, and cleaning.
- Two units capturing the same White unit get different mates when the capture square lies on two
  battery lines at once: the departing unit opens one, the arriving unit self-blocks the other
  (KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n). With batteries mating, the queen's post selects which
  departure mates.
- A set+solution diagram must not be a complete block or any waiting move cooks it.
- Set play is content: a unit may exist only to answer one Black move in the set.

## Dual avoidance
Motivations in rising order of unity: a sibling mate refuted by a unit that never moved (incidental);
the king escaping (weak); the defender itself keeping hold of the line or capturing the mating square;
interference by the defence (line opened/closed). A dual in a thematic variation is unacceptable.
A protector of a mating square along a line can mate along a parallel line for the same pin reason
(Rd7 in 8/3Rp1K1/6B1/1r3N1R/2N1k2P/1p4B1/2b1P3/1n2Qrq1); move it back so its second line is closed (d8).

## Economy and necessity
- Necessity is judged on content in every phase: a unit that only plays a try carrying a change, or only
  answers one set move, is thematic, not a cook-stopper.
- Test removals in pairs: two units each removable alone can be jointly necessary.
- Reuse general ideas and the search process, not structures; the same solution appears in other
  directions - rotate, reflect, shift, respect the constraints of the position.
