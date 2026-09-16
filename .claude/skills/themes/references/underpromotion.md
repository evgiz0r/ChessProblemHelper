# Underpromotion keys

Settings: claude-underpromotion-S (8/4P3/4bB2/6K1/1N2k3/8/4P1N1/8: 1.e8=S! B~ 2.Sd6#),
claude-underpromotion-B (K7/4P3/5PN1/4b3/2P1k1P1/5N2/4PP2/8: 1.e8=B! 2.Bc6#),
claude-underpromotion-R (8/4P3/8/5P2/4N2k/5P2/6P1/K7: 1.e8=R! Kh5 2.Rh8#).
Reason used in all three: after the wrong promotion Black is stalemated (the queen pins or covers the
last Black move; a bishop cannot pin on a file, a rook cannot on a diagonal; a knight pins nothing but
must then produce the mate). Cost: Black immobile, so the play is thin; ~150k enumerated additions gave
no second variation.
Not done yet: an underpromotion key with a threat and real defences (the check-avoidance route failed,
see the compose skill's dead ends), and mates by underpromotion (AUW without the queen).
