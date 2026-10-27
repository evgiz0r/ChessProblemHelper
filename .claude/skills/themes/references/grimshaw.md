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

## Changed mates on a Grimshaw (15 Oct 2026, unfinished)
The basic scheme first (postsearch READY=1 + keyfind): claude-grimshaw-e6-scheme, 2N1r1b1/8/3p4/1Bk5/2P5/K6n/5n2/1RQR4,
1.Qh6! (2.Qxd6#) Re6 2.Rd5#, Be6 2.Qe3#. Mates by interposition cuts: the cut piece can no longer interpose (Bd4, Rf3) or
guard the landing square (e3, d5).
- Queen posts on the threat line beyond X choose the pair: bK c5, X e6, threat Qd6#: f6 (Qc3#/Qf2#), g6 (Qc2#/Qg1#),
  h6 (Qc1#/Qe3#), six different mates. The diagram square is the problem: only g7/h7 reach two posts; g7 reaches the
  guarded d4 (1.Qd4#, 1.Qc3+ Bc4 2.Qxc4#), h7 is attacked by Bg8. Look for the start square before the posts.
- Leave d4 unguarded: 1.Qf6! (Qc3# covers d4 itself), tries 1.Qg6?/1.Qh6? Re6!, Be6 mated three ways. Still open: the
  diagram checks 1.Qc3+ Bc4 2.Qxc4#, 1.Qg1+ Re3 2.Qxe3# (a check whose interposition is captured with mate).
- E. Bourd's solution (bench, 15 Oct): bourd-grimshaw-d3-changed-set, B3K3/3N4/6pN/6p1/5k2/Qp2b2R/4Pr2/1b1r4, our scheme turned
  180 degrees; the queen starts ON post a3 with the threat line masked by bPb3, 1.Qxb3! opens it: set Rd3 Qf8#, Bd3 Qd6#;
  solution Rd3 Qf7#, Bd3 Qb8#. Masked start instead of a start square off the line. His word: not the best key (capture).
- Next to try: Velimirovic's own mechanism with a real Grimshaw (both units cut a White guard of the threat square on X,
  e.g. wRh6 guarding d6 through e6), so the queen's posts are free of the line; `chesscomp.compose.trychange` with KP=Q.

## Tries reaching both Grimshaw moves (daily No. 21, 27 Oct 2026)
claude-grimshaw-d6-unmasked-file-sf3, 1b1RQ3/8/7r/2p1p1B1/3Nk3/4N3/2K2nP1/8 (7+6): the knight d4 masks Rd8's guard of
d3-d5; every knight move threatens a knight check; Rd6/Bd6 cut the d-file. Rd6 cuts Bb8 from e5 (2.Qxe5#, protected only
by the knight on f3 or c6), Bd6 cuts Rh6 from c6 (2.Qc6#, d4 held by any knight square). Random 1.Sb3?/1.Se2? Rd6!, the
correction 1.Se6? (shuts the rook out of d6) Rxe6!, 1.Bxh6? Bd6! (Dombrovskis effect), 1.Sf3!.
- Write each thematic mate's needs from the key piece first. A try refuted by one Grimshaw move alone needs a mate whose
  needs the other mate does not share. No. 6's frame fails this: Sd7 blocks the queen's file, so 2.Qd6#'s guards are a
  subset of 2.Sd7#'s and no landing fails to Re7 alone.
- A Grimshaw with set mates changed by queen posts (threat through X, interposition cuts) is E. Bourd's own family: a
  scratch enumeration found only his shape (bench 15 Oct; Problemesis 2004, Zagoruiko 4x2).
- The threat decides which landing can be a try: with a knight-check threat, a landing with no check (c6 here) is no try.
- evolve `DEFTRIES=1|2 PATTERN=Grimshaw DEFS=...` scores the try per Grimshaw move (2: by the key piece). unmask_search with
  WANT and TRIES fixed found the sound post-keys of this frame in 5 minutes; EMPTY keeps a mating square free.

- Mirror interference tries (after E. Bourd's verdict on No. 21: "need some unified concept between the tries"):
  1b1R4/8/1r5p/R3p2B/pPPNk1P1/8/4P1NB/7K, 1.Sb5? Rd6!, 1.Sf5? Bd6!, 1.Sf3!. Each try blocks the line of one Grimshaw mate
  (a5-e5 rook, h5-g6 bishop checking via f5). For a pure interference try the other mate's guards must not depend on the
  try piece (e5 protected by Bh2, not only by the key knight). A queen on the 5th rank also mates on d5 (Rd8 protects it).

- Bare or lightly seeded `compose.evolve` (DEFS=Re7,Be7 / Rg6,Bg6): checking keys only, as for every theme so far.
- The threat 2.Qe8# on the e-file through e7: the defenders interpose after the check (rule 1).
- A bishop as the threat piece (2.Bd8-f6#) so the queen cannot cook along rank 8: after 1...Re7 the rook
  simply takes the mating bishop on c7.
- The c3 Grimshaw of 8 Oct (claude-grimshaw-c3-qc1): sound only with an edge queen key that does nothing.
- The white knight standing on the crossing (No. 6's frame, Se7 vacating e7): no try fails to Re7 alone (see above).
- A masked battery (Ra4 behind Bc4 behind the knight d4): every bishop move is a discovered mate, ten threats.

## Archive models (read, never copy)
- B. Delobel, Problemesis 2006 (psis-7ba72c1d6b), 6+7: 1.Re7! (2.Qd7#) Re6 2.Rc3#, Be6 2.Rxd6#.
- R. Ganapathi, Problemesis 2003 (psis-15bf4d17ff): white correction tries with a Grimshaw on e6.
- H. Selb, Die Schwalbe 1953, 1st Prize (psis-eabdb0206f): Grimshaws in try and key with changed mates.
