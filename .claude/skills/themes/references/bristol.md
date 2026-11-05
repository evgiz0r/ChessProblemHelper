# Bristol clearance

Definition (E. Bourd): a line piece moves along a line; another piece follows on the same line in the same direction,
passing the vacated square and stopping short (`chesscomp.analysis.bristol`, reported as "Bristol" in Patterns).
Extended by tries in which the line piece stops on other squares, or leaves the line, each failing to a thematic defence.

Settings in the kit:
- bourd-bristol-prototype (his): 1Q6/R1Bpb3/2p5/6p1/1p1P4/1k6/N7/2K2B2, 1.Bh2! (2.Qg3#) Bd6 2.Qg8#, d6 2.Qxb4#;
  tries 1.Bd8? Bd6!, 1.Bb6? d6!, 1.Bd6? c5!. The defences close the cleared line (Bd6) or block d6.
- claude-bristol-corner: Q1K5/1B6/8/8/5p1p/R1n5/4NN1k/8, 1.Bh1! (2.Qg2#): see corner_key.md.
- claude-daily11-bristol-rook-files (daily No. 11): 4N3/4N3/Bn6/P1k5/6P1/2P3Pp/6RQ/6K1, 1.Rd2! (2.Qf2#) Sc4 2.Rd5#,
  Sd5 2.Rxd5#; 1.Rb2? Sd5! (1...Sc4 2.Rb5#). The rook's file selects the mates.

What worked:
- Box the following piece first, so that the line is its only way to the mate: Kg1 closes g1-c5, bPh3 the h-file,
  Pg3 (held by Pg4) h2-b8. A free queen gives a dozen queen keys.
- Give the clearing piece work where it stops: stops beyond the mating square differ by their file (or diagonal), from
  which the piece mates after a defence. The defences decide which stops still mate: tries with their own refutations.
- `BRISTOL=1 KEY=<uci>` in `chesscomp.compose.evolve` scores the Bristol threat and the tries by the key piece.

Dead ends:
- A first-rank line puts the clearing piece on the edge: out-of-play key (fatal in the gate) when the black king is
  three or more squares away and the piece guards nothing near it.
- Interference tries by a rook on a rank need diagonal lines through the stops; a rook on a file takes a file pin over.

## Tries as stops on the line beyond the mating square (3 Nov 2026, attempts, not finished)
Aim: the 2x2 shape with a new error type: the clearing piece stops on one of three squares beyond the follower's
mating square M; each wrong stop shuts a White line that one thematic mate needs (unified interference tries).
Traps met, in order (each is structural, not a placement problem):
- M next to the king on the line: the clearing piece can stop on M and mate itself (1.Be4# v Kf3), and with the king
  next to two squares of a diagonal the follower has two mating squares (Qe4/Qf5 v Kf4). Mate from a distance along a
  line crossing the Bristol line, as in his prototype (2.Qg3 along the 3rd rank).
- With a distant check, a defender that interposes on the CHECK LINE kills the threat itself (Qc3+ f3 / Bd3 v Kh3): the
  thematic defences must close the follower's PATH (before M) and the defending units must be unable to reach the check
  line or M once the follower has arrived. His prototype: bPd7 and bBe7 reach d6 but not the 3rd rank.
- Black knights next to the king fail that test (they interpose or take M), and a knight blocking a side line usually
  has two defensive moves (Sd4 and Sg3), so a try would have two refutations.
- Side-mate rooks are threats of their own in the post-key unless a black unit shuts their line; the thematic defence
  is then that unit's departure (line opening), which is the dual avoidance, but it has to be the unit's only move that
  stops the threat. Pawns (one move) and bishops on long lines fit; knights rarely.
- Search: evolve KEY/BRISTOL/TRIES manages 60-1300 diagrams in 280 s here and finds sound one-phase Bristols without
  tries; postsearch on the post-key reaches 60-80k positions but needs a threat that already mates in the core.
- (second attempt, 3 Nov) King orthogonally next to M on a diagonal Bristol (Ke3, M = e4 on b1-h7): the bishop on M
  gives no check, and the other line square next to the king (d3) can be guarded by a black knight (f4), which then has
  a single defence (Sd3, opening the f-file for Rf3#); a black rook g5 with Re5 opens the g-file for Rg3#; the bishop's
  off-line squares can be shut (Sb3, Kd1) so that e4 may be protected statically without off-line keys. But the bishop
  beyond M protects the square behind M (d3): 1...Sd3 is answered by 2.Qxd3# as well, and f2 has no guard without new
  checks (Be1 gives Bd2+/Bf2+, a d1 knight checks e3). The distant-check geometry of his prototype keeps the line's
  squares out of the king's field; the next attempt should start from it: pawn defenders interposing on the path (one
  move each, never on the check line), whose departures or arrivals select the mates.
- (third attempt, 3 Nov) Distant check with pawn defenders on the path (Kd8, Qa1-d4; Kc5, Qa1-e5): pawns interposing on
  the path stand far from the king and cannot select between side mates; the selection has to come from what the
  defenders' departures or arrivals do near the king (his prototype: the d7 pawn's double step to d5, the bishop d6
  guarding b4). Option 2 (tries leaving the line onto the follower's other lines, his prototype's concept): the two
  side mates must use two DIFFERENT follower lines, one per thematic defence. With Qa1/Kc5 both natural mates (Qa3,
  Qa5) are on the a-file and the 1st-rank mates (Qc1, Qg1) are blocked by the d4/c3 interpositions; with Qa1/Ke3 both
  defences on d4 (d5-d4, Sd4) leave only 1st-rank mates. postsearch (EMPTY on the side lines) finds post-keys whose
  second mate is the queen capturing the interposer on the path (Qxd4#, Qxc3#), a recapture mate and no side line.
- (fourth attempt, 3 Nov, structural) The Kh3 corner version (Qh8, Bg7, bBe7/bPf7 Grimshaw on f6, 1.Ba1! 2.Qc3#, f6
  2.Qxh4#, Bf6 2.Qc8#, tries 1.Bh6? f6!, 1.Bf8? Bf6!) is his prototype's mechanism in another corner: same Grimshaw,
  same black correction (random Be7 unguards the capture square), same leaving tries. Nothing added.
- The prototype's Grimshaw fixes the geometry: the pawn's next step (Y, below X) must lie on a line to the king, and the
  bishop's line through X must end next to the king. Of 494 placements of queen, line piece, X, M and king that meet
  both (scratch geom.py, pure geometry), none has two stops beyond M whose other lines reach the king's field; at most
  one does, the stop next to M. Stop tries cannot be added to this Grimshaw. They need another pair of defences.
- A queen as the line piece (the queen's stop selecting its mates) fails: from any stop beyond M the queen returns to
  M and gives the follower's check herself, so a closure of the follower's path is no defence.

## His short-Bristol schemes (bench, 5 Nov 2026)
He put three cores on the bench after rejecting the corner Grimshaw-Bristol as too close to his prototype. All three are
short Bristols: the queen mates NEXT to the king, protected by the line piece from its stop ("the bristols dont have to
be long"); the stop chooses the protected square, and two phases (two stops, or two line pieces) carry changed play.
1. `7K/8/8/3k4/8/4B3/5Q2/8` Be3/Qf2 v Kd5: "bishop moving along the diagonal and mates are on Qc5/Qd4".
2. `7K/8/8/8/4k3/3RB3/3Q4/8` Rd3+Be3/Qd2 v Ke4: "both the bishop and the rook perform 2 phases ... changed mates and more".
3. `K7/8/8/3k4/8/4R3/4Q3/8` Re3/Qe2 v Kd5: "rook-queen bristol with maybe 2 phases with some changed play".
What the first attempts showed (scratch climb.py: python-chess hill-climb, key + tries + required threats):
- A rook next to the king's line gives a check-cook: 1.Rd4+ (scheme 2), 1.Re5+ (scheme 3) mate or force mate (1.Rd4+ Rxd4
  2.Qxd4#). Cure: Black guards the square twice with pawns (bPc5+bPe5 on d4; bPd6+bPf6 on e5), which also kills the
  queen mate on that square, so the threat moves to the next square (Qd3# after 1.Rd5, Qe4# after 1.Re6).
- A black guard of d4 down the d-file is cut by every rook stop d5-d8, not only the short one; a guard on the bishop's own
  diagonal (bBh6 v Be3) is simply captured (1.Bxh6).
- Every move of a line piece opens the queen's line, so each wrong stop (and the sideways moves) needs its own reason to
  fail; the stops differ by what the line piece guards from the stop (rank 5 from d5, rank 6 from e6) and by which queen
  squares it protects: from e7/e8 the rook also protects e6, so the long phase gains Qe6 (scheme 3).
- Scheme 1: Ra6 makes 1.Bb6 cut rank 6 (c6), so after 1.Bb6 only Qc5 threatens while 1.Bc5 keeps Qd4; a black pawn e4,
  blocked by Be3 in the diagram, gets ...e3 (closing f2-d4) only after the key: a defence common to both phases.
- Sound sketch of scheme 3 (gate FAIL, one-sided): 8/2nK1R2/3p1p2/1npk4/8/1Np1R3/4Qp2/8, 1.Re6! (2.Qe4#) Sxe6 2.Qxe6#,
  Sd4 2.Rxd6#, f5 2.Rxf5#; 1.Re8? (Sxe8 2.Qe6#, Se6 2.Qxe6#) and 1.Ree7? both Sd4!: only from e6 does the rook take d6.
