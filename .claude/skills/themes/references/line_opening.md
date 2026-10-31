# Black line opening: the same black unit opens one white line twice, with different mates

Setting: claude-bishop-opens-d-file, 4N2K/5p2/2R2P1p/4k1p1/3bP3/5P2/4p3/2BQ4 (11 Oct 2026):
1.Rc7! (2.Re7#) Bc5 2.Qd5#, Be3 2.Qd6#. The closing counterpart is claude-knight-cuts-d-file-twice.

## What works
- The opened line is the mating piece's PATH (Qd1 through d4 to d5/d6), not a check line. Departure is the common
  error, and arrival chooses the mate: Bc5 guards d6 (2.Qd6? Bxd6); Be3 cuts Bc1-e3-f4 (2.Qd5? Kf4) while Qd6 covers f4
  by x-ray through the king.
- The blocker stands next to its own king, which protects it against the line piece behind it (1.Qxd4? Kxd4).
- Each defence's reason against the threat comes from its arrival: Bc5 guards e7 (threat Re7), Be3 opens f4.
- The key piece guards, before the key, the one square only the diagram needs guarded (every mate covers e6), and the key
  gives that flight (Rc6-c7).

## Rules (lessons.jsonl, 11 Oct)
- The departing unit can always return to the square it left, so a check along the opened line is interposed
  (a Ra5-Sd5 battery behind Bc5 fails to Bd4/Bd6-c5). Use a guard or path line, a double check, or an arrival that pins.
- The departing bishop guards its origin square from everywhere, so no mate on the vacated square ever works.
- The white line piece always attacks the blocker: protect the blocker at scheme time.

## Dead ends
- Ke6, Bd3 (unprotected) in front of Qd1: 1.Qxd3/1.Sxd3 cook it, and with only the bishop for Black, waiting moves work.
- A rook key from the h-file (Rh2/h3/h6-h7): out of play every time; h3 also allows f4+, h4 Bf4#, h5 Rxf5#.
- A clearance key along the guarding diagonal (Bf7-g8): the other-side retreats Bc4/Bb3/Ba2 do the same job, and any
  white blocker on c4 that guards d5 makes 1.f4+ Kxe4 2.Bd5# work.
- A lone black bishop against Q+R+B+S: plan Black's line-closing pawns with the scheme (e-file, c1-h6 diagonal squares,
  e6), not one per cook afterwards.

## Related: black unpinning on one square (bourd-bench-unpin-c3-bd3)
2N5/3p1K1p/Q7/3nkB2/rbPn3N/6P1/1B6/8, 1.Bd3! (2.Sf3#) Sc3 2.Qf6#, Bc3 2.Qd6#. Bb2 pins Sd4, both defenders interpose
on c3, each departure gives up the square the queen then mates on. My keys were idle or cooked; his: give Black a rook
(a4) and make the key close its line in advance (Bf5-d3 against Ra3).

## Closing counterpart, three closers and a masking key (31 Oct 2026): claude-line-closed-thrice-sd2
3R4/B7/2P5/1rp1kPK1/Rp2p3/1N2P3/B3b3/8, 1.Sd2! (2.Rd5#, Ba2 protects d5). 1...Bc4 2.Sxc4#, 1...c4 2.Bd4#, 1...b3 2.Rxe4#.
The closed line is the protection of the threat's mating square. Black cutting it lets the king take the checker, and the
mates after the cuts need nothing on d5, which was the trap of the guard-line versions. In those, every mate had to
re-cover the cut square, and no knight check on e5 covers d5. Pawn closers (single steps) have no random moves. Their
departure opens the mating lines: c5 opens a7-d4 and b4 opens the 4th rank. Model: Ahues, Die Schwalbe 1998, 3rd prize
(three units close Qa8's line on c6). The key is a knight that masks the line on a closing square (b3). Its departure
frees the square for a closer and gives it two jobs, c4 and e4. Each wrong landing keeps one job, and those are the pure
tries: 1.Sxc5? Bc4!, 1.Sa5? b3!. Dead ends on the way: guard-line cores (Rh6, Ra6 with d7/e7 pawns) where the far cut had
no error of its own; 1.Bb1-a2 from the corner (sound, but idle and out of play); a third knight or rook as the mask.
