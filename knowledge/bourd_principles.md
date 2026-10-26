# Composing principles, as taught by Evgeni Bourd (IM, FIDE)

Living document. Each principle is linked to the tool rule that implements it (or "not yet").

## Judging a #2 (session 1, Sept 2026)

| Principle | Weight | Tool rule |
|---|---|---|
| A king escape (flight) available in the diagram makes the problem easy to solve | big flaw | `king escape in diagram` |
| A try refuted by a king move is pretty bad. Only a try the problem shows: an incidental White move refuted by a king move is no try and no flaw (E. Bourd, 26 Oct 2026: "no its not a try") | big flaw | `king refutes try` (tries by the key piece) |
| Random moves answered by one mate (S~) are not defences (E. Bourd, 15 and 26 Oct 2026: "those S~ are not defenses") | no content | `random defences`; not counted in `varied play` |
| A principle he taught needs no credit; credit him for a position, a scheme or the idea of that problem (26 Oct 2026: "dont name me, its ok") | convention | not a tool rule |
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

## Session 28: balance between thematic variations

On the finished knight-ambush problem (3R4/4b3/K7/1Np2n2/2kPp2p/B1p4q/2P5/3Q4), the
correction 1...Sd6 does two things at once (cuts the rook's guard of d5 and the bishop's guard
of c5) while 1...Se3 does one (cuts the queen's h3-d3 line). He agrees the richer effect is
nicer in itself, but calls the imbalance a drawback: "if the theme is symmetrical, we want the
effect in all thematic variations to be roughly similar." Corrections are a symmetrical theme,
so their motives should carry similar weight. Two ways to restore balance: give the other
correction a matching double effect, or make both single. A lone strong variation reads as an
accident, not a design.

## Verdicts on the first daily problems (7 October 2026, chat)

| Principle | Weight | Tool rule |
|---|---|---|
| A key by a piece out of play (a knight on the edge, far from the king) makes the solution obvious | fatal | `out-of-play key` (gate) |
| A White unit that takes no part in the solution, there only for a thematic try | fatal: "way too big of a price" | `try-only unit` (gate), `superfluous piece` (gate) |
| A known mechanism with nothing added, or reduced from the published original | not a problem | anticipation check (identical only); judge by hand |
| A single phase without thematic tries or changes, random tries do not count (18 Oct 2026), unless very complicated or pretty | not for publication | gate `single phase`; the judge may except it |
| Corrections: few and strong, errors subtle; remove the weaker of two weak ones; no fake blocker that only stops the random move from allowing the correction's mate | flaw | not yet |

## Session 29: keys that activate idle pieces, and changes that need their own mechanism

On the pawn-step problem (1r2k3/1N1p3p/7n/8/8/B7/Q1B1K3/7R, 1.Rf1! 2.Rf8#; d6 Qe6#, d5 Ba4#): "the Rf1 is
really bad as it is a piece out of play", and, sharpened: "the key piece is always in play; the issue is that
on the initial diagram it has no role - not guarding, not delivering mates, not blocking pieces. So its only
role is to come out of thin air and place itself obviously on the key square." The critique rule `idle key
piece` checks those three in the diagram (a guard of the black king's field, a set-play mate, a line it
blocks for any line piece); softer when the key piece also plays thematic tries.
Asked whether set-play mates for the two steps were worth two or three units: "obviously, but it will not
cost 2 or 3 units. A complete mechanism has to be thought; it will not be a small change to the existing
mechanism, as the gameplay is somewhat rigid." A change of mates is designed from the start.
What he liked: the dual avoidance, two mates that both seem possible after any pawn move, each killed by
one landing square.

His own changed-mate version (2B5/2p1N3/3k4/3NpK2/8/3pQ3/3P4/8, 1.Ke4! c6 Sf5#, c5 Qh6#; try 1.Be6? e4!):
"at first I just had two mates, then I somehow had to separate, that's obviously the hard part. Here it's
square vacations and line changes for the queen. Not so simple geometrically." He shifted the scheme one file
to make it work, and on why that is the only freedom: "Pawn move themes are limiting by nature, can't rotate
or move the board up or down. It does make the mechanism more rigid and less open for enhancements." He narrowed it: "By no rotations, it applies mostly to themes themselves involving pawns. If there are
pawns, then it's not impossible to rearrange so rotation works. Again unless a pawn move is critical
thematically then it might be more difficult." So the bench rotates with a warning naming the pawns to
re-place, refuses up/down shifts that put a pawn on the first or last rank, and warns when a shift gains or
loses a double step.
On the edge, asked whether a thematic pawn on the b or g file is worse than on c-f: "Just by the freedom, the
edge seems very limiting. Much less mates or freedoms to play with." Keep the thematic play central.

His answers on the pawn-step problem. Set duals: "not important imo, they are not part of the intended
thematic play" (the critique does not flag them; the report shows them as information). Threat or zugzwang:
"a threat, yes, it makes the problem richer. Zugzwang is limited and a bit less interesting by nature." How
the split came: "I wanted to find mate on h6, but stopping the mate on the diagonal was hard. The
breakthrough was adding the black pawn, which eliminated the rest of the mates and I could keep my h6 mate.
Maybe it was a bit lucky this worked, otherwise I would have to find a different reason for splitting. And
it's not easy inserting two effects in each of the keys." `chesscomp/compose/keepkill.py` now searches for
that unit (one addition that keeps the wanted mate and kills the rivals in every phase); it ranks bPe5 first.

On my verdict "using self-blocks twice was right": "I think it's not the correct framing. It worked. Not that
it was right, many other things could be 'right' as well. And if not I'll change so it was wrong?!" A
critique reports what a choice achieved and what the alternatives were; it does not bless the choice after
the fact, which would make the verdict follow the outcome.

On his own knight self-block sketch, whose thematic mates are set and unchanged by the key: "it's probably not
the best, lowers the complexity a bit, as no new play is generated by the key in a sense. But in a single
phase problem, the set play is not even mentioned, so it's not that bad. But yes, probably from solving and
quality perspective, a more dynamic key that changes or introduces the play is more interesting." Critique
rule `static key` (minor).

On the second black knight (f7) in his must/can't problem, which I had called the main blemish: "I disagree on
f7, it's a black knight stopping a lot of white play. I find it fine adding such black pieces, even if it's
the same type of the thematic piece." A black unit that holds back a lot of White's play is a legitimate
construction choice; a second unit of the thematic type is not a flaw in itself.

On the promotions in the must/can't problem: "the promotions, the fact that d1 also has the same effect as the
self-block, these are not great. Could almost remove the Se2 defence, and the content somewhat remains, but not
clean. But that d1=R stops big cooks like Qc3, so I accepted it in the construction limits (the improvements
could be infinite, extending more, cleaning etc.)." Verified: 1.Qc3? (2.Qc5#/d4#) fails only to 1...d1=Q/R/S.
Knowing where to stop is part of composing: a flaw that pays for soundness against a strong cook is accepted
once further cleaning stops paying.

Presentation: "Please keep showing diagrams when posting." Every position discussed gets a diagram card, not only a FEN.

Session 30, on the tools: "I know it's hard to make a program find my thematic desired content, especially if
it's not ready. But I think you should incrementally realize what we want to see in the solution, as I'm
solving, as I'm iterating: what operations could be sped up, what information is valuable, according to the
goal, and improve the solution view." First steps (bench v23): a theme box (pinned thematic defences, kept in
the table even while broken) and "since the last solve" (cooks, theme cells, holes, duals that the edit changed).

Session 30, his ordering of the work on the corrections problem (2Q1N3/1p6/1p1BPpP1/1B1knn1R/8/K3p3/4N1P1/8):
"prioritizing more challenging things first, so I need to change geometry or the scheme, only later getting to
the trivial." In order: (1) the threat, hardest with two flights; (2) guarding the square near the king;
(3) how to make two phases; (4) the threat was too hard, so zugzwang, which turned the original moves into
corrections ("a rather high level step; maybe I could have gone in the previous direction but I decided that
way"); (5) arranging the mates around the king flight; (6) construction with a purpose for each unit: Pg2 so the
mate after Ke4 is ready in the set play and 1.Qc2 does not take an unprovided flight; Ka3 as a cook-stopper,
so tries that give room fail to Qc4 with check; (7) last, the dual outside the thematic play ("least important,
but still annoying"), which forced rearranging the guard of e5. "I am very limited due to zugzwang and flights,
hard to manoeuvre much more."

On 1.Qg5-f5 (Muralidharan, Problemesis 2002, an alternative to the published 1.Qh3-f5): "G5 to f5 is also bad.
The queen is attacked. An attacked piece moving is counted as a flaw. Here it's debatable, as h3 is so out of
play, where it's obvious. I would probably go for g5 here, but not much of an improvement." Critique rule
`attacked key piece` (minor); the key finder marks such keys and lists them after clean ones.

Presenting a problem (session 30): "in official solutions that we present, it's ok to hide some flaws, the minor
ones. We can mention them to ourselves, but as part of the solution write what's needed." The solution block
carries the play (set, tries, key, variations, theme); minor flaws (a dual outside the thematic play, a passive
king, a provided diagram flight) go in our own notes or the mentor issue, not in the solution.

"I think king specifically as cook-stopper is not a flaw, it's ok." (critique: a king whose square matters for
soundness is a note, `cook-stopping king`, not `passive king`.) On the presented solution: "I would probably add
the [a], [b] for the mates that change thematically."

## Mentor answers, 10 Oct 2026 (issues #4, #5, #6)

- A unit that serves only the set play: "a big flaw, if it's completely redundant." (critique
  `set-play-only unit`: major when nothing else needs it, minor when it also holds soundness or the tries.)
- "Passive king is ok, it's usually a piece that is hard to give a role when many black pieces exist."
  (critique: `passive king` is a note.)
- Two changed mates on one effect without tries: "it's enough content, but I am always looking for extending
  for more content at the cost of pieces."
- A complete block where many White moves keep the set play: "seems hard to finish... blocking all of them
  will probably not be worth it."
- A failed daily run: he wants the failed report too, with diagrams, not only a study post.
- A try refuted by a king flight, even when the flight is the theme: "it's a big flaw." The rule stands.
- Several defences that guard the threat square, one of them a self-block: "unified is better... improving is
  always nice: unifying the scheme, the squares of the defences, the tries and so on."
- A protected key piece attacked by the king, whose key gives a flight, opens a line and guards the threat
  square (1.Sg7! in Daily No. 5): "no, it's a good key."
- Cook-stopper pawns: "acceptable, a lot more material is usually added to stop cooks and move stuff around."
- Restructuring (11 Oct 2026, after finishing two of my abandoned sketches on the bench): "i am pretty open to just
  switching a whole side around, the really small steps cant do it. i am reasoning over the reconstruction, and its
  not step by step. its whole restructuring." In his two-knights unpin, everything around the thematic core changed
  at once: the mate moved (Qh8 to Qf6), the queen took a second duty, Black self-blocks replaced White guards, and
  the key became the pinner arriving.
- A theme means a good problem around it (11 Oct 2026): "i always try to add more content. i consider what i can
  extend, almost at any point. maybe cleaner position, maybe making tries, maybe making changes. so even though i
  give a theme, what i actually mean is compose a good problem around it, not the simplest. not only the one
  fulfilling the theme... still you would want to make this in steps." Asking him "is it worth it?" is my job.
- Static key with a thematic job (1.Bf7 pins): "acceptable here, a bit predictable, but not too bad."
- Symmetry by design is a flaw in general; publish tries as a pair (one per thematic refutation), not 2+1.

- Spread scheme placement (11 Oct 2026): "i try picking so that my scheme placement is somewhat spread, you put the
  bishop on e5, its way too much interfering with too much. and takes a lot of freedom. you need the mechanism to be
  somewhat apart so its easier constructed. its not always possible, but starting on softer schemes is a skill."
- Shifts and rotations (11 Oct 2026): "they do not ruin the base of the theme". His demonstration on the bench
  (mv4dvvuh): a quarter turn fixed the pawns and the White king's room; 1.Sg6! (bourd-two-bishops-sg6).
- Freedom around the threat; mates away from the line (11 Oct 2026, second bench demonstration, 1.Qb5!): "i left
  freedom in my geometry around the threat, and what squares could be needed (i switched from d6 to e6, on the same
  line). and i changed the mates with the bishops, putting them away from the line, they are less interfering with
  other play and dont need a lot of patching." The d6 pawn was added "to avoid the defense Be5".

## 11 Oct 2026: on the studies of published #2s
- A White unit there only for a try is a drawback, not a fatal flaw: weigh it against what the try buys.
  (Asked about Pg2 in his own miniature 8/2K5/B7/8/4k3/7Q/6P1/6B1, which serves only 1.Be3?.)
- Miniatures are too simple: very basic even when they show changes. He would not publish one as an advanced
  composer; later in his career he mainly composed complex problems. Study material and our own aim should be
  complex #2s (several thematic phases, rich defences), not light positions.
- Reuse the mating pieces (11 Oct 2026, on 1.Qb5!): "both mating pieces guard the same c5. this makes so that each of
  the other variations they have a job, in some kind of mutual work of who guards c5. this way the play seems
  connected, and not like 2 distant variations." (anatomy: LINKS)

## 12 Oct 2026: on his own complex #2s
- Wola Gulowska 2015 5th HM (5Rq1/2p2b2/2Pp1Npn/2nQ2RP/4Pk1P/4N3/3rPPBK/2Brb3): the problem shows reciprocal changes
  (threat A / mate B in one try, threat B / mate A in the other), "rather complex". He started from the geometric
  scheme: both lines (two masked batteries on f4) and the mates by the knights; the content evolved from it.
  Process: geometry first (lines and mating units), then the paradox it can carry.
- StrateGems 2007 2nd HM: Pc4 is there to stop duals and cooks; the checking defence it allows is a by-product.
- (12 Oct) "As the content grows, we need to be more tolerable to flaws. A small 1 variation problem cannot be
  compared to like reciprocal changes. We pay flaws for content, and find the balance." Scale in the judge checklist.
- Tries come as their natural pair (12 Oct 2026, on 1.Se2!): "The rd1 is fatal here, as it disallows adding a second
  try. Showing just 1 gives bad taste. Se6 sounds like almost a must, once having the sb5 try."
- Weight follows the theme (12 Oct 2026, on 1.Sg6!): "i think the position is decent, its reasonable in terms for
  composing, your earlier versions showed simple themes. more complex themes require more pieces and more heavy
  positions." 7+9 with a try pair and two thematic variations is acceptable weight.

## The second layer reaches every thematic variation (mentor issue #21, 25 Oct 2026)
"If the thematic content consists of 2 variations, only 1 is not enough, its too short and usually spoils a lot. The
extention has to be aligned with both thematic variations somehow (tries, transfers and so on)." One try refuted by one
of two thematic defences (daily No. 20: 1.Bc7? Sd6!, nothing for 1...Se5) is not a second phase. Tool rule:
critique 'one-sided extension' (fatal in the gate): tries refuted by thematic defences and changes against the key must
reach at least two thematic variations (defences with their own mate; king flights belong to the key).
