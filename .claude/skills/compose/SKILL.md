---
name: compose
description: Compose a #2 chess problem from a theme or a scheme, in Evgeni Bourd's order - mechanism, box, reason for the key, defenders, cleaning, trimming. Use for any request to compose, set, build or finish a problem.
---

# Compose a #2

Read `references/construction.md` now (the order and the rules with their example FENs) and
`references/dead_ends.md` (what has already failed, with the reason). Do not repeat a dead end.

## Order of work
1. **Mechanism first, on paper.** Choose the Black effect that yields several mates (self-block, self-pin
   by capture, line closing/opening, unguard) and the squares it happens on. Mating squares and lines
   close to the king. Ask, before placing anything: what is the REASON the thematic moves defend? The five
   reasons are in the reference. If none is available for the square, no queen post will supply one.
2. **Kernel.** Place the black king boxed (no flights), the pieces of the mechanism, the key piece and its
   reason for the key square. Solve. A sound kernel of 5-8 units is the goal of this step; nothing else.
3. **Reason for the key.** The key must be the only move: the other candidates fail for stated reasons
   (a check the king escapes, stalemate, a line the piece must keep, a square it must protect).
3b. **No kernel yet?** Sketch the theme's core and let `chesscomp.compose.evolve` grow candidates (see its
   docstring); it found a sound five-unit pawn-step mutate in a minute where hand kernels took hours. Treat
   its output as sketches to judge and refine, not as finished problems.
   For a Black correction use `CORR=<square of the correcting piece>` (and `DEFS=`): it scores the
   solver's S~ lines. Seed it with a hand sketch of the mechanism, not a bare king: from a blank core it found
   corrections but no key in 20 minutes; from a sketch, a sound eight-unit problem in two (daily No. 2).
