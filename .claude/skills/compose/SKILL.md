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
3c'. **Errors before any search** (E. Bourd, 8 Oct 2026: "this small thing cannot be just search"). For every
   defence, and every hole, run `python3 -m chesscomp.compose.effects POSTKEY [MOVE ...]`: it lists what the move's
   departure and arrival change (self-block, lines opened/closed with the squares, guards lost/gained, pins) and
   marks each error as `only this move` or `[also ...]`. Choose each mate from an error that is only that move's
   (or a shared one that every other defence cancels by a property of its own, like a knight on d4 guarding e6).
   Write the choice down: "1...Se4: self-block e4 -> a mate that needs e4 blocked; must fail after Bb5, which
   opens Qb4-e4". Only then search, and only to place the unit that the named mate needs. A search with no named
   error is a guess; a one-unit search cannot supply a missing error.
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
clear the board and rebuild from the idea. Rotation and shifting only make room; they never supply a reason.

## Signals
- Pre-key solve returns only checking tries: no quiet threat exists in this structure. Restart.
- The solve names one thing (one cook with a line, one hole, one dual): fix it, one unit, one minute.
- The solver's necessity check says a unit is not needed: remove it unless it carries a try or set mate.
