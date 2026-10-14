# Underpromotion keys

Settings: claude-underpromotion-S (8/4P3/4bB2/6K1/1N2k3/8/4P1N1/8: 1.e8=S! B~ 2.Sd6#),
claude-underpromotion-B (K7/4P3/5PN1/4b3/2P1k1P1/5N2/4PP2/8: 1.e8=B! 2.Bc6#),
claude-underpromotion-R (8/4P3/8/5P2/4N2k/5P2/6P1/K7: 1.e8=R! Kh5 2.Rh8#).
Reason used in all three: after the wrong promotion Black is stalemated (the queen pins or covers the
last Black move; a bishop cannot pin on a file, a rook cannot on a diagonal; a knight pins nothing but
must then produce the mate). Cost: Black immobile, so the play is thin; ~150k enumerated additions gave
no second variation.
Flight motivation (not pin): claude-underpromotion-B-flight (8/2K1P3/3P4/3kP3/7R/3N4/8/5R2: 1.e8=B! Ke6
2.Bf7#) - the only Black square lies on the promotion file, Q/R cover it and stalemate, the bishop mates from
the diagonal-adjacent square with an x-ray over the vacated square; box units must not be able to check d5.
Minimal form (E. Bourd): 7K/3P1k2/3Q4/8/8/8/8/8, 1.d8=B! Ke8 2.Qe7# - the promotion removes the pawn's
attack on e8 (flight-giving), Q/R re-cover it on the rank and stalemate, the bishop protects e7 for the queen.
Exhaustive: 11 such four-unit positions exist, all with a queen; nothing smaller. Four promotions as
try/key in one problem: bourd-four-promotions (5K2/3P4/1N2p3/1P2k1NP/1P4P1/3p4/3B4/8).
Threat with real defences (daily No. 9, claude-underpromotion-S-threat): B2B4/2r1P3/2nppp2/N3k3/2P3Q1/8/8/2K5,
1.e8=S! (2.Bxf6#) Rf7/Re7 2.Sxc6#, Sxd8/Se7 2.Qe4#; 1.e8=Q?/R? f5!. Recipe: list the squares only the promoted piece
reaches from the promotion square (knight on e8: d6, f6, c7, g7) and make one of them the guard a white line piece
needs once the promotion unmasks it (Bd8-e7-f6 against Ke5 behind black pawns d6, e6, f6). Q and R then fail for a
reason in the position, not by stalemate. Built post-key first: postsearch with CORE=3BN3/8/3ppp2/4k3/8/8/8/8,
THREAT=Bd8f6, DEFS=Re7,Ne7 placed every other unit in under five minutes. Open: changed mates (both mates are set
there), and a different refutation for each wrong promotion. evolve KEY=e7e8n NVAR=n scores a fixed key.
Not done yet: mates by underpromotion (AUW without the queen).
