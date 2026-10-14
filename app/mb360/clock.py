"""Demo clock. The seed is built around NOW = 2026-09-27 10:00 (data/seed/generate_seed.py);
the app uses that time until a real clock is wanted (specs/001-alr-core/plan.md, Complexity Tracking)."""
from datetime import datetime

SEED_NOW = datetime(2026, 9, 27, 10, 0)
_override: datetime | None = None


def now() -> datetime:
    return _override or SEED_NOW


def set(when: datetime) -> None:  # noqa: A001 - mirrors reset()
    global _override
    _override = when


def reset() -> None:
    global _override
    _override = None
