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
4. **Defenders.** Add Black units whose moves defend for the reasons chosen; each thematic defence gets
   one mate. Here the enumerator earns its keep: `KERNEL=... KEY_UCI=... KEY_SAN=... BUDGET_S=300 JOBS=4
   python -m chesscomp.compose.kernel_search <n_black> <n_white>` around the SOUND kernel only.
5. **Clean.** Every cook or dual has a one-unit remedy: load `stop-cooks`. One change, one solve.
6. **Trim.** Remove each unit and re-solve; remove pairs too. The critique lists what is not needed.
7. **Judge before showing**: load `judge`. Draw the board, give the FEN, name the flaws first.

## Tempo
One solve per change; never sixteen minutes of placing without a solve. If four or five posts of the
key piece give only "double threat", "holes" or "no threat", the geometry has no line to exploit:
clear the board and rebuild from the idea. Rotation and shifting only make room; they never supply a reason.

## Signals
- Pre-key solve returns only checking tries: no quiet threat exists in this structure. Restart.
- The solve names one thing (one cook with a line, one hole, one dual): fix it, one unit, one minute.
- The solver's necessity check says a unit is not needed: remove it unless it carries a try or set mate.
