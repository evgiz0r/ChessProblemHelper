---
name: bench
description: Read back Evgeni's Composing Bench journal (the artifact database) and reconstruct what he did - sittings, ideas, solves, dead ends, the moment it worked. Use when he says he composed on the bench or asks what he did.
---

# Read the bench journal

The bench is the artifact "Composing Bench" (https://claude.ai/code/artifact/acc24a96-d9f6-4076-98a9-7915ed586916);
its database collection `journal` holds one document per step: `{session, n, t, action, detail, fen}`.
Actions: place, move, remove, undo, clear, refresh, rotate cw/ccw, mirror, shift, back to, note, solve,
findkey. Old entries (7-10 Oct 2026) may also hold `theme` (a removed box for the thematic defences),
`look`/`lookup`, from a look-up feature (playing
legal lines from the diagram) and a "key check by unit" option; he never used them and both were removed on
10 Oct 2026 ("not sure what it is, probably a mistake"). Do not add bench features he has not asked for.
Solve details start with the verdict (COOKED / Key / No solution), then threat and holes, then tries.

1. Read the documents newer than the last session you know of with `read_db` (query on `t`, `out_dir`
   to save them), then condense: keep solves, notes, look-ups, transforms and clears; single piece moves
   are the fine grain of his search (what he tried and took back), so count them and read them where a
   sitting turned.
2. Split by `session` id; each is one sitting. For each sitting: start position, ideas in order (the
   FENs at each solve), what each solve reported, where it stopped and why.
3. Re-solve the final and the turning-point positions with the Python solver; the journal line is the
   bench's JavaScript solver (same keys, less critique) and it was truncated in early sessions.
4. Draw the stages as boards; write the story in his terms; record the finished problem with `record`.
5. Read the process, not only the result: sittings that ended nowhere, transformations that only made
   room, the change that supplied the reason, how many solves it took.
6. Timestamps are not thinking time (E. Bourd, 8 Oct 2026): he composes between food, family and errands, so a
   gap between two steps is usually a break, not deliberation. Count steps and solves, not minutes; never
   report a sitting's length or a pause as effort, and never infer that a step was hard from the gap before it.

While working on anything (E. Bourd, 24 Oct 2026, in general, not only in one session): query the journal for steps
newer than the last one read before each solve batch and before each answer. If he advanced, build on his newest
board and say what you took from it (his 1.Bf2! came on the bench while Claude was still searching his older board).

Transforms respect pawns (session 29): with pawns on the board a rotation or the up-down mirror is made with
a warning naming the pawns to re-place (fine for cook-stoppers and blocks, undo when a pawn move is
thematic; pawns landing on rank 1 or 8 are named as illegal). An up/down shift that puts a pawn on rank 1
or 8 is refused, and one that gains or loses a double step is made with a warning. Left-right shifts and the
left-right mirror always work.
