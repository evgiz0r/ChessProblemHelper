# Dead ends, with the reason (do not repeat; do cite when relevant)

- Same-piece changed mates by blind enumeration: four skeleton families, ~5M positions, no sound hit
  with a quiet key. Enumeration finds placements, never mechanisms.
- King-key with interference tries: ~150k positions over six geometries, no two king tries whose
  refutation exploits the line; with little Black material every try dies to a king flight.
- Self-pinning tries by rigid search: 102k positions (Q + 2 knights vs R + B), no unique king key; the
  pinners are strong defenders.
- Providing a diagram flight afterwards (d5 in 5NR1/8/8/5nQ1/3Pk3/3R1p2/3K4/4N3): 18 single units give
  a set mate, no pair keeps the change, the key and dual-free play. Box the king first instead.
- Knight promotion with the king on the promotion file (queen/rook check too early): the hole the knight
  mate fills is a flight the quiet key cannot answer. Failed for e4 and h4 kings.
- Bishop promotion with a pinned dark bishop and knight mates: the bishop's self-blocks on d6/f6 give
  duals (Sxd6#/Sf6#); with a pinned knight, self-blocks on the bishop's mating squares c6/g6 give duals
  and non-interfering squares give more. Clean two-mate settings needed 16+ units.
- Stalemate-motivated underpromotion keys stay thin: Black must be immobile, so nobody defends. ~150k
  one/two-unit additions around three kernels found no second variation.
- A bishop on the pin diagonal of the promotion square captures the promoted piece; a knight pinned on
  f7 reaches h6 and blocks the mating file; on g6 it cannot.
- Rotating and shifting a scheme whose captures stop nothing: 45 minutes, six transformations, no key.
- Black line opening with the check along the opened line (battery behind the defender): the defender steps back to its
  origin square and interposes. And a lone unprotected blocker in front of the queen: 1.Qx(blocker). See themes/line_opening.md.
- Flight-giving key by an unprotected bishop next to the king (Bd4 v Ke4, black pawns d5/e6 cutting the long diagonal from
  either side, daily No. 19): no knight check on e4 also guards d4, so every knight threat fails to Kxd4. Five evolve jobs
  (12 min each) on that core returned a zugzwang with one mate.
- Second layer for claude-two-flight-knight-sacrifice by moving the refuting bishop to the other side of d3 (g6 -> b1): it
  then guards d3 (no 2.Qd3# after Kxe4) and reaches c4 (1...Ba2). The g6 bishop's three jobs cannot be split.
