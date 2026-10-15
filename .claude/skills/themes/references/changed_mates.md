# Changed mates

Settings: bourd-changed-mates-3 (8/4p2K/Q2B4/1N1Np3/1pP1k1P1/6P1/2n1P3/8), bourd-changed-mates-4
(1K3b2/1P1p1B2/3r2p1/Q3P1RN/R1n1k2p/3p1p2/4nP2/4Nb2), claude-one-knight-change
(5NR1/8/8/5nQ1/3Pk3/3R1p2/3K4/4N3), bourd-one-knight-change (8/2K2p2/6pB/3p1nQ1/3Pk1P1/2P5/4P3/5r2),
claude-one-bishop-change-2 (7n/6b1/1Np5/R7/3Pk1K1/2Q5/8/8), bourd-two-captures-three-phase
(KB3R2/4p2P/4Pq2/2pPNB1p/1pRbNk1P/6pQ/3P4/7n), claude-two-captures-e5 (2R5/3n1p2/1B6/1K1kP1Q1/1P4B1/4rP2/8/8,
daily No. 3).

Mechanism: one Black effect that yields several mates; a selector per phase; then the threat. Selectors:
Black pawns guarding the mating squares removed one per phase; the queen's post; the key piece giving the
set mates and switching them off by moving; the key piece that moved giving the other mate itself.
Simplest one-defence change: set 1...Sxd4 2.Qe3#, 1.Qf6! 1...Sxd4 2.Qxd4#.
Two units capturing on one square: the capture square on two battery lines (departure opens one, arrival
self-blocks the other); the queen's post selects which departure mates; three phases for one defence.
Fast start for "two pieces defend on the same square": let them CAPTURE a White unit there
(8/3n4/8/3kP3/8/4r3/8/8), then arrange the mates, then the threat.
Two captures of the threat's guard (daily No. 3): Sd7xe5 and Re3xe5 both remove d6's only guard. Set mates by
the lines the departures open (Rd8#, Qd2# through e3); 1.Qe7 leaves the g5-d2 line and the mates change to the
knight's unguard of c5 (Qc5#) and the rook's self-block of e5 (Qxd7#). Evolve CHANGED=1 seeded with the core
8/3n4/8/3kP3/8/4r3/8/8 found it in ten minutes; bare cores found nothing. Its hits put a unit on the board only
for a set mate (Rg8 for Rd8#): give that mate to a unit that also works after the key where you can.
His answer to No. 3 (bourd-e4-selfpins, 8 Oct): the same two captures, but on e4 under the queen's rank, so in the
set they self-pin (pin-mates Rd7#/Rd1#, the pinned unit cannot block again) and after 1.Qe6 they unguard b5/c3
(Sxb5#/Bc3#). One Black error per phase. The reason came from a one-rank shift, not from a new unit. A flight on e4
was not possible: its mate needed d5, the phase selector (lessons.jsonl, 8 Oct).
Traps: the try threat and the key duals coming from the same resource (2Rn1N2/7K/3P4/3k4/pB1p1P2/3n1P2/1p1Q1p2/8);
a set+solution block cooked by any waiting move; a diagram flight that the change needs (queen on g5/h5).
Dead end: blind enumeration for same-piece changes (5M positions, nothing); the composer's 3-unit scheme
plus ONE named changed defence as the criterion succeeded in one pass.

Note (E. Bourd, 15 Oct 2026): "those type 1 - 2 - 3 are just enumerations, not real composition terms" - his way to break
down the implementation stage (unguard, self-block, line play...), separate from the theme (changes, tries...). Never present
them as terms in a post or a source line; name the theme (changed mates) and say how it is implemented.
E. Bourd's three types (bench mv88wzbb, 14 Oct 2026): (1) one White piece mates in both phases on another line, each
Black defender guarding one arrival square on each line; (2) different White pieces mate; (3) one piece has two mates
and each phase excludes one (king flights widen the geometry but make the play rigid).
Type 1, claude-changed-type1-qg8 (8/3BB3/5NQ1/4k1Pp/2pn4/2n1P3/8/7K): Sd4 guards f5+e6, Sc3 guards e4+d5; the queen on
b1-h7 (g6) mates Qf5/Qe4, after 1.Qg8! on a2-g8 Qe6/Qd5. One protector per knight pair (Sf6: e4, d5; Bd7: f5, e6).
Knights next to the king interpose on every rank/file check, so the threat is a diagonal check they cannot reach
(Qb8+ through d6). Evolve on bare cores (8 jobs) found no key; the hand design, one cure per solve, did.
E. Bourd on it: "realistically all knight moves are the same" - one change per knight, not six. Unique defences:
claude-changed-type1-unique-qg8 (8/2pK2nQ/5N2/4k1P1/7p/2nBP3/2r1p3/8): the threat 2.Sg4 is made by the e4/d5 guard
itself, so d5 hangs on the queen's new line and f5 on Bd3 alone; only Se6 cuts g8-d5, only Se4 cuts d3-f5. The f5/e6
knight stands on g7 (not d4), shutting the queen's 7th rank (no twin 1.Qf7). Search: evolve UNIQUE=1.
Type 1 with a rook and a bishop (claude-changed-type1-rook-bishop, 1K6/7b/1N1B4/1p5r/3k1pp1/Q7/nPpNBP2/2r5): impossible with
two whole queen lines (`python -m chesscomp.compose.type1_geometry d4 --types RB` prints the post pairs that work, with
knight threats, the off-line defences and the plugs). Qa3 -> Qa8: Bh7 holds d3/e4, Rh5 holds c5/d5; set Bg8 Qd3#, Rh3 Qc5#;
1.Qa8! (2.Sb3#) Bg8 Qe4#, Rh3 Qd5#. Its set Grimshaw on f5 is fake (E. Bourd: never fulfilled after the key, so
it does not exist). Before anything else check the set escape: the threat piece's vacated
square must not be mated by the set queen (Qg3-g2 and Qc7-b7 died there); a threat square on the queen's own line cures it.
Cost here: six black cook-stoppers.
Two orthogonal lines (claude-changed-type1-ranks, 8/3K4/2p1p3/7Q/N2k1PP1/8/1N3PB1/2r1r3): Qh5 -> Qh3, black rooks c1/e1;
set Rcd1 Qc5#, Red1 Qe5#; 1.Qh3! (2.Qd3#, the line's third square) Rcd1 Qc3#, Red1 Qe3#: both rooks defend on d1. Guard the
field with units that cannot mate there (knights, a bishop off the lines); by-play Rc3/Re3 (Qxc3, Qxe3) is inherent.
Two errors in one defence (E. Bourd, bourd-changed-type1-pawn-errors, 2Q2K2/1B1N4/3p4/1p6/1n1k1P2/1Ppp2R1/2b2N2/2b5):
the defender need not hold one square of each line. 1...d3-d2 opens wRg3 to c3 (set Qxc3#) and closes bBc1 to e3 (Qe3#
after 1.Qe8!). Combine any two errors (unguard, black line closed, white line opened, self-block); the queen's line picks one.
`python -m chesscomp.compose.effects POSTKEY MOVE` lists each move's errors.
Where two errors are possible (claude-changed-type1-qg8-two-errors, 8/3BB1nQ/1nP2N2/p3k1Pp/r7/p2KP1P1/8/8, the first type-1
problem redone): with no diagram flight and the threat needing the set squares guarded, every mate comes from removing a
Black guard, and on the side the queen comes from (f5/e6 for a queen above K e5) no defence can do it twice: each Black line
to one of those squares hits the other or the queen's path. A White line opened onto e6 leaves e6 a flight in the diagram.
So only the far pair (e4/d5) takes two errors: Sf2-d3, Sb6-c4 (used: arrival closes Ra4-e4, departure unguards d5), d5-d4.
E. Bourd's pawn scheme has the same split (d5 double unguard on the near squares, d2 two errors on the far ones).
`python -m chesscomp.compose.errors FEN DEF --key UCI` says which part of the move (departure / arrival) makes each mate.
Type 2 (different White pieces mate), his rook scheme: claude-type2-rooks-light (8/2n5/2B2RK1/4k3/3R4/4P1n1/8/8) and
claude-type2-rooks-full (b7/1pn5/1PB2R2/4k1P1/3R2P1/3K2n1/8/8). Rd4 mates on d5/e4, Rf6 on e6/f5; Sc7 guards d5+e6, Sg3 e4+f5
(not Sd6, which both rooks capture). All four squares touch the king, so the selector is protection: Bc6 (d5, and e4 through
d5) in the set, 1.Bd7! (e6, and f5 through e6). The far square of each pair needs a second guard in the near mate (e4 in
Rd5#: Pd3/Kd3; f5 in Re6#: Kg6/Pg4). A mutate needs a set hole, or every waiting move solves (Kf7, Bb7, Rg6 cooked the
complete block): leave one variation unguarded (light, one change) or let a black pawn take the key piece (full, 2x2, three
units and an escape-looking key). Trim block problems only with the 15 Oct fix of chesscomp.compose.trim.
