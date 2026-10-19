"""Fast and full test runs (E. Bourd, 19 Oct 2026: "tests are starting to take long, maybe small tests up to 2 minutes.
and big regressions just remind like one in whatever").

    python -m pytest -q tests            fast run (about a minute): every test except the slow ones below
    python -m pytest -q tests --full     everything (about 7 minutes); a pass writes today's date to LAST_FULL

The fast run still re-solves every stored key (tests/test_regression.py). It prints a reminder when the last full
pass recorded in LAST_FULL is older than FULL_EVERY_DAYS days, or missing. A test slower than about 4 s goes in SLOW.
"""
import datetime
import os
import pytest

SLOW = {
    'test_keyfind.py::test_newunit_finds_the_clearance_key',
    'test_battery_guards.py::test_queen_holds_the_d_file_battery_two_ways',
    'test_battery_guards.py::test_holder_attacking_the_rear',
    'test_battery_guards.py::test_no_knight_holds_the_pawn_battery',
    'test_battery_guards.py::test_pawn_front_piece',
    'test_rerefute.py::test_lighten_finds_his_queen_removal',
    'test_rerefute.py::test_lighten_checks_every_first_move_for_a_cook',
    'test_rerefute.py::test_finds_his_bg6_regard',
    'test_blog.py::test_single_phase_needs_tries_or_changes',
    'test_blog.py::test_white_correction_with_king_tries_in_the_threat_pool',
    'test_blog.py::test_plug_that_also_plays_a_try_is_not_try_only',
    'test_blog.py::test_gate_refuses_a_cook',
    'test_blog.py::test_random_tries_are_not_a_second_phase',
    'test_keysel.py::test_critique_counts_a_double_threat_stopper_as_needed',
    'test_keysel.py::test_a_unit_that_stops_solution_duals_is_not_set_play_only',
    'test_anatomy.py::test_refutation_reason_and_stalemate',
}
LAST_FULL = os.path.join(os.path.dirname(__file__), '..', 'knowledge', 'last_full_tests.txt')
FULL_EVERY_DAYS = 2


def pytest_addoption(parser):
    parser.addoption('--full', action='store_true', help='also run the slow tests (the full regression)')


def pytest_configure(config):
    config.addinivalue_line('markers', 'slow: part of the full run only (python -m pytest -q tests --full)')


def pytest_collection_modifyitems(config, items):
    for item in items:
        if f"{os.path.basename(str(item.fspath))}::{item.originalname}" in SLOW:
            item.add_marker(pytest.mark.slow)
    if config.getoption('--full'):
        return
    keep = [i for i in items if 'slow' not in i.keywords]
    if len(keep) < len(items):
        config.hook.pytest_deselected(items=[i for i in items if 'slow' in i.keywords])
        items[:] = keep


def _last_full():
    try:
        return datetime.date.fromisoformat(open(LAST_FULL).read().split()[0])
    except (OSError, ValueError, IndexError):
        return None


def pytest_sessionfinish(session, exitstatus):
    if session.config.getoption('--full') and exitstatus == 0 and session.testscollected:
        with open(LAST_FULL, 'w') as f:
            f.write(datetime.date.today().isoformat() + '\n')


def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if config.getoption('--full'):
        return
    last = _last_full()
    if last is None or (datetime.date.today() - last).days >= FULL_EVERY_DAYS:
        when = 'never recorded' if last is None else f'last on {last}'
        terminalreporter.write_line(f'REMINDER: full regression {when}: run python -m pytest -q tests --full', yellow=True)
