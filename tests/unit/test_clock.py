"""T005 — demo clock (plan.md Complexity Tracking: seed NOW)."""
from datetime import datetime

from mb360 import clock


def test_default_now_is_the_seed_now():
    clock.reset()
    assert clock.now() == datetime(2026, 9, 27, 10, 0)


def test_now_can_be_overridden_and_reset():
    clock.set(datetime(2026, 10, 1, 8, 30))
    assert clock.now() == datetime(2026, 10, 1, 8, 30)
    clock.reset()
    assert clock.now() == datetime(2026, 9, 27, 10, 0)
