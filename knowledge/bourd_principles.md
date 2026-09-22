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

## Sessions 18-19 (Sept 2026): changed mates, and how to iterate

Taught while composing five changed-mate problems (see `problems.json`: bourd-changed-mates-3/4,
bourd-one-knight-change, bourd-selfpin-changed-mates-2, and the Claude settings judged alongside).

### Construction order for a change
1. Choose the squares and the Black EFFECT that creates several mates at once: a self-block usually;
   closing a line, opening a line, unguarding several squares do the same job. A self-pin by capture is
   an effect too (the pinned unit can neither capture the mating piece nor interpose).
2. Choose the DIFFERENTIATION: which of those mates each phase allows. Selectors seen: the mating squares
   are guarded by Black pawns and each first move removes one guard (Bxb4/Bxe7); the queen's post holds one
   pair of squares per phase (a5 vs d2, g5 vs f6); the key piece gives the set mates itself and switches
   them off by moving while its arrival protects the new square (Se8-c7); the key that moved just does
   the other mate (Qg5-f6, Sxd4 Qe3 -> Qxd4).
3. Only then a threat that the thematic defences parry, and cleaning.

### Hard rules (fatal or near-fatal)
* Build around a king WITHOUT escapes. A diagram flight is structurally hard: every escape must be
  answered in every phase. The same enumeration that needed 10 units with a flight gave 6-unit hits without.
* An unprovided CHECK in the set play is fatal. Ordinary unprovided moves are a blemish.
* Mating squares and their lines close to the king; a Grimshaw square near the king, lines crossing there.
* A pinner on the rank + a White pawn on the pin square + a queen nearby = a discovered-check cook
  (1.d5+ with the pinner protecting d4). Give Black the blocker before anything else.

### Stopping cooks, and what a refutation means
* Stop a cook by giving Black a resource that lives only in the cook's line (a knight that can block the
  discovered check on c4), not by weakening White (that breaks the mates).
* If that resource also refutes the intended key, INVERT: the intended key becomes the try, the other move
  the key (1.Sc7? Sc4!, 1.Qh5!). A try whose play equals the set play still shows the change on its own.
* Test removals in pairs before calling a unit superfluous (bPg6 and bPh4 each removable alone, not together).
* Necessity is judged on content in every phase: a unit that only plays a try carrying changed mates is
  thematic, not a cook-stopper.

### How to iterate (process, from Evgeni's feedback)
* Cause -> remedy -> verify. The solver verifies a claim already made; it is not a generator.
* When the solver reports a cook, name what makes it work, then pick from the remedy list above.
* Enumerate only for PLACEMENT, after the mechanism and the selector are fixed on paper; a search family
  never produced a decision this session, only confirmed one.
* Reuse ideas and the search process, not structures: the same solution appears in other directions -
  rotate, reflect, move pieces, respect the constraints of the position.
* Claude's board sight is unreliable (asserted "no mate in one", solver found three, twice). Every step is
  checked, and the check is cheap.

## Session 20: the reason for a defence (from Evgeni's bench journal)

Evgeni composed a two-capture self-pin problem on the bench and said afterwards that the issue was
"finding a reason why the thematic moves are defenses". The journal shows what that costs and what
solved it:

- A scheme with a good mechanism (two Black pieces capturing on e4, a rank pinner, knight mates) is not a
  problem until the captures STOP something. Rotating, shifting and re-posting the queen around such a
  scheme for 45 minutes gave threats with holes, double threats, or no threat - never a reason.
- The reason came from a line geometry: put the threat piece (the queen) and the White king on the
  extension of the capture line (e8-e4-e2-e1). Then every capture on e4 pins the queen, which is why the
  threat 2.Qd3 fails; the same capture self-pins the capturer against the rank rook, which is what the new
  knight mates use. One Black rook was changed into a queen so both captures reach e4 from different lines
  and both land on the pinning file.
