# Dombrovskis paradox

A try 1.T? threatens 2.A# and is refuted by a defence a; after the key, the same a allows 2.A#. The paradox: the
move that stopped A now lets it through. The solver reports it under Patterns ("Dombrovskis (refutation): a [try T vs
key K]"); claim it only when it does. Doubled: two tries, two threats A and B, two refutations a and b, and after the
key a 2.A#, b 2.B#. The doubled form usually carries a change for free: in try 1 the defence b has another mate,
which the key changes to B (Slesarenko & Gvozdjak below), and the solver reports it under Changed continuations.

## Why a defends in the try and lets A through after the key
The defence must do two things: a side effect that beats A in the try (it vacates or opens a flight, removes A's
guard, closes a White line A needs) and a main effect that parries the key's threat and leaves A as the mate (a
self-block, a block of the threat line). The key kills the side effect: it guards the vacated flight, replaces the
removed guard, or makes the closed line unnecessary. Write both effects of every thematic defence before placing a
unit; a defence with one effect cannot be paradoxical.

## Engines read from the archive
1. **Pawn steps on the threat line, one vacated flight** (Slesarenko & Gvozdjak, Shakhmatnaya Kompozitsiya 1999,
   Special Prize, psis-8687c07e99): 3n1KB1/3p1n2/2p1k3/8/5P1B/2PQ4/8/8, 6+5. 1.Be7? (2.Qe4# A) d5 2.Qh3#, d6! a;
   1.c4? (2.Qg6# B) d6 2.Qh3#, d5! b; 1.Ke8! (2.Qxd7#) d6 2.Qe4# A, d5 2.Qg6# B. The pawn beside the king's file
   stands on the queen's file: both steps block the threat Qxd7 and self-block, both vacate d7 (the side effect);
   the king key guards d7. Each try's other step is met by Qh3#, so the key also changes two mates. The model of
   the doubled form; do not mirror it.
2. **Captures of two sole guards** (E. Bourd, session 28, bourd-double-dombrovskis in knowledge/problems.json):
   a knight is the only guard of d4, a pawn the only guard of d6; dxe6 and Bxe5 remove one each and refute the tries
   whose threat needs that square; the key 1.Bc5! covers both squares and threatens a mate both captures parry for
   reasons of their own. Heavy (11+11); the method is general: one key unit that replaces two removed guards.
3. **Grimshaw by capture** (Manolescu, Buletin Problemistic 1984-85, 2nd Prize, psis-e1c54a41bb):
   7n/2K1P3/3B4/3kN3/R2N1r2/5P2/2P2b1Q/7B. Bxd4 and Rxd4 both take the knight d4; each capture closes the other
   piece's line. Tries 1.Sec6? (2.c4#) Bxd4! and 1.c3? (2.Ra5#) Rxd4!; key 1.Qh3! (2.Qe6#) Bxd4 2.c4#, Rxd4 2.Ra5#.
4. **King flights** (Zhuravlev psis-546cff2c9b, Cuppini psis-49233800b3, E. Bourd psis-9d842df173): tries refuted
   by king moves into flights, a waiting key. Not for us: a try refuted by a king move is a fatal flaw in our
   constitution, whatever the archive printed.
5. **Changed threats on the same refutation pair** (Onkoud, Problemesis 2001, psis-f1aad5e7c6): 8/p2B4/3pN1p1/2Pkpr1Q/
   4R3/3Kp3/3N4/8, 1.Qh1? (2.Rd4#) Rf3!, 1.Sb3? (2.Sc7#) dxc5!, 1.Sc4! (2.Sxe3#) Rf3 2.Rd4#, dxc5 2.Sc7#: two
   unrelated black units, a doubling by addition.

## Tools
- `chesscomp.compose.pattern_search` (DEF=a,b; every listed defence must carry the pattern) adds one or two units
  around a kernel; the one-variation No. 1 (6K1/1N6/4p3/1PBk3p/8/8/4Q3/6N1) came out of it in seven minutes.
- `chesscomp.compose.evolve` with PATTERN='Dombrovskis (refutation)' DEFS=a,b scores the pattern on each defence. With no DEFS
  (PATTERN=... NPAT=n) it rewards the pattern on any defence; since 21 Oct DEFS no longer defaults to d6,d5 there.
  It found no gradient from a sound kernel without the pattern: use the exhaustive layers instead.

## What failed on 21 Oct 2026 (daily No. 16, a study post on Manolescu)
- **The pawn two files away** (Kf5, e7, black Bd8): both steps open d8-h4 (the bishop then guards g5) and each
  self-blocks its own square. That gave a sound kernel at once: 3b4/4p3/8/5k1P/8/1BQ2P1N/8/7K, 1.Qg7! (2.Qg5#) e6
  2.Bc2#, e5 2.Qg6#. But neither step has a side effect a key can cancel. 2.Qg6# needs a queen that reaches g6 and
  guards e5, and only the key square g7 does both. 2.Bc2# needs another guard of e6, and every line through e6 runs on to
  f6/g6, which the kernel already covers. Every one- and two-unit layer around it was searched (pattern_search
  w1/w2/w1b1/m1, plus a scan that moves or removes one unit and adds one: about 47,000 positions), with no try.
- **The e-file threat trap**: 1.Qe1? (2.Qe6#) e5! and 1.Qc4 e5 2.Qe6# look like a paradox, but a queen on e6 covers
  e5 itself, so wherever 2.Qe6# mates after ...e5 it is already the key's threat. A pawn step cannot be the reason
  for a mate whose mating piece covers the step's own square.
- **Two pawns beside the king** (Ke5, d6, f6, single steps vacating d6/f6): evolve finds sound zugzwangs
  (8/4K3/3p1p1R/4k3/8/4B3/6Q1/7N, 1.Qf3!), but with a White king or a fixed unit guarding the vacated squares they
  never become flights. Then the scans' paradoxes pair two tries, not a try and the key.
- Rule: before placing anything, write for each thematic defence its side effect (what beats the try) and the unit
  that cancels it after the key. If no unit can cancel it, the pair is a scheme for another theme, not a Dombrovskis.
