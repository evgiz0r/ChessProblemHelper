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
