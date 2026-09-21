# Black correction (knight)

Reference: `claude-knight-correction`, b3N3/8/ppn1p3/4k3/3R2P1/4P3/7K/2Q5 #2 (6+6), session 26,
built in E. Bourd's order.

1.Qc4! (2.Re4#)  1...S~ 2.Qc7#  1...Sxd4! 2.Qxd4#.  Try 1.Qc2? (2.Qe4#) S~ 2.Qc7# but 1...Sxd4!

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
