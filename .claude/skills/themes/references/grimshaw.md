# Grimshaw

A black rook and bishop whose lines cross on one square X. Each moves to X to defend, and each arrival cuts
the other piece's line beyond X: two defences on one square, two mates, each mate needing exactly the guard
the other piece lost. Claim it only when the solver's report prints `Grimshaw: ../.. on X`.

Reference: daily No. 6 (11 Oct 2026), 3Q1bb1/2N3r1/1N3Rpp/1pP1k3/3p4/3P4/5K2/8 #2 (7+8).
1.Rf3! (2.Qf6#) Re7 2.Qd6#, Be7 2.Sd7#, Rf7 2.Qd5#. Try 1.Qxf8? (2.Qd6#) Re7!

## The geometry (learned the hard way, 11 Oct 2026)
1. **X lies on the threat piece's PATH, not on the check line.** If the threat checks along a line through X,
   the rook and bishop simply interpose after the check and the threat is not a mate in one: there is no
   defence to make. The threat piece must travel through X to a square next to the king (Delobel:
   Qh3-d7 through e6 against Kc6; No. 6: Qd8-f6 through e7 against Ke5). The defence is a pre-emptive block.
2. **The square beyond X.** A rook that can reach X can go one square further while X is still empty. Check
   every square of its line before and beyond X: none may guard the threat square, or that move needs its
   own mate. In No. 6 the rank-7 rook reaches f7, which guards f6. Cure that worked: a black bishop g8 whose
   d5 guard 1...Rf7 closes (2.Qd5#), so the extra move became a third variation (it also pins the key rook).
   Confining the rook with its own pawn (g6) took away Rg6, which also guarded f6.
3. **A move that leaves both lines.** A bishop that steps off its diagonal to a square on the rook's line
   (Bf8-g7 with the rook on h7) both unguards and interferes: it allows both thematic mates (a dual). Put the
   rook on that square instead (Rg7), so the bishop cannot go there.
4. **The two mates.** Each mate uses one cut square near the king: f8-d6 cut gives Qd6# (d6 protected by a
   pawn c5); h7/g7-d7 cut gives Sd7#. The arriving unit keeps the other square (Re7 still guards d7,
   Be7 still guards d6), so dual avoidance is unified for free.

## Order that worked (20 minutes after the geometry was right)
- Threat first: a mate next to the king whose path crosses X. Then the post-key position with
  `chesscomp.compose.keyfind.post_spec(fen)` (the threats, each defence with its mates; a few lines of Python
  printing it in SAN is enough), one unit per solve: block extra threats with black units
  (Qd4 -> block the d-file; Qg5 -> bPh6; Sc4 -> a black guard of c4).
- `compose.postsearch` with READY=1 found the g8-bishop cure for the f7 square in five minutes.
- Key: `keyfind` gave none (the post-key position already mated by checks: Bb8+, Sd7+). What worked: give the
  key piece ONE retreat square. The rook on f6 (the threat square) with the white king on f2 can only go to
  f3 (f4 is next to the king, f5 checks, f7/f8 are captures). Then cure the checking cooks one by one.
- Cooks met and their causes: a white bishop on the g8 bishop's diagonal (b3) gave 1.Bxg8 and 1.Bf7; a pawn
  e4 that protects d5 made 2.Qd5 a standing threat whenever g8 was blocked; 1.Qb8+ along b8-e5 (Rc7 is then
  pinned, so 2.Sd7# still works): a white knight on c7 blocks that diagonal and covers e6 and d5 as well.

## Dead ends
- Bare or lightly seeded `compose.evolve` (DEFS=Re7,Be7 / Rg6,Bg6): checking keys only, as for every theme so far.
- The threat 2.Qe8# on the e-file through e7: the defenders interpose after the check (rule 1).
- A bishop as the threat piece (2.Bd8-f6#) so the queen cannot cook along rank 8: after 1...Re7 the rook
  simply takes the mating bishop on c7.
- The c3 Grimshaw of 8 Oct (claude-grimshaw-c3-qc1): sound only with an edge queen key that does nothing.

## Archive models (read, never copy)
- B. Delobel, Problemesis 2006 (psis-7ba72c1d6b), 6+7: 1.Re7! (2.Qd7#) Re6 2.Rc3#, Be6 2.Rxd6#.
- R. Ganapathi, Problemesis 2003 (psis-15bf4d17ff): white correction tries with a Grimshaw on e6.
- H. Selb, Die Schwalbe 1953, 1st Prize (psis-eabdb0206f): Grimshaws in try and key with changed mates.
