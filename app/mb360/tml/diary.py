"""S-051 / S-052 diary entry: TML FR-008 – FR-010, BR-002, BR-005, BR-006, D-46, D-60 (research R4).

An entry is created and read only — there is no update or delete (BR-006, D-60)."""
import sqlite3
import uuid
from datetime import date, datetime
from pathlib import Path

from . import weeks

MEDIA_DIR = Path(__file__).resolve().parents[3] / "media"   # git-ignored; the database keeps the relative path
MOODS = ("Happy", "Calm", "Nervous", "Tired", "Worried")
MAX_PHOTOS = 5
MAX_BYTES = 10 * 1024 * 1024
SIGNATURES = {b"\x89PNG\r\n\x1a\n": "png", b"\xff\xd8\xff": "jpg"}


class DiaryError(Exception):
    def __init__(self, errors: dict):
        super().__init__("invalid diary entry")
        self.errors = errors


def _kind(data: bytes) -> str | None:
    return next((ext for sig, ext in SIGNATURES.items() if data.startswith(sig)), None)


def validate(text: str, mood: str | None, photos: list) -> dict:
    errors = {}
    if not (text or "").strip():
        errors["text"] = "Please write something about today."
    if mood and mood not in MOODS:
        errors["mood"] = "Choose one of the moods."
    if len(photos) > MAX_PHOTOS:
        errors["photos"] = f"At most {MAX_PHOTOS} photos."
    elif any(_kind(data) is None for _, data in photos):
        errors["photos"] = "Photos must be JPG or PNG."
    elif any(len(data) > MAX_BYTES for _, data in photos):
        errors["photos"] = "Each photo must be 10 MB or smaller."
    return errors


def save(conn: sqlite3.Connection, user_id: str, text: str, mood: str | None, photos: list, now: datetime) -> str:
    photos = [(name, data) for name, data in photos if data]
    errors = validate(text, mood, photos)
    if errors:
        raise DiaryError(errors)
    edd = conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (user_id,)).fetchone()
    if edd is None:
        raise DiaryError({"text": "Set up the pregnancy first."})
    week = weeks.current_week(date.fromisoformat(edd[0]), now.date())     # BR-005: always the current week
    diary_id = str(uuid.uuid4())
    files = [(f"diary/{diary_id}-{i}.{_kind(data)}", data) for i, (_, data) in enumerate(photos, start=1)]
    written = []
    try:
        conn.execute("INSERT INTO DIARY_ENTRY (diary_id, user_id, text, mood, gestational_week, entry_date) VALUES (?, ?, ?, ?, ?, ?)",
                     (diary_id, user_id, text.strip(), mood or None, week, now.date().isoformat()))     # BR-002: automatic date
        for order, (rel, data) in enumerate(files, start=1):
            conn.execute("INSERT INTO DIARY_IMAGE (image_id, diary_id, file, sort_order) VALUES (?, ?, ?, ?)",
                         (str(uuid.uuid4()), diary_id, rel, order))
            path = Path(MEDIA_DIR) / rel
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(data)
            written.append(path)
        conn.commit()
    except Exception:
        conn.rollback()
        for path in written:
            path.unlink(missing_ok=True)
        raise
    weeks.clear(user_id)
    return diary_id