- The set mates come from the key piece (Qh5: Qe5#/Qd5#), which moves to e2 and switches them off -
  the same shape as bourd-one-knight-change and the self-pin problem of session 19.
- Finishing is a short loop of pre-key solves: cook by promotion -> remove the pawn; two keys with the
  same threat -> give Black a capture on the unwanted key square (Bh1 -> Bxf3!) which makes it a try; dual
  after a side defence -> a Black pawn guarding the dual square. Each fix took under a minute once the
  solver named the flaw.
- Last step, which he skipped: remove pieces and re-solve. bRh4 and the Rf4 shift were unnecessary.
- Process rule: after a few solves without a reason for the defences, clear and rebuild from the idea. The
  fresh sitting took 33 minutes; the rotated one took 45 and ended nowhere.

### What the journal taught about tempo (session 20, Claude's reading of Evgeni's process)

- Reasons a capture defends, to check at scheme time before any solving: it pins the threat piece
  against the White king (this problem); it removes a guard the threat mate needs; it opens a Black line
  to the threat's mate square; it closes a White line; it guards the mate square itself. If none of these
  is available for the capture square, no queen post will make the captures defences.
- The signal that a structure is empty: a pre-key solve returning only checking tries (no quiet move
  threatens anything), or post-key solves that change between "double threat", "holes" and "no threat"
  across four or five queen posts. That is not a flaw to fix; the geometry has no line to exploit.
  Rotation and shifting preserve the geometry, so they cannot supply it - they only make room.
- The signal to keep playing: the solve names one thing (one cook with a line, one hole, one dual, one
  double threat with a nameable second square). Each has a one-unit remedy and costs a minute.
- Tempo: one solve per minute; sixteen minutes of placing without solving produced nothing.
- The White king is a construction resource, not only something to hide from checks: behind the threat
  piece on a line it turns captures on that line into pins.

## Session 24: weighing flaws against content

Evgeni's four-promotion problem 5K2/3P4/1N2p3/1P2k1NP/1P4P1/3p4/3B4/8 (1.d8=Q? stalemate, 1.d8=B? Kd4!,
1.d8=S? Kd6!, 1.d8=R!) has three diagram flights, a flight-taking key, king-move refutations and one
king-flight variation. His judgement: the theme is tripled, and that balances flaws that would be fatal
in a simple problem; clean and simple is usually considered worse than complex with some flaws, though
that is somewhat subjective. For composing: doubling the theme buys tolerance; economy alone buys little.

## Session 25: he hands over a scheme, not a theme

Asked for a key that gives two flights, Evgeni put three units on the bench (bK d5, bP e5, wS c5) and
said "use the scheme on my board now, Se4 will give two flights". The scheme names the key move and the
flight squares and leaves everything else open. Working from it reached a sound position in one sitting
where a day of abstract searching had not: the composer's part is the mechanism and the key move; the
builder's part is mates, threat, cooks. Result: claude-two-flight-knight-sacrifice (13 units, thin).

## Session 27: draw the diagrams so we understand each other

Two messages of prose about a cooked scheme got "what's up"; four board images with arrows (the
cell, the random mate, and one board per structural dead end) got "not bad, finally got somewhere".
When the discussion is about a mechanism, post a board per idea, with arrows for the moves that
matter, and keep the prose to one line under each. A FEN is for the solver; a picture is for him.
Also: he asks for the session review while he is still composing on his side. Write the record
(lessons as rules, session log, themes reference) as soon as a pass ends, not when the problem is done.

## Session 27: start small, keep it light, then extend

"I started small, and if my mechanism is light enough, I have the freedom to try and extend something.
More content. Not always possible of course, but if your original structure is heavy or too rigid, or
too dependent on very specific flights, it may be hard to extend." His bench journal shows it: a random
move and one mate on three units, the threat added, "that's 1 option", cleared and rebuilt as option 2,
a second correction with a different mechanism, then cooks and economy last. Extension is a property of
the mechanism, not of the position: a structure where every flight is covered by exactly one unit has no
slack. Judge a kernel by how much can still be added to it.
