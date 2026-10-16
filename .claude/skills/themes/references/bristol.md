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
