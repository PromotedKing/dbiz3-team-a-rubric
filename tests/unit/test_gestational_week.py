"""T012 — ALR FR-015: completed weeks from the EDD (research R4, same rule as the seed)."""
from datetime import date

from mb360.alr import reports


def test_u09_is_in_week_20_at_seed_now():
    assert reports.gestational_week(date(2027, 2, 14), date(2026, 9, 27)) == 20


def test_due_date_is_week_40():
    assert reports.gestational_week(date(2026, 12, 20), date(2026, 12, 20)) == 40
