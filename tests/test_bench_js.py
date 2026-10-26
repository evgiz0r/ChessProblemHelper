"""The bench runs docs/analysis.js on docs/bench/chess.js in the browser; run the same pair in node."""
import json
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent
RUNNER = r"""
const fs = require('fs'), vm = require('vm');
const ctx = { window: {}, console }; ctx.self = ctx; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx); ctx.Chess = ctx.window.Chess;
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);
const r = ctx.ChessComp.keyReadiness(process.argv[3], false);
console.log(JSON.stringify(r.solutions));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_post_key_readiness_after_double_step_with_ep():
    # 1.e4 lets ...fxe3 e.p.; "Black passes" must drop the e.p. square or chess.js throws
    # "illegal en-passant square" (E. Bourd, 18 Oct 2026, bench post-key play)
    out = subprocess.run(["node", "-e", RUNNER, str(ROOT / "docs/bench/chess.js"), str(ROOT / "docs/analysis.js"),
                          "k7/8/1K6/8/5p2/8/4P3/7R"], capture_output=True, text=True, timeout=60)
    assert out.returncode == 0, out.stderr
    assert isinstance(json.loads(out.stdout), list)


RUNNER_REPORT = r"""
const fs = require('fs'), vm = require('vm');
const ctx = { window: {}, console }; ctx.self = ctx; vm.createContext(ctx);
vm.runInContext(fs.readFileSync(process.argv[1], 'utf8'), ctx); ctx.Chess = ctx.window.Chess;
vm.runInContext(fs.readFileSync(process.argv[2], 'utf8'), ctx);
console.log(ctx.ChessComp.formatReport(ctx.ChessComp.analyse(process.argv[3], '#2', {})));
"""


@pytest.mark.skipif(shutil.which("node") is None, reason="node not installed")
def test_bench_reports_random_move_when_the_threat_captures_the_piece():
    # E. Bourd (26 Oct 2026): "if we are attacking it, a random of it defends. thats for sure a random move"
    out = subprocess.run(["node", "-e", RUNNER_REPORT, str(ROOT / "docs/bench/chess.js"), str(ROOT / "docs/analysis.js"),
                          "8/B7/8/5p2/2Prkp2/1Q3N1K/6P1/8 w - - 0 1"], capture_output=True, text=True, timeout=120)
    assert out.returncode == 0, out.stderr
    assert 'R~ random' in out.stdout and 'Sg5#' in out.stdout, out.stdout
