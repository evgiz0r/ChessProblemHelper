# Pictures of the formats, and where Claude's geometry really fails (6 Nov 2026)

Follow-up to `board_views_2026-10-09.md`, at E. Bourd's request: "once in a while claude was reasoning really bad around
some position missing very simple geometric relations like diagonals or attacks, or knight moves. can we see how these
intuitively help around some of those ... Maybe you can ask to draw a picture, for visualizing those formats." His
framing during the run: "the board itself contains diagonals, the rest [are] some kind of graphs or smaller graphs";
and after round 1: "maybe we should limit the reasoning, to feel the intuition. Or spam the agent with many positions."

Files: `tools/board_pictures.py` (the pictures, test `tests/test_board_pictures.py`); scripts, cases, sealed keys, every
answer and score in `board_pictures_2026-11-06/` (`harness.py` round 1, `harness2.py` round 2, `harness3.py` round 3;
paths inside point at the session's scratch folder). Cards: `docs/blog/cards/views-example-pictures.png`,
`sight-test-A.png`, `sight-test-A-rays.png`, `intuition-P11.png`, `intuition-P11-rays.png`.

## The pictures
The text views drawn on the board (`python tools/board_pictures.py "<FEN>" out.png all`):
- **plain**: the diagram. Every line is there, implicitly: a diagonal has to be traced square by square.
- **rays** (= `annotated`): each line piece's lines of sight to the first unit, a dashed continuation behind it (x-ray),
  knight jumps and pawn captures as short lines. White blue, Black red.
- **arrows** (= `relations`): the attack graph, an arrow from every unit to every unit it attacks or defends.
- **field** (= `kingzone`): the black king's field shaded by the number of White guards, flights yellow.
In his words: the board holds the lines; the other views are graphs (arrows) or smaller graphs (field) drawn over it.

## The cases
Real misreadings with a recorded position (a scan of ten chat transcripts found no further geometry corrections by him):
- A `3N1r1B/3R4/2P2q2/1K1pnp2/3k1p2/3B2p1/3PQ3/8` (session 3 sight test): "Bc4 checks the king on d4" (a rank),
  set "1...Q~ 2.Bc4#", missed 1...Qd6 2.Qd3#.
- B `b2R4/b6p/8/N2pPQ2/2Npp2R/1pPk3P/1Pp5/2n2KB1` (his half-battery, session 11): missed the pin of Pe4 by Qf5.
- C `8/1N2K1B1/2p5/2pk4/Q7/3P4/3N4/2r1n2b` (12 Oct): cooked by queen checks with a pawn recapture next to the king.
- D `1B6/2Q3p1/1P5N/1p2rp2/1N1k1P2/5K2/5P2/8` (29 Oct): "2.fxe5 is a check" against Kd4.
- Session 18's missed queen mates in one were never recorded with a position; four post-key positions of our
  problems (White to move again, so the threats are mates in one) stood in for them in round 1.

## Round 1: list everything (normal effort, 8 positions, 7 views)
Checks, mates in one, pins, Black's captures. Every view 100% on every probe, except arrows-picture checks 96% (missed
Qxe4+ in B). Nobody repeated Bc4 or fxe5, nobody missed the Pe4 pin or the queen mates. But each subject spent 7-10
minutes and 115-135k tokens: asked to enumerate, Claude sees correctly from any format, FEN included. A ceiling, as on
9 Oct; the old errors were not a reading limit.

## Round 2: solve by sight (normal effort, the four real diagrams)
Key, threat, every defence with its mate, set play; python-chess judged every claimed mate.

| view | keys | claimed mates | mate | only check | not even check | defences found | time |
|---|---|---|---|---|---|---|---|
| FEN | 4/4 | 53 | 49 | 4 | 0 | 19/19 | 15 min |
| annotated text | 4/4 | 46 | 44 | 2 | 0 | 18/19 | 17 min |
| rays picture | 4/4 | 40 | 37 | 3 | 0 | 18/19 | 23 min |
| FEN + "draw it yourself" | stopped after 31 min, no answer | | | | | | |
| plain picture | stopped after 31 min, no answer | | | | | | |

Every false mate was a check with an escape the reader did not see, and every one came from what the moving piece
changed on leaving its square, never from a misread line:
- FEN, P4 (bourd-grimshaw-d5-7x7): 1...Rxc4 2.Qe5/2.Nf5 - the c5 rook leaving opens the 5th rank for bRa5 (Rxe5, Rxf5);
  set 1...Re5 2.Qxe5 likewise. The mate is 2.Qxc4#.
- annotated, P4 set: 1...Bb7/1...Ba8 2.Qe4 - the bishop slides along its own diagonal and still guards e4.
- rays picture, P1 set: 1...Qf7/Qxd8/Qg6 2.Qxe5 - the queen leaving e2 drops the guard of Bd3 (2...Kxd3); the mate is 2.Bxe5#.
- annotated and rays picture missed 1...Qd6 (interposing on the d-file unpins d5), the defence Claude missed by hand in
  session 3: two of three readers repeated the historical miss.

## Round 3: intuition (low effort, 40 positions, 120 "does 1.X give check?" claims, half of them copies of the old errors)

