# White correction

Definition (blog/themes.json): the key piece's random move fails to one defence; its corrections fix that but
fail to another; the key is the correction with no negative effect. The mirror of a black correction; the one
in our kit by E. Bourd is in `black_correction.md` (1.Re7!, rook corrections Re5?/Ree3?).

## Reading: Loustau, Phénix 1999, 2nd Prize (psis-22fa9079c1, daily No. 10 study)
4R3/3N4/1BNb1R1r/1K1k1p2/1p4q1/3P4/4r3/6Q1 #2 (8+7). 1.B~ (d8, c7, a7, a5)? Qxg1!; 1.Bc5? Bc7!; 1.Bd4? Bc5!
(1...Bc7 2.Sxb4#); 1.Be3! (2.Sb6#) Bc7 2.Se7#, Bc5 2.Re5#, Qd4 2.Qg8#, Qc4+ 2.dxc4#.
- Threat by clearance: every bishop move empties b6 for 2.Sb6#.
- Random error: leaving the g1-a7 diagonal lets 1...Qxg1 stand on it and guard b6.
- Corrections stay on the diagonal between g1 and b6 and block it; each arrival spoils a mate: c5 takes the mating
  square of 2.Qc5# (after 1...Bc7, which guards b6), d4 cuts the white queen's g1-c5 line (after 1...Bc5).
  e3 still blocks and spoils nothing; the bishop defences get new mates there (changed against both tries).
- The error table is the problem: one line (g1-b6) that the bishop must block, one White line (g1-c5) and one
  mating square (c5) on it that a blocking square can spoil.

## Rules (daily No. 10, 15 Oct 2026)
- Write the error table before searching: for each arrival square, the defence it stops and the mate it spoils.
- A black interposition on the vacated line (Rd2, Rg2) gives the random refutation at once, and a square that closes
  the interposer's line gives the first correction (1.Be2!, 1.Sg3!), but neither carries an error, so no second
  correction follows. The closing square must also lie on a second White line or a mating square.
- A knight orthogonally next to the black king never checks by moving, so it can mask a queen line next to the
  king; but its landing squares give knight checks (second threats, cooks). Prefer a bishop or rook as the key piece.
- Search: `WCORR=<square> python -m chesscomp.compose.evolve` (score in `chesscomp/compose/white_correction.py`;
  `python -m chesscomp.compose.white_correction FEN SQ` scores one position). Seed it with the error table placed,
  not a bare core; it found one correction three times and never a second error by itself.

## Near-misses (daily No. 10)
- 8/2K2R2/8/4k3/4PN1r/2RB4/2P4r/3Q4: 1.B~? Rd2!, 1.Be2!; diagram flight d4, no defence after the key.
- 8/6rb/1N1P4/4P3/1P1kNP2/8/1K2PP2/7Q: 1.Sf6?/Sc3?/Sd2? Rg2!, 1.Sg3!; cooked by 1.Sg5 and 1.Sc5 (knight checks).
