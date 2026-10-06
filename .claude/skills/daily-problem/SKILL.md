---
name: daily-problem
description: Compose, judge and publish the daily #2 on the blog (docs/blog), act on the mentor's answers, then review the run and make one improvement to the kit. Use when the daily routine fires, or when asked for today's blog problem.
---

# The daily problem

One run = one published twomover + one lesson + one improvement to the kit + questions for the mentor.
The point is not only the diagram: every run must leave the composer (tools, skills, knowledge) a little
better than it found it, and say so. Budget about three hours of wall clock; check `date` at each stage.

## 0. Setup (10 min)
- `pip install -q --use-pep517 -r requirements.txt` if `import chess` fails.
- Read `CLAUDE.md` (the constitution), the `compose`, `judge` and `stop-cooks` skills,
  `knowledge/bourd_principles.md`, the last 40 lines of `knowledge/lessons.jsonl`, and the last five entries
  of `knowledge/daily_log.md` (what earlier runs said to try next, and the open proposals).

## 1. The mentor first (15 min)
Open GitHub issues labelled `mentor` on evgiz0r/chessproblemhelper are questions from earlier runs. Read them
with the GitHub MCP tools if the session has them, otherwise with the built-in client, which works in
routine sessions:
`gh api "repos/evgiz0r/chessproblemhelper/issues?labels=mentor&state=open"` and
`gh api repos/evgiz0r/chessproblemhelper/issues/<n>/comments`. For each
one where Evgeni (evgiz0r) has answered and no later comment of ours says "Acted on":
- Turn each answer into knowledge: a line in `knowledge/lessons.jsonl` (source "E. Bourd, mentor issue #N"),
  a principle in `knowledge/bourd_principles.md` if it is general, a critique rule or a skill line if it is
  checkable. If he contradicts a rule we hold, his word wins: change the rule and say where.
- Add a one-line summary to the `feedback` list of the post the issue belongs to.
- Reply on the issue once: what changed, with the file names (and the commit after step 8), starting
  "Acted on:". Close the issue when every question in it is answered. Never nag about unanswered ones.

## 2. Theme (2 min)
`python tools/blog.py next-theme` gives the theme used least recently, with its definition, the kit's
reference and the archive label. Take it. A `stretch` theme is attempted in its full form only if a sound
simpler form exists first; otherwise publish the simpler form and say so.

## 3. Study (15 min)
- Read the reference. If the theme has none, the improvement of step 7 is to write one.
- Read three light archive examples: `python -m chesscomp.db list --stip '#2' --orthodox --text "<db_text>"`,
  then `show <id>`; re-solve the lightest with `python -m chesscomp.report --fen "<FEN> w - - 0 1" "#2"` to
  see the mechanism in our own terms.
- Write the mechanism in one sentence (the black effect, the squares, the reason each thematic move
  defends) before placing a piece. Never copy a matrix: change its geometry, its pieces or its content.
  The gate rejects an identical or mirrored archive position.

## 4. Compose (90 min)
Follow `compose`: mechanism, box, reason for the key, defenders, cleaning, trimming. One change per solve.
Shrink before you grow. Use the machine for the last layer only:
`chesscomp.compose.pattern_search` (any pattern the solver detects: Dombrovskis, Le Grand, changed mates;
PURE=1, several DEF, MODE w1|w2|w1b1|w2b1|m1) and `chesscomp.compose.kernel_search`. Keep counts as you go:
solves, kernels tried, searches run, minutes.

## 5. Gate and judge (15 min)
- `python tools/blog.py check "<FEN>"` must print `GATE: PASS`. Fatal: unsound, cook, promoted force,
  unprovided check in the set play, checking key, dual in a thematic variation, a major diagram flight,
  anticipation (same or mirrored position in the archive or on the blog). Nothing else may override it.
- Then the `judge` skill: flaws first, in his order. Every gate warning appears among the post's flaws, or
  "What it is" says why it is not one. Claim a theme only if the solver's report shows it where a detector
  exists (Patterns, Changed continuations, the S~ correction lines).
- Fallback, in this order: a sound simpler form of the theme (fewer variations) is a normal post that says
  what it lacks. If nothing passes the gate, publish a study post: an archive problem of the theme with full
  credit, titled "Study: ...", author and source as printed, and a comment on why today's attempt failed.
  Never publish a cooked or unchecked diagram.

## 6. The post (15 min)
Write `blog/posts/<date>-<slug>.json`, copying the structure of the latest post (fields in the docstring of
`tools/blog.py`). Title: short and not naming the key. Teaser: what to look for, no spoilers. Solution in the
card format (`#Tries`, `#Key`, two spaces before a variation, letters A/B and a/b where they help). Comment:
what it is (two to four sentences), every flaw, the pluses, how it was made (dead ends included), and one
lesson, which also goes into `knowledge/lessons.jsonl`.
Mentor questions: one to three, each answerable in a line, about something the run could not settle by
itself: taste, conventions, whether a flaw is acceptable, which of two versions is better, whether a rule
we follow is right. Never quiz questions, never questions the solver can answer.

## 7. Self-review and one improvement (30 min)
Append an entry to `knowledge/daily_log.md`: theme, result, minutes per stage, what wasted time, what tool
was missing or wrong, what the next run should try. Then make ONE improvement to the kit and test it:
a faster or smarter search, a new detector or critique rule, a fix, a theme reference that was missing, a
clearer skill line. Constraints: `python -m pytest -q tests` passes; a change to `chesscomp/analysis.py` is
mirrored in `docs/analysis.js`; a solver or critique change gets a regression test; the gate's fatal list
changes only on the mentor's word. Too big for 30 minutes: write it under "Proposals" in the log and ask
about it in a mentor question. Summarise the change in the post's `improvement` field.

## 8. Publish (10 min)
- `python tools/blog.py build`, run the tests, commit "Daily No. N: <title>", push to `main` (retry on
  network errors: 2, 4, 8, 16 seconds).
- Open the mentor issue (GitHub MCP `issue_write`, or
  `gh api repos/evgiz0r/chessproblemhelper/issues -f title=... -F body=@issue.md -f 'labels[]=mentor'`;
  reply with `.../issues/<n>/comments -F body=@reply.md`, close with `-X PATCH .../issues/<n> -f state=closed`):
  title "Mentor questions: No. N (<date>)", label `mentor`, body with the post link
  `https://evgiz0r.github.io/chessproblemhelper/blog/<slug>.html`, the FEN, the questions numbered, and the
  attribution footer. Put its number in the post's `mentor_issue`, rebuild, commit, push.
- End with three lines: the post link, the issue link, the improvement.