3c. **Two mates per defence and you want changed mates?** Separate before you add blockers. Run
   `python3 -m chesscomp.compose.separate FEN DEF DEF` on the scheme: it lists the mates left after each
   named defence for every white first move, and the pairs of moves that give one distinct mate per defence
   with every mate changed (a try/key pair). No pair means the selectors are on different pieces: change the
   geometry (E. Bourd shifted his whole scheme one file) rather than piling on cook-stoppers.
   Have the mates you want but rivals remain? `python3 -m chesscomp.compose.keepkill FEN "Ke4: c6=Sf5 c5=Qh6"
   "Be6: c6=Sc8 c5=Qe5"` tries every single unit and lists those that leave only the wanted mate per defence
   in every named phase, fewest new black moves first. On his pawn-step scheme it ranks his bPe5 first.
   These are implementation aids, not ideas (E. Bourd: "add one unit that eliminates mates? That's not an
   idea, that's a specific implementation"). Decide the reason for every split first; use a tool to place it.
3c-type1. **Changed mates of one queen (type 1)?** `python -m chesscomp.compose.type1_geometry d4 --types RB` lists the queen
   post pairs, the defenders that free one mating square per phase, and the knight threats with each defender's off-line
   defences and plugs. Then a guard table by hand; `evolve` with DEFSQ/TKEY/QMATE and CANDS only for the last layer.
   Two errors per defence: only the far pair of mating squares can take them (themes/changed_mates.md); check each
   defence with `python -m chesscomp.compose.errors FEN DEF --key UCI` (departure / arrival per mate).
3c0. **Try/key changes on the same defences?** `python3 -m chesscomp.compose.trychange` (env CORE, SEED, KP or Q, THREAT,
   DEFS, ONLY, FORBID, TARGET) scores pairs of key-piece moves by the mates after each defence, without the solver: a
   mechanism in minutes (Grimshaw queen posts, 15 Oct 2026), never a sound problem. Solve every hit.
3c'. **Errors before any search** (E. Bourd, 8 Oct 2026: "this small thing cannot be just search"). For every
   defence, and every hole, run `python3 -m chesscomp.compose.effects POSTKEY [MOVE ...]`: it lists what the move's
   departure and arrival change (self-block, lines opened/closed with the squares, guards lost/gained, pins) and
   marks each error as `only this move` or `[also ...]`. Choose each mate from an error that is only that move's
   (or a shared one that every other defence cancels by a property of its own, like a knight on d4 guarding e6).
   Write the choice down: "1...Se4: self-block e4 -> a mate that needs e4 blocked; must fail after Bb5, which
   opens Qb4-e4". Only then search, and only to place the unit that the named mate needs. A search with no named
   error is a guess; a one-unit search cannot supply a missing error.
3c'''. **Threat first, then the post-key position** (E. Bourd, 8 Oct 2026): fix the threat that makes the thematic
   moves defend, then `READY=1 python3 -m chesscomp.compose.postsearch CORE SEED THREAT DEFS BUDGET RNG` builds the
   post-key position (threat fixed, named defences single and distinct, no holes, White's other mates minimised),
   then keyfind and trim. Grimshaw on c3 (claude-grimshaw-c3-qc1) came out this way after 20 failed diagram searches.
3c''. **Coverage claims by tool, not by eye**: `python3 -m chesscomp.compose.matecheck FEN "MOVE"` lists each square of
   the king's field with its White guards (or FREE), the interpositions and the captures of the checker. Decide the
   threat line and its interpositions before the mates.
3d. **Find the key with `python3 -m chesscomp.compose.keyfind POSTKEY [--patch]`.** It takes back every White
   unit one move, keeps the diagrams where that move is the only key and the post-key play is unchanged, and ranks
   them (sacrifice, flight given, changed set play high; check, capture, idle or out-of-play key piece low).
   --patch adds one unit to near-misses. It first prints the other mates in two that the post-key position already
   has with White to move, and which unit they all need: no shared unit = no key until the position is tightened.
   His way when no unit can be taken back (8 Oct 2026): take the key piece from the units that already play,
   never a new one. Put a unit with a role on the threat's line or a mating square, give it a job it must keep
   from its new square (rook d6 -> g6 still guards e6/f6), so one clearance square works and the others are
   tries; then clean cooks one at a time (bourd-b5-three-blocks-rg6). A new officer placed only to clear a line
   is fatal ('useless key piece').
   **Key last is too late.** `python3 -m chesscomp.compose.retract POSTKEY` undoes every white move of a
   finished post-key position and solves each diagram (his habit: post-key position first, then take the key
   back). It only finds the keys the position already allows: in session 29 two good mechanisms gave only
   idle or flight-taking keys. Think about the key's role while the mechanism is still soft.
   **Whole-diagram search** (11 Oct 2026): `python3 -m chesscomp.compose.diagsearch CORE SEED DEFS BUDGET RNG` mutates
   everything outside CORE and scores by solver and critique. Put the theme's carriers in CORE, or it drops the theme.
   **Unmasking-key search** (11 Oct 2026): `python3 -m chesscomp.compose.unmask_search CORE SEED KSQ FSQ PSQ WANT BUDGET RNG`
   fixes the post-key core, lets the threat be free (one threat, not by the pinner on PSQ), and scores the diagram with the
   key unit moved back from KSQ to FSQ: no flight, no check, key piece in play, no idle White unit, unique key. A pinner
   that must come from the edge is out of play; mask the pin with a unit next to the king instead, and give it a new job
   that only exists after the key (Bd5-f7 protecting the threat square, claude-two-rooks-unpin-bf7).
   Prefer a threat to a zugzwang when you can: "it makes the problem richer. Zugzwang is limited and a bit
   less interesting by nature" (E. Bourd).
   With pawns the geometry has little room: "Pawn move themes are limiting by nature, can't rotate or move
   the board up or down. It does make the mechanism more rigid and less open for enhancements" (E. Bourd).
   A double step ties the pawn to its home rank, so only file shifts and the left-right mirror remain; plan
   the selectors with that in mind from the start, since the board will not rescue a pawn mechanism later.
   This binds only pawns whose moves are thematic; cook-stopper pawns can be rearranged after a rotation.
   Keep the thematic play central: "Just by the freedom, the edge seems very limiting. Much less mates or
   freedoms to play with."
4. **Defenders.** Add Black units whose moves defend for the reasons chosen; each thematic defence gets
   one mate. Here the enumerator earns its keep: `KERNEL=... KEY_UCI=... KEY_SAN=... BUDGET_S=300 JOBS=4
   python -m chesscomp.compose.kernel_search <n_black> <n_white>` around the SOUND kernel only.
5. **Clean.** Every cook or dual has a one-unit remedy: load `stop-cooks`. One change, one solve.
6. **Trim, recursively.** `python3 -m chesscomp.compose.trim FEN` removes units in every order until nothing more
   can go with the same key and play: some units are artifacts of others (E. Bourd: bPh6 only stopped bRh5's checks).
6b. **Extend before showing** (E. Bourd, 11 Oct 2026). The theme working is a stage, not the end: ask what can be
   added and try it - tries by the key piece refuted by the thematic defences, changed mates, a cleaner position.
   Example: 1.Bf7! (static, theme only) became 1.Sa3! with a knight wheel once the mask moved to b5 and the key
   piece became a knight whose other moves block the queen's mates. Avoid symmetry for its own sake: it is a
   flaw in general.
6c. **Make a try's refutation thematic** (E. Bourd, 15 Oct 2026: "how would you find that improvement, its not just
   trimming"). Read why the try fails (anatomy: "Sc2+: flight e4"): the try lacks a guard the key has. If its only guard is a
   pawn or a short-range unit, the refutation can only capture it. Re-guard the square with a line piece whose line crosses a
   thematic unit's line, and the refutation becomes a quiet interference: `python -m chesscomp.compose.rerefute FEN KEY TRY
   THEME DEFS` (his 1.Qf7? Bxf3! -> -Pf3 +Bg6, 1.Qf7? Rf5!, found alone in 13 s).
7. **Judge before showing**: load `judge`. Draw the board, give the FEN, name the flaws first.

## Shrink before you grow
When the mechanism is known, find its minimal form first: the mate picture with the fewest units, kings and
the key piece moved one square per solve (E. Bourd: 12 units -> 4 in nine solves, 7K/3P1k2/3Q4/8/8/8/8/8).
Add units only to add content, never to protect a structure that was already bigger than the idea. When two
thematic moves both solve, choose the key and make the other fail for its own reason: that is a doubling.

## Light enough to extend (E. Bourd, session 27)
Start small: a random move and one mate on a near-empty board, then the threat, then one correction,
then a second. A mechanism that is light (few units, no square that only one unit covers, no flight the
whole structure depends on) leaves room to add content later; a heavy or rigid one, or one that hangs on
very specific flights, cannot be extended without breaking. His b5-knight scheme grew from three units to
a second self-block correction because every step was checked at its lightest form. My Bf2-g3 cell died
because it needed every flight covered from the start: nothing could be added and nothing could move.

## Tempo
One solve per change; never sixteen minutes of placing without a solve. If four or five posts of the
key piece give only "double threat", "holes" or "no threat", the geometry has no line to exploit:
clear the board and rebuild from the idea. Rotation and shifting never supply a reason, but they keep the theme and
change the pawns and the edges: see "Shifts and rotations" below.

## Signals
- Pre-key solve returns only checking tries: no quiet threat exists in this structure. Restart.
- The solve names one thing (one cook with a line, one hole, one dual): fix it, one unit, one minute.
- The solver's necessity check says a unit is not needed: remove it unless it carries a try or set mate.

## Order of work (E. Bourd, session 30)
Hardest constraint first: whatever may force a change of scheme or geometry (a threat against two flights, a
square next to the king, getting two phases) before the mates, the mates before the construction, and the
non-thematic duals last. If a requirement keeps resisting, consider a level switch (threat to zugzwang), which
can turn the same Black moves into corrections. Give every construction unit a stated purpose.

## Restructure, do not patch (E. Bourd, 11 Oct 2026)
"The really small steps cant do it... its whole restructuring." When cooks keep returning or no key comes, keep the
thematic core and rebuild a whole side at once from the mechanism's needs, then solve that as one change. One-unit
steps are for cleaning a position that is already sound.

## Soften before searching for a key (E. Bourd, 11 Oct 2026)
A sound post-key with no key is not a dead end. In this order: move each mate next to its piece's natural post
(Qh8# -> Qf6# with the queen on g5); give each free White officer a duty it must keep (the queen guards a pawn); replace
White guards by Black self-blocks; protect mating squares with short-range units; then retract the theme's carrier (the
pinner) as the key. Example: 8/3n4/2R1P1B1/R2pk3/7Q/3n4/3B2b1/K7 -> 8/3n4/R2p4/3pkPQN/4p3/3nP3/b2B4/K7, 1.Ra5!.

## One unit, several line-closing errors (12 Oct 2026)
Enumerate the geometry before placing: `python3 -m chesscomp.compose.line_skeletons d5 [--t e3]` (threat square, knight
square, two arrivals guarding it, the black line each arrival closes). Then the post-key with
`python3 -m chesscomp.compose.freethreat CORE SEED '{"Nc2":"N*c3","Ng2":"Qe8e4"}' zz 270 RNG`, then the key with
`unmask_search` (KSQ/FSQ fixed). A key that only adds a guard cannot create a check threat (flight or mate in one);
bring the threat piece instead. Pawns protecting diagonal mating squares recapture with check: use a rook or knight.
Result: 4Q3/6p1/8/2Pk4/2R5/1Pp3K1/3N4/1Nr1n2b, 1.Sf1! Sg2 Qe4#, Sc2 Sxc3#.
Then E. Bourd: pieces closer, key from the centre, and the try pair is a must ("Showing just 1 gives bad taste"); a
by-play that repeats a thematic mate also refutes the partner try (1...Rd1). `python3 -m chesscomp.compose.knight_pair_skeletons
d5` lists skeletons whose rook escapes self-blocks can stop; the clearance key (the knight leaves the threat square
for the square reaching both mates) gives the pair for free: 8/1r6/1p1PRn2/1KpkNB2/2p1p2r/2Q5/b2P4/8, 1.Sg6!,
tries 1.Sd3? Sd7!, 1.Sc6? Sg4!.

## Two units self-block one square (12 Oct 2026)
The square needs no White guard after the key (the flight is given by the key), and the threat may not check through
it (the blockers interpose before it plays). Motive that works: a White line masked by the threat piece runs through
the square to the next field square; the threat unmasks it, the block cuts it. Search with `SELFBLOCK=1` (freethreat,
postsearch, unmask_search). Prefer the king on the edge: fewer static guards, fewer other solutions. In the diagram the
square is guarded, so each thematic mate is a mate in one unless the key adds what it needs or Black can parry it.
Result: n2kNB2/8/B6p/2N3nQ/8/3K2b1/1R6/2R5, 1.Sf6! (2.Sb7#) Sc7 2.Rb8#, Bc7 2.Qe8#, Kc7 2.Se6#.
E. Bourd called it "mega complicated" and built five easier schemes on the bench the same day: ask first which mates
can come on the block, then the separation, then why Black goes there. Simplest motive: capture a White unit standing
on the square that the threat needs (1.Qd6!, 1.Bf4!, 1.Bf6! with a pin as separation). A threat through the square
works if it is a double check (no interposition): 1.Qd3! (2.Rc7#, unmasking Bf8 through d6). Zugzwang is the last
resort. A sacrifice key captured three ways is anticipated (Strebkovs 2003); capture defences after a quiet key are not.

## Tries by the key piece (E. Bourd, 12 Oct 2026)
"Usually by the same piece that moves away to open a line or to guard a square." Choose the try piece before the
guards: one White unit whose every move creates the threat (a knight on the threat square: each move vacates it and
guards it). Then list, for each thematic mate, what a landing square can spoil: a line mate's path (Sf2 blocks
Bg1-d4: a pure try), a guard line to a flight through the landing square (f6 cuts Rf8 or Rh6), or the flight the
mating unit gives up (then only the landing squares guarding it keep the mate, and all the others fail to the same
defence). A knight mate has no path: its pure try needs a guard line through a landing square, i.e. one more heavy
piece. Search with `unmask_search` (THREAT=<mate id>, TRIES='{"e4f2":"c1c5",...}'); a black check that refutes
every try (Rxg1+ on the king) can hide cooks: block it and re-solve before trusting a "sound" result.
Result: 6b1/b3N2p/3ppP1K/R2pk1P1/3pN2R/8/7P/2r1n1B1, 1.Sg3! (1.Sd2? Bc5!, 1.Sf2? Bc5!/Rc5!), rejected: "without a
pure pair, its almost not worth having 1 pair" and a try with both refutations "is not a thing" (E. Bourd). The pure
pair came from a line lever on the knight-mate side: a white pawn on the flight e6 protected by the mating knight and
by Rh6 along the rank, cut by the landing square f6: 3N2b1/b2P3p/3pP2R/1Q1pk1K1/3pN2R/8/1n1PP1PP/2r3B1, 1.Sg3!
(1.Sf2? Rc5!, 1.Sf6? Bc5!). `python3 -m chesscomp.compose.trypair` (SPEC env) enumerates the last stoppers.

## Spread the scheme (E. Bourd, 11 Oct 2026)
Place the scheme so the mechanism's parts are apart: the guarding line long, its cut squares away from the king, the
cutting pieces at a distance with free paths (his 8/8/3P3R/3k4/8/2bb4/8/8: Rh6 guards the 6th rank, the bishops cut at
f6/g6 from anywhere on their diagonals). A unit inside the king's field (my Be5: guards d4, d6, f4, f6, sits on the
e-file and the 5th rank) interferes with too much and takes the freedom; every change ripples. Not always possible;
starting soft is a skill. Units may move into the field later, when a need puts them there (his bishop went to c5).
Decide the line, not the square: the square the threat needs guarded may move along the guarded line (he went
from d6 to e6). Put the error mates away from the cut line (his second sitting: cuts on f6/g6, mates Sb4#/Qb3# on
the far side), so they do not tangle with the play around the cuts and need little patching:
nK6/3B4/N2PP2R/2Bk2P1/5P2/2b2P2/2b1Q3/8, 1.Qb5! Bf6 Sb4#, Bg6 Qb3#. Among keys take the origin that gives the key a
thematic job (Qe2 leaves the e-file guard of e6) over a bare only-key (Qf1), even at a cook-stopper's price.
A cook-stopper can often move so that it also plays: `python3 -m chesscomp.compose.restop FEN KEY "Bf6=Sb4#,..." a8`
(his Sa8 -> Se8: 1...Sf6 2.Sc7#, a third cut).
Connect the variations by reusing the mating pieces (E. Bourd): let the mating units share a guard square that each
holds in the other's mate (Sa6 and Qb5 both on c5: Qb5 holds it for Sb4#, Sa6 for Qb3#). Check it with
`python -m chesscomp.anatomy --fen FEN`, section LINKS; "none" means two distant variations.

## Shifts and rotations (E. Bourd, 11 Oct 2026)
"They do not ruin the base of the theme": the line pieces keep their geometry (the two bishops change colour together).
What changes is the pawns (direction, captures, promotion) and the edges (room for the White king). Reach for it when
the stuck point is a pawn or the White king's room, after the White king and queen have been moved and spare units
stripped. `python3 -m chesscomp.compose.transform FEN --all --post` solves every legal placement of a post-key
(`--pre` for a diagram; `--rot 90|180|270 --flip --shift dx,dy` for one). His sitting: a quarter turn made a black
c2/c3/c4 chain (it checked Kb3, captured on b3, promoted) into a static b6/c6/d6 chain, the targets of the mates;
three changes later 5N2/2KQ1p2/1ppp3n/1bbkBPp1/8/2R2P2/8/4R3, 1.Sg6! Be2 Qxc6#, Be3 Qxd6#; try Sh7? Be2!.
Among several unique keys he took the origin with a try (Sf8: 1.Sh7?; from h4 none, from h8 only 1.Sxf7?).
