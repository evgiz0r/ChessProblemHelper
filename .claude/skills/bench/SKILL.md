---
name: bench
description: Read back Evgeni's Composing Bench journal (the artifact database) and reconstruct what he did - sittings, ideas, solves, dead ends, the moment it worked. Use when he says he composed on the bench or asks what he did.
---

# Read the bench journal

The bench is the artifact "Composing Bench" (https://claude.ai/code/artifact/acc24a96-d9f6-4076-98a9-7915ed586916);
its database collection `journal` holds one document per step: `{session, n, t, action, detail, fen}`.
Actions: place, move, remove, undo, clear, refresh, rotate cw/ccw, mirror, shift, back to, note, solve.
Solve details start with the verdict (COOKED / Key / No solution), then threat and holes, then tries.

1. Read the documents newer than the last session you know of with `read_db` (query on `t`, `out_dir`
   to save them), then condense: keep solves, notes, transforms and clears; drop single piece moves.
2. Split by `session` id; each is one sitting. For each sitting: start position, ideas in order (the
   FENs at each solve), what each solve reported, where it stopped and why.
3. Re-solve the final and the turning-point positions with the Python solver; the journal line is the
   bench's JavaScript solver (same keys, less critique) and it was truncated in early sessions.
4. Draw the stages as boards; write the story in his terms; record the finished problem with `record`.
5. Read the process, not only the result: sittings that ended nowhere, transformations that only made
   room, the change that supplied the reason, how many solves per minute.
