# Composing principles, as taught by Evgeni Bourd (IM, FIDE)

Living document. Each principle is linked to the tool rule that implements it (or "not yet").

## Judging a #2 (session 1, Sept 2026)

| Principle | Weight | Tool rule |
|---|---|---|
| A king escape (flight) available in the diagram makes the problem easy to solve | big flaw | `king escape in diagram` |
| A try refuted by a king move is pretty bad | big flaw | `king refutes try` |
| The same refutation for several thematic tries is bad | big flaw | `same refutation` |
| Every White piece should take part in the mates; the key piece is forgivable | flaw | `passive piece`, `cook-stopper`, `superfluous piece` |
| No obvious Black defence that has no answer, or the solution becomes trivial | flaw | `unprovided move` (partial) |
| Simple defences (pawn moves opening lines for the king) are weak: they defend against anything and help the solver. Heavy pieces moving and leaving squares are better | preference | not yet (defence-motive classification) |
| Economy and an airy position are valued, but aesthetics yield to content as ideas get richer | balance | `economy` |
| A natural, game-like look adds points | plus | not yet |
| Long moves, paradoxes, thematic play and geometric manoeuvres are valued; more so when doubled or tripled | plus | `long key`, `theme` |
| Value = balance of thematic depth, novelty, complexity against the cost in pieces/aesthetics | judgement | not yet |
| Too simple + big flaws = not worth it, even if economical | judgement | not yet |

## How a #2 is built (session 1)

1. **Choose the thematic line** and place the Black king where the mating piece has many options
   (a central king gives the queen more mates).
2. **Choose the mates**: e.g. queen mates from the corners (Qa8, Qh1) look nicer; mates from other
   squares are fine if they serve another theme.
3. **Start with simple defences** (e.g. pawn moves d4, f2 opening the queen's lines). Weak in the final
   judgement, but easy to set up while exploring.
4. **Pick the threat square** (e.g. Qe5 vs Qd4): prefer the one that lets a Black move become a defence.
5. **Close holes**: notice recurring unwanted mates (e.g. d3 mates in many places, Qd3 intrudes) and
   remove them to finish a prototype.
6. **Refine**: make defences more interesting (heavy pieces leaving squares), add tricky tries on the
   thematic line (e.g. B to f6/g7/h8, each blocking something: f6 blocking a knight mate, g7 cutting a
   rook's path), rotate/reflect the board if pawns must move the other way.
7. **Check**: every piece optimal and participating; no obvious unanswered defence.

## Themes taught

* **Bristol**: a line piece moves along a line; another piece follows on the same line in the same
  direction, passing the vacated square and stopping short. Extended by thematic tries in which the
  line piece stops on other squares that block something else. (`bristol()` detector)
* **Pickabish**: (keyword on Variantim 2015): the bishop's choice of square, shown by tries. Definition to be
  confirmed by the composer.

## Session 2 (Sept 2026): feedback on the Bristol prototype

* Leftover pieces from earlier experiments must be removed (bPe6 was left from tries against Qf5 / back-rank
  mates). Tool: removal test flags pieces whose removal changes nothing.
* **A piece can be essential for the thematic tries even if soundness doesn't need it** ("the same mate in 2,
  but a problem without its soul"). Necessity must be judged against the *content* (tries, variations),
  not only against the key. Tool: TODO, compare tries/variations after removal, not just keys.
* Unified defences are a plus: both defences opening lines, giving a symmetry.
* The key piece not taking part in any mate IS a flaw (forgivable, but a flaw).
* A king on the side is slightly annoying; placing it more actively risks extra queen mates. Accepted
  compromise when no role can be found.

## Session 2: new idea: rook vacates d5, threat Sd5# (Rd5, Sb6 vs Kf4)

* Tries should have **uniform gameplay**: the same mechanism across tries is more interesting than
  isolated events. The more the theme recurs across tries and variations, the more dominant and evident.
* Suggested mechanism: **line closing for White**: the rook's wrong squares cut a White line, leaving
  something unguarded.
* My analysis: against a knight check on d5, Black can only guard d5, capture the knight, or make a flight.
  A White line cut helps Black only if that line was a **pin**: the rook interposes on a pin line and
  **unpins** a Black piece, which then refutes. Three pin lines through f4 cross the rook's squares:
  4th rank (Rd4), diagonal c1-f4 (Rd2), diagonal b8-f4 (Rd6).
* Structural lesson: a pinned piece on e5 is attacked by the rook on d5 itself (capture keys Rxe5 keep
  appearing) and blocks the rook's path along the 5th rank. The e5 pin is the wrong one.
