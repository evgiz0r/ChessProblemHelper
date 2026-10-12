"""Blind tourney experiments from yacpdb (E. Bourd, 12 Oct 2026; knowledge/experiments/README.md).

    python tools/blind_tourney.py build "The Problemist" 2010 --tourney "The Problemist" --label W
        fetches the year's orthodox #2 originals from yacpdb, seals them (awards included) in --sealed,
        and writes blind group files (FEN, published solution, author keywords; no author, source or award)
        to --blind for the judge agents. Prints only counts.
    python tools/blind_tourney.py compare --sealed DIR --order "W03 W11 ..."
        after our ranking is committed: our rank against the real distinctions, and the AUC.
"""
import argparse, json, os, random, re, subprocess, urllib.parse

import chess

GATEWAY = "https://www.yacpdb.org/gateway/ql?q="
PIECES = {'K': chess.KING, 'Q': chess.QUEEN, 'R': chess.ROOK, 'B': chess.BISHOP, 'S': chess.KNIGHT, 'P': chess.PAWN}
AWARD_WORDS = re.compile(r'prize|preis|prix|\bhm\b|honou?rable|commend|\blob\b|award', re.I)


def ql(query, page):
    out = subprocess.run(["timeout", "120", "curl", "-sS", GATEWAY + urllib.parse.quote(query) + f"&p={page}"],
                         capture_output=True, text=True).stdout
    d = json.loads(out)
    if not d.get("success"):
        raise SystemExit(d.get("error", "")[-300:])
    return d["result"].get("entries", [])


def fetch(source, year):
    # a date given as a year only counts as 1 January: query from the day before, then keep the year exactly
    q = (f'Stip("^#2$") AND Source("{source}") AND PublishedAfter("{year - 1}-12-31") '
         f'AND NOT PublishedAfter("{year}-12-31")')
    res, page = [], 1
    while True:
        e = ql(q, page)
        res += e
        if len(e) < 100:
            break
        page += 1
    # orthodox only: no options (fairy conditions), no twins, no neutral pieces (stored apart from white/black)
    return [x for x in res if not x.get("options") and not x.get("twins")
            and set(x.get("algebraic", {})) <= {"white", "black"}
            and x["source"].get("date", {}).get("year") == year]


def fen(entry):
    b = chess.Board(None)
    for colour, key in ((chess.WHITE, "white"), (chess.BLACK, "black")):
        for p in entry["algebraic"][key]:
            b.set_piece_at(chess.parse_square(p[1:]), chess.Piece(PIECES[p[0]], colour))
    return b.board_fen()


def build(a):
    os.makedirs(a.sealed, exist_ok=True)
    os.makedirs(a.blind, exist_ok=True)
    entries = fetch(a.source, a.year)
    keep, other, bad = [], 0, 0
    for e in entries:
        aw = e.get("award")
        if aw and a.tourney and aw["tourney"]["name"] != a.tourney:
            other += 1
            continue
        try:
            keep.append((e, fen(e)))
        except Exception:
            bad += 1
    random.seed(a.year)
    random.shuffle(keep)
    field = [{"label": f"{a.label}{i + 1:02d}", "id": e["id"], "fen": f} for i, (e, f) in enumerate(keep)]
    json.dump([e for e, _ in keep], open(os.path.join(a.sealed, "entries.json"), "w"), ensure_ascii=False)
    json.dump(field, open(os.path.join(a.sealed, "map.json"), "w"), indent=0)
    byid = {e["id"]: e for e, _ in keep}
    leaks = 0

    def block(x):
        nonlocal leaks
        e = byid[x["id"]]
        sol = re.sub(r"\n\s*\n", "\n", e.get("solution", "")).strip()
        if AWARD_WORDS.search(sol):
            leaks += 1
            sol = "(solution withheld: it mentions an award)"
        kw = ", ".join(e.get("keywords") or []) or "(none)"
        return (f"=== {x['label']}\nFEN: {x['fen']}\nAuthor's theme keywords: {kw}\n"
                f"Published solution:\n{sol}\n\n") if a.solutions else f"{x['label']}: {x['fen']}\n"

    with open(os.path.join(a.blind, "field.txt"), "w") as f:
        f.write("".join(f"{x['label']}: {x['fen']}\n" for x in field))
    n = (len(field) + a.size - 1) // a.size
    for g in range(n):
        with open(os.path.join(a.blind, f"g{g}.txt"), "w") as f:
            f.write("".join(block(x) for x in field[g * a.size:(g + 1) * a.size]))
    print(f"{a.source} {a.year}: {len(field)} problems in {n} groups; excluded {other} awarded in other tourneys, "
          f"{bad} unreadable; {sum(1 for e, _ in keep if e.get('award'))} with a distinction; "
          f"solutions withheld for award words: {leaks}")


def compare(a):
    field = json.load(open(os.path.join(a.sealed, "map.json")))
    byid = {e["id"]: e for e in json.load(open(os.path.join(a.sealed, "entries.json")))}
    order = a.order.split()
    assert sorted(order) == sorted(x["label"] for x in field), "order must list every label once"
    rows = []
    for x in field:
        e = byid[x["id"]]
        aw = e.get("award") or {}
        rows.append((order.index(x["label"]) + 1, x["label"], aw.get("distinction", "-"),
                     ", ".join(aw.get("judges", [])), ", ".join(e["authors"]), ", ".join(e.get("keywords") or [])))
    rows.sort()
    for r in rows:
        print(" | ".join(str(c) for c in r))
    placed = [r[0] for r in rows if r[2] != "-"]
    unplaced = [r[0] for r in rows if r[2] == "-"]
    if placed and unplaced:
        auc = sum(p < u for p in placed for u in unplaced) / (len(placed) * len(unplaced))
        print(f"AUC {auc:.2f}; placed {len(placed)} of {len(rows)}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    b = sp.add_parser("build")
    b.add_argument("source")
    b.add_argument("year", type=int)
    b.add_argument("--tourney", help="keep only distinctions of this tourney (others are excluded)")
    b.add_argument("--label", default="X")
    b.add_argument("--size", type=int, default=8)
    b.add_argument("--no-solutions", dest="solutions", action="store_false")
    b.add_argument("--sealed", default="/tmp/claude-0/sealed/yac/current")
    b.add_argument("--blind", default="/tmp/claude-0/blind_current")
    c = sp.add_parser("compare")
    c.add_argument("--sealed", default="/tmp/claude-0/sealed/yac/current")
    c.add_argument("--order", required=True)
    args = ap.parse_args()
    build(args) if args.cmd == "build" else compare(args)
