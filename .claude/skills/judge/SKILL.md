---
name: judge
description: Judge a #2 the way Evgeni Bourd does - run the solver and critique, then name fatal flaws, flaws and pluses in his order. Use before showing any position, and whenever asked "what do you think" of a position.
---

# Judge a #2

1. Solve: `python -m chesscomp.report --fen "<FEN> w - - 0 1" "#2" --critique`. Read the whole report,
   including the "further moves allow the threat" counts and the try list.
2. Roles: `python -m chesscomp.anatomy --fen "<FEN>" --tries 1` (king field per mate, essential pins, role
   table). A unit flagged "no part" or "needed in no mate" (removal test) gets one solve without it: cook-stopper or
   try-only unit (a drawback, E. Bourd 11 Oct). The critique does not check this. Call a unit a cook-stopper only when
   you can name the cook it stops; a unit the solution needs (it guards a flight the key would give) is part of the
   problem, and a king that just exists is no flaw (E. Bourd, 26 Oct 2026: "what cook exactly are they stopping").
   Count the force yourself (the critique does not): a third knight or rook, a second queen, two
   bishops on one colour = promoted piece = fatal unless the idea cannot exist without it.
3. Verdict in this order, see `references/checklist.md`:
   - Fatal: cook, dual in a thematic variation, double threat, unprovided check in set play, promoted
     piece, diagram flight, key by check or capture of a piece without thematic reason, try refuted by a king move (a try the problem shows;
     an incidental White move refuted by a king move is no try and no flaw, E. Bourd 26 Oct 2026). Random moves
     answered by one mate (S~) are not defences: never count them as content (E. Bourd, 26 Oct 2026).
     A pawn capture (key, try, mate, refutation) is minor (E. Bourd, 13 Oct 2026); do not lead a verdict with it.
     A dual is a flaw only after a move that defends and corrects: a move of the correcting piece that still allows the
     random mate (it keeps the error and adds another, 1...Re4 2.Sxf5#/Rd3#) and a move that does not defend the threat
     have no duals worth naming (E. Bourd, 29 Oct 2026: "logically its not a flaw as its not a logical progression").
   - Flaws: same refutation of several tries, passive units (the key piece is forgivable; a king that
     anchors a pin a defence creates is thematic; a passive king is acceptable, E. Bourd), a unit that serves
     only the set play (big flaw when completely redundant), cook-stoppers (acceptable: usual cost), unprovided moves, heavy pawn count,
     thin play (one mating move), defences that merely guard the threat square in a single-phase problem (with changed
     mates they are pure single moves, no flaw: E. Bourd 14 Oct 2026), a mate that recaptures the defender on its arrival square.
   - A second layer that reaches one of two thematic variations (one try, one change) is not enough (E. Bourd, issue #21):
     the gate fails it as 'one-sided extension'.
   - The tries need one concept (E. Bourd, 27 Oct 2026): each fails for the same kind of reason. A try capturing a black
     officer is no try (1.Bxh6? in daily No. 21); random tries plus a correction refuted by a capture are 'almost random'.
   - Pluses: flight-giving key, long key, unified defences, dual avoidance with one motive, tries whose
     refutation uses the theme, changed mates, economy, connected variations (the mating units hold a square for each other: anatomy LINKS,
     E. Bourd 11 Oct 2026). Unified play beats a mixed set (defences that all
     guard one square, tries on one scheme), E. Bourd. A protected key piece the king attacks is no flaw
     when the key has several jobs (gives a flight, opens a line, guards the threat square).
3b. Cause before verdict (E. Bourd, 24 Oct 2026: "a good critique is a good composer... this pure raw flaw count needs
   some element of understanding the anatomy, freedom of the position"). For every flaw the critique flags, say what it
   is FOR before calling it a flaw: which unit or line makes it, what it does in the scheme, and what the obvious repair
   would break (reason it from the anatomy; one solve if unsure). Structural (the repair kills the idea or cooks it):
   it is the price of the idea, judged with the idea. Constructional (another construction does the job): a real flaw,
   repair it before showing. Read every try as a sentence: what does it show about the diagram? His masked pin 1.Bf2!:
   the e4 flight is the only answer to the free knight's checks (a set mate for Ke4 cooks), and wPc2 plays
   1.cxd3?, which shows that knight free before the key pins it; both were flagged, both are the idea.
   A removal test sees cooks and lost variations, not every job: first write each thematic variation's dual avoidance
   (which sibling mate fails, by which line or guard). His bQa3 (28 Oct 2026) looked like a cook-stopper and was the
   set play's dual avoidance (d6 seen through the vacated c5); his bPf6 kept 1...Se3 the knight's only defence.
4. Weigh, do not count; tolerance grows with content (E. Bourd, 12 Oct: "we pay flaws for content, and find
   the balance"). Place the problem on the scale in `references/checklist.md` (light / medium / rich) first.
   Weigh, do not count: a doubled or tripled theme can carry flaws that would be fatal in a simple
   problem (see the checklist's last section). Say what content each flaw is buying.
5. Say what the problem IS (theme, phases, changes) in two lines, then the flaws, then the pluses. No
   praise before the flaws. Give the FEN and draw the board.
   Every post that names a position shows it as a diagram (`python tools/show.py <name> "<FEN>"`,
   sent as an image, with the bench link), not only as a FEN: E. Bourd, session 29, "please keep showing diagrams when posting".
6. If a repair is obvious (one unit), test it with the solver and report it as verified, not proposed.
7. Describe choices, do not bless them. Say what a choice achieved and what else could have done the job;
   never call it "right" because it worked. E. Bourd (session 29), on "using self-blocks twice was right":
   "It worked. Not that it was right, many other things could be 'right' as well. And if not I'll change so
   it was wrong?!"
8. Official solution vs notes (E. Bourd s30): the published solution shows what is needed - set play, tries,
   key, variations, theme - and may leave out minor flaws (an unthematic dual, a passive king, a provided
   flight). Keep those in our own notes or the mentor issue. Major flaws are never hidden.
