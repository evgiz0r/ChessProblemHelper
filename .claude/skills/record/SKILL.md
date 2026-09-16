---
name: record
description: Write what a session learned into the repository so the next session starts with it - problem collection, lessons, session log, principles, tests - and push. Use before ending any composing or judging session.
---

# Record a session

1. `knowledge/problems.json` (and the identical `docs/problems.json`): every position worth keeping, with
   id, FEN, author, themes, a note that says what it is and what is wrong with it, the solver output, the
   key(s). Rejected positions stay, marked rejected with the reason.
2. `knowledge/lessons.jsonl`: one line per generalisable fact: `{date, source, topic, kind, text,
   example}`; dead ends are lessons too (kind: negative result).
3. `knowledge/session_log.md`: the story of the session, including what failed and why.
4. Fold anything that changes how to compose or judge into the skills' references (compose, judge,
   stop-cooks, themes), not only into the raw files; a session reads the references at the moment of use
   and the raw files only on lookup. Sessions with more than a handful of lessons: consolidate now.
5. Anything that can be tested goes into code: a critique rule, a search filter, a regression test in
   `tests/test_regression.py` (every stored key is re-solved). Run `python -m pytest -q tests`.
6. Commit with a message naming the session and push to the working branch.
