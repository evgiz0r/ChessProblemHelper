# Self-pin by capture

Settings: bourd-selfpin-changed-mates-2 (3rN2b/7b/8/n1Q5/1R1Pk1P1/4P3/4K3/8: 1.Sc7? Sc4!, 1.Qh5!),
claude-two-rook-selfpin-v1 (8/7B/p6K/r4N2/1N1Pk3/2P4P/6PQ/5r2), bourd-two-rook-selfpin
(8/3Rp1K1/6B1/1r3N1R/2N1k2P/1p4B1/2b1P3/1n2Qrq1, repair Rd7->d8), bourd-queen-pin-selfpin
(q3r3/8/3B4/N1N4Q/p1PkPR1r/6p1/3Pp3/3nK2b).

The pinned unit can neither capture the mating piece nor interpose: both are exploitable. The set mates
usually come from the key piece (Se8: Sd6/Sf6; Qh5: Qe5/Qd5) and it switches them off by moving.
The reason the captures defend: the capture square on a line from the capturer through the threat piece
to the White king (they pin the queen), the same capture self-pinning against a rank rook.
Traps: the pinner on the rank with a White pawn on the pin square gives a discovered-check cook; every
White line piece near the king adds checks; a protector of the mating square mates along a parallel line
(thematic dual); two rooks reach every line, shield the White king with thematic blockers.
The a5 knight that refutes the cook AND the intended key: invert phases (the key becomes the try).

## Geometry of a direct self-pin (daily No. 8, 13 Oct 2026)
- The pin line must hold a White unit on the arrival square before the defence: an empty line from pinner to king
  is a check, and a Black unit already on it is pinned in the diagram. So a direct self-pin is a capture of a White
  unit standing on the pin line (Avner & Retter 2000: Bxd6 on Rd8's file, Bxf4 on Rh4's rank), or a king move.
- The capturer must not be able to move along the pin line: a knight is pinned dead on any line, a bishop only on a
  file or rank, a rook only on a diagonal. A Black bishop capturing on a diagonal pin line can still interpose or
  capture along it.
- The captured White unit must not be a battery front piece. White knights on c6 and e6 in front of Ba8 and Re8
  (Ke4, a Black Sd8 capturing either) make two loaded batteries: every evolve run gave checking keys, and the
  zugzwang post-key (B2nR3/8/Q1N1N3/8/4k3/3R2K1/2P5/B7: Sxe6 Se7#, Sxc6 Sg7#) was mate in two by thirty moves.
  Use immobile units (a pawn blocked in front, or a piece that cannot leave the line) as the captured blockers.
- Each capture must remove something the threat needs, and the two needs must differ: two knights that both guard
  d4 cannot make two captures defend against one threat that needs d4.
- A mate on the square the captured unit guarded is made by a line piece that already guards that square in the
  diagram, so the captured unit was never the only guard and the capture defends nothing. The mate after the
  capture must come from a move whose new guard did not exist before (a knight landing, a line opened by the move).
- The solver reports `Self-pin: <defence>` (Patterns) when the defender is pinned on arrival and, unpinned, could
  capture the mating unit or interpose; evolve takes `PATTERN=Self-pin NPAT=2` (DEFS empty).
- Result (daily No. 8): the capture checks the white king, which is the front piece of a royal battery; the pinned
  knight cannot interpose and its remaining control picks the king's square. B7/2N5/2Pp4/1P2p1B1/RK1nk2N/1PR5/2P5/1Q1n4,
  1.Rg3! (2.Rg4#) Sxc6+ 2.Ka3#, Sxc2+ 2.Ka5#; try 1.Qxd1? Sxc2+!. Made in three steps: freethreat with the exact
  thematic mates (`{"Nxc2+":"Kb4a5","Nxc6+":"Kb4a3"}`) after placing the king-square selectors by hand (bPd6 for c5,
  bSd1 for c3, wPb3/wPb5), then postsearch READY=1 for the flight guards, then keyfind.
