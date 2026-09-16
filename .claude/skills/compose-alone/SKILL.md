---
name: compose-alone
description: Compose a #2 without a human in the loop - pick or take a theme, build, judge, repair, trim, and leave the result with its verdict in the collection. Use when asked to compose alone, as a routine, or to test the entity.
---

# Compose alone

Load `compose` and `judge` first. Then:

1. **Theme.** Use the theme given; otherwise pick one from `themes` that is not yet done well (the
   references say what is open). State the theme, the Black effect, the reason the defences will
   defend and the reason for the key, in four lines, before placing a piece.
2. **Kernel.** Hand-build the boxed king, the mechanism and the key. Solve. Iterate one change per solve
   until the kernel is sound (unique key, no duals). Budget: 20 solves. If the pre-key solve keeps
   returning only checking tries, restart from a different geometry (once).
3. **Defenders.** Run `kernel_search` around the sound kernel (1 Black; then 1 White + 1 Black; 2 Black),
   `BUDGET_S=300 JOBS=4`. Take the hit with the most distinct mates; tie-break by fewer units.
4. **Clean and trim** with `stop-cooks` and the critique's necessity check. Count the force.
5. **Judge** with the checklist; write the verdict as Evgeni would, flaws first. If a fatal flaw remains,
   say so and stop repairing after three attempts; a recorded failure with its reason is a result.
6. **Record** with `record`: the problem (or the best failed attempt, marked), the lessons, the session
   log line, then commit and push.

## Budgets are hard limits
An unattended run has a wall clock of 20 minutes and 45 tool calls; whoever launches it arms a watchdog
(a background timer that ends the run) because the agent tool has no timeout of its own. Reason in at most
three sentences between tool calls; append one line to a notes file after every solve so progress is
visible from outside. The first unattended run made one tool call in 27 minutes and hit its output limit
thinking: that is the failure mode these limits exist for.

Never show or record a position you have not solved in this session. Never add a promoted piece to
fix a cook. Prefer fewer units over an extra variation of the same mate.