| claim type | FEN | grid | annotated | plain picture | rays picture |
|---|---|---|---|---|---|
| false: bishop next to the king on its rank/file | 14/14 | 11/14 | 13/14 | 13/14 | 13/14 |
| false: rook diagonally next to the king | 9/9 | 9/9 | 8/9 | 8/9 | 9/9 |
| false: blocked line, knight near the king, pawn next to the king, other near squares | 39/39 | 39/39 | 39/39 | 39/39 | 39/39 |
| true: discovered check | **4/8** | 8/8 | 8/8 | 7/8 | 8/8 |
| true: long line | 13/14 | 14/14 | 14/14 | 14/14 | 14/14 |
| true: knight, capture, near | 36/36 | 36/36 | 36/36 | 36/36 | 36/36 |
| **total** | 115 | 117 | 118 | 117 | **119** |
| time | 38 s | 45 s | 49 s | 92 s | 124 s |

- **The board formats reproduce the Bc4 error exactly**: a bishop or rook landing on the square next to the king, on the
  wrong kind of line, is called check (every false "yes" had the piece adjacent to the king). P11
  (claude-bench-two-knights-e4-se2, 1.Bd4 next to Kd5) fooled four of five readers; only FEN said no. On a board,
  contact is seen at once and read as attack; in FEN the line must be worked out, and was.
- **FEN misses discovered checks** (4 of 8): the line through the moving piece is invisible in a string.
- No reader ever invented a check from a distance or through a blocker (15 blocked-line traps, all answered correctly).
- The rays picture was best and slowest. n is small (40 positions, about six distinct error positions); the totals differ
  by 1-4 answers. What repeats is the error type per format.

## Round 4: the move-change view (7 Nov, low effort, 40 claims "1...X 2.Y - mate?")
New `tools/move_delta.py` (test `tests/test_move_delta.py`): for one move, the lines it opens and closes, what the moving
piece drops, gains and keeps next to the black king, the guards its side loses altogether, pins made and broken, flights
gained and lost; as text, and as a picture of the board after the move (thick line = opened, dashed = closed, orange
cross = guard lost, green ring = guard kept, yellow = new flight). Claims from our problems' set and post-key play: 20
true mates, 14 generated traps whose only escapes come from a departure effect (opened 8, kept 6, dropped 6 over the 20
traps incl. the real ones), and the six real round-2 errors. Script, key and answers in `board_pictures_2026-11-06/round4/`.

| | FEN | plain diagram | boards after both moves, nothing drawn | move-change text | move-change picture |
|---|---|---|---|---|---|
| true mates | 16/20 | 11/20 | 16/20 | 20/20 | 20/20 |
| the six round-2 errors | 3/6 | 4/6 | 3/6 | 6/6 | 6/6 |
| generated traps | 1/14 | 4/14 | 12/14 | 14/14 | 14/14 |
| total | 20 | 19 | 31 | 40 | 40 |
| time | 6 s | 56 s | 144 s | 7 s | 52 s |

- **At first impression a two-move claim is a coin flip** from FEN or the diagram; the FEN reader said "mate" 32 times
  of 40: a check that looks like mate is taken for mate (the "2.Bc4#" of session 3).
- **Seeing the boards after the moves** (the control) lifts it to 31: half the failure is playing the moves in the head.
- **Drawing or writing what changed** lifts it to 40. The control still accepted all three "rook behind" false mates
  of bourd-grimshaw-d5-7x7 (1...Rxc4 2.Qe5/2.Nf5, set 1...Re5 2.Qxe5) with the board after 1...Rxc4 in front of it;
  the thick red line of the a5 rook through c5 is what the move-change picture adds.
- Caveat, a leak by design: the traps were chosen by exactly the effects the view reports (an opened line reaching the
  mating square, a flight gained, a guard kept), as `relations` gives away captures. The 40/40 shows the facts decide
  the claim and are read in seconds when shown; it does not show the view finds a reader's blind spot unprompted.

## Conclusions
1. Asked to enumerate, Claude reads any format correctly (round 1, and 9 Oct). The errors live in quick reading and in
   fluent analysis.
2. Quick reading has two format-specific blind spots: **contact** (board formats: a bishop/rook adjacent to the king
   taken for a check) and **discovered lines** (FEN). Drawing the lines (rays) reduces both.
3. In analysis the misses are **departure effects**: a line opened behind the moving piece, a guard the moving piece
   drops, a slider that moves along its own line and keeps its guard, an interposition that unpins. The static board was
   read correctly every time. This is the 9 Oct backlog's top item, a view of what a move changes; no format tested here
   provides it.
4. The move-change view now exists (round 4): shown the change, a reader at first impression gets every claim right
   that it otherwise gets at chance. Its practical use is as a checker with reasons: before claiming 1...X 2.Y#, run
   `python tools/move_delta.py "<FEN>" "X Y"` (or the solver, which is exact) and read what each move opened and dropped;
   in composing, the same lines name the cause of a failed mate (cause -> remedy), which the solver does not.
5. Practice for this repository, alongside it: before claiming a check or mate by hand, name the line of a
   line piece next to the king; for each claimed mate, ask what the mating piece stopped guarding and what its departure
   (and the defence's departure) opened; then solve.

## Process notes
- Subjects were general-purpose subagents given one prompt file (and pictures); tool use audited from the logs (text: one
  read; pictures: one read per picture). All clean. Keys were kept in a folder the prompts never named.
- Round 2's two unanswered subjects were stopped 10 minutes after the 20-minute watchdog (the session was attended and
  their logs showed one long reasoning pass, not a stall); counted as missing data.
- Cost: about 3.1 million subagent tokens over the four rounds (round 1 ~0.85M, round 2 ~0.9M incl. the stopped ones,
  round 3 ~0.45M, round 4 ~0.53M).
