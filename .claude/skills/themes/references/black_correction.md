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
