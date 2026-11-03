# Schiffmann defence

The defence pins the moved unit against its own king, and the threat would unpin it: the threatening move lands
on the pin line between the White pinner and the defender, after which the defender parries (interposes on the
check line, takes the checker). The solver reports `Schiffmann: <defence>` (chesscomp.motives.detect_schiffmann);
evolve takes `PATTERN=Schiffmann NPAT=2`.

## Published settings read (Problemesis)
- Aliovsadzade, Problemesis 2005 (psis-248d80a8fd), 4B1b1/7R/1pp2nRr/1pkP3Q/1p1NPBp1/1P3N2/2K1P3/8: 1.Be3! (rear of
  the Be3-Sd4 battery arrives, gives d6) 2.Sf5# (the front lands on Qh5's rank, covers d6); Sxd5 2.Sxc6#, cxd5
  2.Sxb5#, set Sxd5 Bd6#, cxd5 Rc7#. Both mates are discharges of the same battery. His Rh6 attacks the pinner Qh5,
  so every discovered check from the pawn d5 is answered by Rxh5; black pawns box the king (b4, b5, b6, c6).
- Kovacevic & Subotic, The Problemist 2000, 4th Prize (psis-3f6a82c74a): three Schiffmann captures on e5 (Sxe5, Qxe5,
  Bxe5) on Rh5's rank, threat Bf5 (half-battery front); reciprocal change 1.Sf5? / 1.Sc8!.
- Dyachuk & Melnichenko & Kopyl, The Problemist 2003 (psis-c4883e7793): Rxd4 Schiffmann with Dombrovskis and Rudenko.
- Robert 2004-05 (psis-dbc3c27642): Qxd5, Sxd5 on Ba8's diagonal, Pseudo Le Grand.

## Geometry (2 Nov 2026)
- The threat is always a battery discharge: from the pin line the landing unit cannot check past the White unit next
  to the king, so the check comes from the rear. A pawn defender can parry only a check line it can step onto (d4-d3
  against a b1-e4 battery); an e-file battery is parried by knights (Se2), bishops and queens (Be3, Qe3) only.
- The White unit next to the king is the front piece of a second battery (pinner -> unit -> king). It must be
  immobile (blocked pawn) or its discovered checks must be answered: a black unit attacking the pinner (Aliovsadzade's
  Rh6; our bSb6 v Ra4: dxe5+/d5+ Sxa4).
- Uniqueness of the threat among the front's other discharges is the hard constraint, and it decides the key. A flight
  that only the landing square covers works (d5 for Sc2-b4; d6 for Sd4-f5): the key gives it, so the diagram guards it
  and the key piece is the guard (rear arrival from a square on the flight's line: Ba2-b1, Bf4-e3). With a blocked pawn
  on that square there is no flight, and only a black line through the landing square remains (a black rook on the
  b-file aiming at Bb1: costs three rook defences, Rb3, Rb2, Rxb1, none with a mate).
- A shield on the landing square (a White unit the key removes) blocks the threat but leaves the other discharges
  loaded: with the flight guarded they mate in one. A shield on the other pin square keeps a mate in one.
- Dual avoidance that worked: each mate needs its own defence's departure. 1...Sxd4 (from c6) unguards e5 -> 2.Qxe5#
  (Pf4 protects e5); 1...exd4 opens Qb8-e5-f4 -> 2.Se3# (the knight cuts Bc1's guard of f4 in the threat; after the
  pawn leaves, the queen protects f4). Each sibling mate fails to the other defender (Sc6 takes e5, Pe5 blocks b8-f4).

## Result: claude-schiffmann-bb1 (not recorded: one-sided)
1Q6/8/1nn5/4pP2/R2PkPP1/2P5/B1N1P3/2B4K, 1.Bb1! (2.Sb4#) Sxd4 2.Qxe5#, exd4 2.Se3#, Kd5 2.Se3#; try 1.Sb4? (2.Bb1#,
threat reversal) exd4! - the knight already on b4 shields the pin, so the capture is no self-pin and ...d3 parries.
Also 1.Qd6? exd4!. No try fails to Sxd4 alone, and none can: 2.Qxe5# needs only the knight's departure, not the pin or
the battery, and every move that spoils it also spoils 2.Se3# (both use b8-e5). For the 2x2 shape both Schiffmann mates
must depend on the post-key battery or pin (two discharges, as in Aliovsadzade). The gate passed it until 2 Nov 2026
(critique fix: the one-sided check now runs with interference tries, and a flight's mate no longer hides a sibling).
Path: postsearch with the core fixed (threat Nc2b4, EMPTY for the pin squares) found the departure mates; the
b6 knight came from reading Aliovsadzade's Rh6; trim removed bPd7 (the b6 knight also interposes on d5 against Qb7+).

## His three-defence version: bourd-schiffmann-three-bc3 (3 Nov 2026, draft: single phase)
b1B4b/2pr1p2/Q1p2n1R/R2Pkp2/1BPN1p2/1K3P2/2P1N3/8, 1.Bc3! (2.Sb5#) Rxd5 2.Sxf5#, Sxd5 2.Sxc6#, cxd5 2.Se6#: every mate
is a discharge, and each defence opens a White line onto d6/e6 (Bc8 through d7, Rh6 through f6, Qa6 through c6). His
bench answer to the one-sided 1.Bb1!: with all mates on the battery, tries that touch the battery reach every variation.
The key came from the rule above (rear from the flight's diagonal) plus a black protector of the direct-check landing
c6. The key piece has one battery square from b4, so no tries by it: a second phase needs a rear with two battery
squares (a queen) or a different loaded/unloaded switch.
