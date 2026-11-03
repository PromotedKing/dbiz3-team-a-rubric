"""Demo clock. The seed is built around NOW = 2026-09-27 10:00 (data/seed/generate_seed.py);
the tests use that time. mb360.server (the v1.0.0 app) switches to the real time with use_live()."""
from datetime import datetime, timedelta, timezone

SEED_NOW = datetime(2026, 9, 27, 10, 0)
_override: datetime | None = None
_live = False
VIETNAM = timezone(timedelta(hours=7))    # a hosting server usually runs in UTC; Vietnam has no daylight saving


def now() -> datetime:
    if _override:
        return _override
    return datetime.now(VIETNAM).replace(tzinfo=None, second=0, microsecond=0) if _live else SEED_NOW


def set(when: datetime) -> None:  # noqa: A001 - mirrors reset()
    global _override
    _override = when


def reset() -> None:
    global _override, _live
    _override = None
    _live = False


def use_live() -> None:
    global _live
    _live = True
