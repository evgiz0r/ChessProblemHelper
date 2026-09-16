# ChessProblemHelper - read this first

Evgeni Bourd (IM for chess compositions) is teaching an AI to compose #2 problems. Nothing learned in a
session survives except what is written into this repository. Before composing or judging anything:

1. Read `knowledge/bourd_principles.md` end to end. It is his judgement, in his words, consolidated per session.
2. Skim `knowledge/lessons.jsonl` (one JSON object per line: topic, kind, text, example FEN). These are
   the specific, solver-verified facts, including dead ends. Do not repeat a recorded dead end.
3. `knowledge/session_log.md` has every session's story; `knowledge/problems.json` every position with its
   solution and critique (`docs/problems.json` is the copy the web page reads; keep them identical).

## Hard rules he has given (fatal flaws)

- Build around a boxed black king; a flight in the diagram is a flaw, a flight-giving key is a plus.
- An unprovided check in the set play is fatal.
- A promoted piece in the diagram (3rd knight or rook, 2nd queen, two bishops of one colour) is fatal
  unless the idea cannot exist without it. Count the force before showing a position.
- Every claim about a position goes through the solver first:
  `python -m chesscomp.report --fen "<FEN> w - - 0 1" "#2" --critique`. Hand analysis has been wrong
  every time it was not checked.
- Mating squares and lines close to the king; every White line piece near the king adds checks and cooks.

## How to work with him

- Iterate at the composer's level: cause -> remedy -> verify, one small change per solve. Do not launch an
  enumeration per micro-question. The kernel (mechanism, box, reason for the key) is hand work; only the
  last layer (defenders around a sound kernel) is for `chesscomp.compose.kernel_search`, run in parallel
  with a time budget, never a long sequential chain.
- Draw boards as SVG images with every diagram and give the FEN with each.
- Be direct and critical, like a judge. He wants flaws named, not praise.
- Record everything generalisable: a lesson line, a session-log entry, the problem in `problems.json`,
  and a regression test (`tests/test_regression.py` re-solves every stored key).
- The Composing Bench (an artifact with a journal in its database) is where he composes; its journal can be
  read back to reconstruct his process. Journal solve lines start with the cook/key verdict.

## Layout

`chesscomp/` solver, analysis, motives, critique, compose tools. `knowledge/` everything learned.
`docs/` the web page and its JS solver (`analysis.js` mirrors `chesscomp/analysis.py`; a fix in one goes
into the other). `tests/` regression.
