# Studies: how published #2s work on the board

E. Bourd (11 Oct 2026): "start going over existing #2, starting with simple ones, understanding how the
mechanism works ... how to guard, what defends, how the tries work, how the paradoxes work."

Method: `python -m chesscomp.anatomy --fen "<FEN>" --tries 1` prints, for each phase, the king's 3x3 field
after every mate (which unit covers each square, which squares Black blocked itself, which Black unit is held
by a pin), what the first move changed in the field, why each try's threat fails after the refutation, and a
role table: the job of every White unit in the solution. A unit that is never the sole guard of a square in
any mate is flagged; then a solve without it says whether it is a cook-stopper or a try-only unit.
Every claim below was checked with the solver. Problems are from `knowledge/problemesis.json`.

## The ten problems

### 1. E. Bourd (psis-e2307f56cb), 8/2K5/B7/8/4k3/7Q/6P1/6B1, Le Grand in 6 units
1.Be3? (2.Qe6#) Kd5 2.Qf5#, but 1...Ke5!   1.Bc8! (2.Qf5#) Kd5 2.Qe6#, Kf4 2.Qe3#.
- The engine is geometry: f5 touches e4 and is two squares from d5; e6 touches d5 and is two from e4. Each
  mate is a contact mate from one king square and a distant mate from the other.
- The try makes both mates DISTANT ones: Be3 takes f4 so a queen two squares away covers the rest of the field.
  The key makes both CONTACT ones: c8 is the one bishop square that protects f5 and e6 together.
- Pg2 covers f3 only with the queen in the solution; without it the solution stands but the try's threat
  2.Qe6# fails (Kf3). It is there for the try alone.

### 2. Z. Labai (psis-bdd8420216), 8/1R5n/2p5/2k3N1/4Q3/K7/8/8, the same Le Grand engine
1.Kb3? (2.Qe5#) Kd6 2.Qd4#, but 1...Sf6! (interposes on d5)   1.Sf3! (2.Qd4#) Kd6 2.Qe5#.
- Same geometry, other pieces: d4 touches c5, two from d6; e5 touches d6, two from c5.
- Try: the king takes c4, the one square the distant Qe5 leaves open. Key: the knight from f3 protects d4
  AND e5. A knight forks two contact squares as the c8 bishop did along a diagonal.
- Ka3 is never needed alone in the solution (b4 also Q, R): its job is the try.
- Lesson: one mechanism, two realisations. Le Grand by flight = two mate squares in this cross-geometry,
  a try that guards the distant mate's free square, a key whose unit protects both contact squares.

### 3. S. Milewski (psis-9545cb04a6), 3Q1Kbk/6p1/3P4/6N1/8/8/8/8, black correction
Set 1...g6 2.Qf6#. 1.Qe8! (zz) g6 2.Qe5#, B~ 2.Qh5#, Bh7 2.Sf7#, Bf7 2.Kxf7#. Try 1.Qc8? Be6!
- Bg8 defends by interposing on h7. Random move: it can no longer reach h7, Qh5#.
- Corrections: Bh7 interposes in advance (self-block, and unguards f7: Sf7#); Bf7 blocks the e8-h5 line, but
  lands next to the white king, which takes it and opens the Qe8-Kf8 battery on the 8th rank.
- The try and key differ only in the queen's route to the h-file: from c8 it crosses e6, where a correction
  goes unpunished (refutation); from e8 it crosses f7, where the king punishes it.
- Pd6 is a plug: without it the d-file is open, cooked by 1.Qd4/1.Qd3 and 1.Ke7.

### 4. I. Kazimov (psis-436998ac49), 2R5/8/2N5/1N1kpP2/KR5b/8/8/6B1, vacating key, flight on a battery
1.Rg4? (2.Sb4#) e4!   1.Rc4! (2.Sb4#) Kxc4 2.Sb4#, Be7 2.Sxe7#, Be1 2.Se7#, e4 2.Rc5#.
- First job of the key: vacate b4 for the knight. The try does the same job and lacks the second one.
- Second job: from c4 the rook can reach c5 after 1...e4. The pawn self-blocks e4 but opens e5. Rc5 covers e5
  through the king.
- The flight c4 costs nothing. It lies on the Rc8-Sc6 battery, so the threat itself mates after Kxc4.
- Bh4 guards e7 and Be7/Be1 attack b4. Same mate square, with and without capture. Bg3/Bf2 give an
  unthematic Se7/Sb4 dual, left out of the published solution.

### 5. S. Milewski (psis-6d012efaba), 1k1b4/1r1P4/Q7/4R2K/5Rp1/8/7B/8, Boros, changed mates
1.Rc5? (2.Rc8#) Bc7 2.Rf8#, Rc7 2.Rb4#, but 1...Rb5!   1.Rc4! (2.Rc8#) Bc7 2.Re8#, Rc7 2.Rb5#.
- Two rooks: one goes to the c-file for the threat, the other stays to mate. Which one stays decides the mates.
- Bc7 and Rc7 cut the c-file and in doing so self-pin on Bh2's diagonal. The pin stops the interposition
  (Bc7-d8, Rc7-b7). Bh2 guards nothing alone: its whole job is that pin. A guard map cannot see it; the
  anatomy tool reports essential pins now.
- Kh5 anchors the refutation: 1...Rb5 pins Rc5 against the king. In the solution 1...Rb5 pins Re5 the same
  way, and the pinned rook takes the pinner with mate.

### 6. V. Marin y Llovet (psis-0ed732d73b), 2BkNK2/N2p4/3n4/8/8/4p3/4QB2/4b3, focal, Zilahi, correction
1.Qd2! (zz) Bxd2 2.Bh4#, Bxf2 2.Qa5#, exd2 2.Bb6#, exf2 2.Qg5#, S~ 2.Qxd7#, Sxc8 2.Sc6#.
- e3 is the crossing point of two white lines, Qd2-g5 and Bf2-b6. The black pawn plugs both. When the pawn
  takes one white piece, it unplugs the other's line.
- Be1 guards h4 directly, and a5 only behind the queen: Qd2-a5 itself would open e1-a5. So Qa5 needs Be1 gone,
  and Bh4 needs Be1 gone or busy.
- Correction: S~ opens the d-file (Qxd7, protected by Bc8); Sxc8 removes the protector but self-blocks c8,
  and the d7 pawn, pinned by the queen on the d-file, cannot take on c6.

### 7. M. Velimirović (psis-2a096adad9), Q4K2/2pp2B1/R1N1B3/2k5/2P5/8/8/8, black Albino
1.Qd8! (zz) dxc6 / Kd6 2.Qe7#, dxe6 2.Qd4#, d6 2.Bd4#, d5 2.Qxd5#. Set 1...d6 has a dual (Qa7/Bd4).
- Each pawn move does something different. d6 blocks the queen's d-file, so the bishop mates. d5 offers a
  protected capture. dxe6 opens the d-file and removes a d5 guard. dxc6 self-blocks c6 and removes Sc6; the
  queen from e7 covers b4 through the king.
- Kf8 covers e7 only together with Sc6 in the mates.

### 8. A. Slesarenko & P. Gvozdják (psis-8687c07e99), 3n1KB1/3p1n2/2p1k3/8/5P1B/2PQ4/8/8, Dombrovskis
1.Be7? (2.Qe4# A) d5 2.Qh3#, but 1...d6!   1.c4? (2.Qg6# B) d6 2.Qh3#, but 1...d5!
1.Ke8! (2.Qxd7#) d6 2.Qe4# A, d5 2.Qg6# B.
- How the paradox works: a Black move has a main effect and a side effect. In the solution, d6 and d5 defend
  by their main effect: they cut the queen's d-file against Qxd7. In the tries they refute by their side
  effect: they vacate d7 as a flight. The key, the king to e8, guards d7, so the side effect is dead and only
  the self-block (d6 or d5) remains, which allows the threat of the try.
- Sf7 is pinned by Bg8 in 2.Qe4# (it would interpose on e5).
- Pc3 takes no part in the solution. It is sound without it; it exists only for the try 1.c4?.

### 9. J. M. Rice (psis-c364835f46), R7/4N3/4p3/1k1nR3/3B3Q/1PP5/8/5K2, unpin key in a stalemate position
1.Bb6? (2.Qb4#) Kxb6!   1.Ba7? (2.Qa4#) Ka6!   1.Bc5! (2.Qc4#) Kxc5/Sb6 2.Qb4#, Sxe7 2.Qa4#, Se3+ 2.Bxe3#, Sf4 2.c4#.
- In the diagram Black has no move: Sd5 pinned by Re5, e6 blocked by Re5, king boxed in. Most waiting
  moves stalemate.
- The bishop goes onto the pin line (c5) and frees the knight. Every knight move now needs its own mate.
- The flight Kxc5 is safe because the king walks onto the pin line and re-pins its own knight (Re5-d5-c5).
- The tries (bishop to b6/a7, queen threat on the same file) are refuted by king moves. That is acceptable
  in this style; under our rules it is a fatal flaw.

### 10. N. Velikÿ (psis-a03442d898), 1R4bB/8/1R3N1K/2k4p/2Br4/8/1N6/B7, focal rook, masked batteries
1.Ra6? (2.Rb5#) R~d 2.Se4#, R~4 2.Sd7#, Rxc4 2.Sd3#, Bxc4 2.Sa4#, but 1...Rd6!
1.Bd5! (2.Rc6#) R~d 2.Sa4#, R~4 2.Sd3#, Rxd5 2.Se4#, Bxd5 2.Sd7#.
- Rd4 is focal: the file guards d3/d7, the rank guards a4/e4. Leaving one line gives the knight mates there.
- The key bishop moves out of c4 and into d5. That opens the rank to a4 and closes the file to d7, which
  changes which squares each rook move gives up: the mates are exchanged between phases (pseudo-Rukhlis).
- Two masked bishops: Ba1 behind Sb2, Bh8 behind Sf6, both aimed at d4. A knight that mates also opens its
  bishop onto d4, the square the rook just vacated. Each mating move covers the hole its defence made.

## Structural lessons (what to use when composing)

1. **Contact vs distant mate.** The same mate square is contact from one king square and distant from the
   next. A contact mate needs one supporter. A distant mate needs the leftover flight taken. A flight
   paradox (Le Grand, mate exchange) is built by choosing two squares in that cross-geometry, then one unit
   that protects both (a diagonal, a knight fork) for the key, and one that takes the leftover flight for
   the try. (1, 2)
2. **A key has a first job and a second job.** The try does the first job and lacks the second. The refutation
   is the one defence the second job answers. Design the second job and its refutation together. (4, 3, 10)
3. **A defence has a main effect and side effects.** Paradoxes come from switching which one matters: in the
   try the side effect refutes, in the solution the key kills the side effect and the main effect lets the
   mate in. (8; also the self-blocking pawn of 4)
4. **Pins do work that guard maps miss.** A self-pin stops the interposition (5). A king walking onto the pin
   line re-pins its own unit (9). A pinned pawn cannot capture the mating knight (6). The pinner's role is to
   pin, not to guard.
5. **Crossing points.** One black unit standing where two white lines cross gives focal play: whatever
   captures, one line opens (6). One black line piece holding two lines gives focal play too (10).
6. **A mating move can cover the hole its defence made**: a battery or masked bishop behind the mating knight
   (10), a battery for a flight given by the key (4), a rook that covers through the king (4, 7).
7. **Where a unit stands decides what it can punish.** A defender landing next to the White king, on a battery
   line, or on a pin line can be punished. Try and key choose routes whose crossing squares are or are not
   punished (3, 5).
8. **Economy is measured per mate.** In most of these problems at least one unit was never the sole guard of
   anything in the solution: a plug (3), a try-only pawn (1, 8), a try-only king (2). Published problems accept
   this. E. Bourd (11 Oct): a try-only unit is a drawback, weighed, not fatal.
