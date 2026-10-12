from chesscomp.compose import trypair

FEN = '3N2b1/b2P3p/3pP2R/1Q1pk1K1/3pN2R/8/1n1PP1PP/2r3B1'
SPEC = {"key": "e4g3", "tries": {"e4f2": "c1c5", "e4f6": "a7c5"},
        "want": {"Bc5": "Nd8c6", "Rc5": "Bg1d4"}, "threat": "Rh4e4"}


def test_pure_try_pair_passes_both_filters():
    # 12 Oct 2026: the pure pair 1.Sf2? Rc5!, 1.Sf6? Bc5!, key 1.Sg3! (E. Bourd: one real try is unfinished)
    trypair.SPEC = SPEC
    assert trypair.cheap(FEN) is not None
    ok, info = trypair.full(FEN)
    assert ok, info


def test_a_cook_is_rejected():
    trypair.SPEC = SPEC
    ok, _ = trypair.full('3N2b1/b2P3p/3pP2R/1Q1pk1K1/3pN2R/8/1n2P1PP/2r3B1')   # without wPd2: 1.Sd2 also works
    assert not ok
