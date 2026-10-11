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
