# Novotny

A White unit goes to the crossing square X of a black rook line and a black bishop line, where both can capture
it; each capture puts the capturer on X and so closes the other piece's line. In the classic #2 the key on X
threatens two mates, each stopped by one of the lines, and each capture leaves exactly one of them (English
Novotny). Our gate calls a double threat fatal (the checklist calls a thematic one content: ask before relying on
it), so the blog's Novotny (daily No. 13) has a single threat.

## Single threat: why else does each mate wait for its capture?
After the key both lines are already closed by the White unit on X, so a mate that only needs one line closed is
a second threat. Each thematic mate must also need something only its capture gives. Three answers in the archive
and in the kit:

1. **Double guard** (daily No. 13, tool `python3 -m chesscomp.compose.novotny_geometry K`): the mating square A is
   held by the rook along its OTHER line (from its origin) and by the bishop through X; B the other way round.
   RxX: the rook leaves its other line and cuts the bishop at X, so A is free; B is still held by the bishop's
   other diagonal. The separation needs no extra unit. Up to symmetry there is one geometry per king square with
   knight mates: Ke4, Rc6, Be7, X d6, A c5, B f6, and one knight d7 reaches both (1...Rxd6 2.Sc5#, 1...Bxd6 2.Sf6#).
2. **Departure opens a White line** (Shire, The Problemist 1997, 2nd Prize, psis-1e6c532522: 1.Bc5! (2.Bd5#)
   Rxc5 2.Qd3#, Bxc5 2.Qe6#): the queen's two lines pass through the capturers' origins (Qa6: b5 and b6).
3. **The key piece is the threat piece**: in both of the above the captured unit makes the threat, so every
   capture defends by removing it; the defences need no further reason.

A threat by a third unit makes the captures defend only if X's unit guards the threat's mate (Le Grand and others,
Eretria 2005, psis-2ff38272a6: 1.Sd5! (2.Ra6#) Bxd5 2.c5#, Rxd5 2.Sxf7#).

## What the double-guard form gives and what it cannot
- The same square is a set Grimshaw when nothing stands on X: 1...Bd6 2.Sf6#, 1...Rd6 2.Sc5#. After the key the
  Novotny captures give the same mates (transferred). This geometry cannot change them: the separation is the
  double guard itself, identical in both phases. Changed mates on the Grimshaw/Novotny square need another
  mechanism (Rice, The Problemist 1966, 2nd Prize, psis-434d985eb2: set Be4 Qxe5, Re4 Qd5; 1.Se4! with a double
  threat, Bxe4 2.Bxe5#, Rxe4 2.Bc6#).
- Donati (Phénix 1999, psis-16af024ec2) has the set Grimshaw on b6 with the same knight mates from d7 and the key
  1.Bb6!, but the captures on b6 do not defend (the threat Qd3# is not touched). The real Novotny defences are what
  No. 13 adds.
- The key rook (on X: a rook, since a bishop on X cannot check and a queen gives too many threats) can only come
  along the black rook's line: from the d-file below it mates at once (Rd4#), from d7/d8 the knight or bishop is in
  the way. So the key piece stands attacked in the diagram, and 1.Rxc6 needs a black guard of c6 (bPb7).
- The black rook's file below X reaches c4, which attacks the threat square d4: give 1...Rc4 a mate of its own
  (2.Re6#, the rook leaves the sixth rank) instead of a White pawn on c4 that the rook takes (2.Rxc4# recaptures).

## Settings
- Daily No. 13 (18 Oct 2026): 8/1p1Nb3/1Nr3R1/8/4k1P1/4P3/4PPK1/B7, 1.Rd6! (2.Rd4#) Bxd6 2.Sf6#, Rxd6 2.Sc5#,
  Rc4 2.Re6#, Bf6 2.Sxf6#; set Bd6 2.Sf6#, Rd6 2.Sc5#, R~ 2.Re6#. Built with freethreat/postsearch (KMP=d7,
  THREAT Rd6d4) on the core from novotny_geometry, then keyfind (one key: from g6), then guards rebuilt by hand.

## Dead ends
- A White bishop on X with a threat by another piece (first freethreat runs): the captures did not defend.
- The queen on X (q1 run): post-keys with the Novotny pair, but every key gave other solutions (Qxc6, Qxe7, knight
  checks).
