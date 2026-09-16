---
name: judge
description: Judge a #2 the way Evgeni Bourd does - run the solver and critique, then name fatal flaws, flaws and pluses in his order. Use before showing any position, and whenever asked "what do you think" of a position.
---

# Judge a #2

1. Solve: `python -m chesscomp.report --fen "<FEN> w - - 0 1" "#2" --critique`. Read the whole report,
   including the "further moves allow the threat" counts and the try list.
2. Count the force yourself (the critique does not): a third knight or rook, a second queen, two
   bishops on one colour = promoted piece = fatal unless the idea cannot exist without it.
3. Verdict in this order, see `references/checklist.md`:
   - Fatal: cook, dual in a thematic variation, double threat, unprovided check in set play, promoted
     piece, diagram flight, key by check or capture without thematic reason, try refuted by a king move.
   - Flaws: same refutation of several tries, passive units (the key piece is forgivable; a king that
     anchors a pin a defence creates is thematic), cook-stoppers, unprovided moves, heavy pawn count,
     thin play (one mating move), defences that merely guard the threat square.
   - Pluses: flight-giving key, long key, unified defences, dual avoidance with one motive, tries whose
     refutation uses the theme, changed mates, economy.
4. Weigh, do not count: a doubled or tripled theme can carry flaws that would be fatal in a simple
   problem (see the checklist's last section). Say what content each flaw is buying.
5. Say what the problem IS (theme, phases, changes) in two lines, then the flaws, then the pluses. No
   praise before the flaws. Give the FEN and draw the board.
6. If a repair is obvious (one unit), test it with the solver and report it as verified, not proposed.
