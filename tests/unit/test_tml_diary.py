"""T004 — TML FR-008 – FR-010, BR-002, BR-005, BR-006 (diary entry and photos)."""
import pytest

from mb360.tml import diary, weeks
from tests.acc_helpers import NOW

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
JPG = b"\xff\xd8\xff\xe0" + b"\x00" * 64
GIF = b"GIF89a" + b"\x00" * 64


@pytest.fixture
def media(tmp_path, monkeypatch):
    monkeypatch.setattr(diary, "MEDIA_DIR", tmp_path)
    return tmp_path


def counts(db):
    return tuple(db.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in ("DIARY_ENTRY", "DIARY_IMAGE"))


def test_save_entry_with_photo(db, user_id, media):
    lan = user_id("tci-000123")
    did = diary.save(db, lan, "Short walk today", "Calm", [("walk.png", PNG)], NOW)
    e = db.execute("SELECT * FROM DIARY_ENTRY WHERE diary_id = ?", (did,)).fetchone()
    assert (e["text"], e["mood"], e["entry_date"], e["gestational_week"]) == ("Short walk today", "Calm", "2026-09-27", 28)
    imgs = db.execute("SELECT * FROM DIARY_IMAGE WHERE diary_id = ?", (did,)).fetchall()
    assert len(imgs) == 1 and imgs[0]["sort_order"] == 1 and imgs[0]["file"].startswith("diary/")
    assert (media / imgs[0]["file"]).read_bytes() == PNG


def test_entry_is_linked_to_the_current_week_not_the_viewed_one(db, user_id, media):
    did = diary.save(db, user_id("tci-000123"), "Looking back", None, [], NOW)       # whatever week was on screen (BR-005)
    assert db.execute("SELECT gestational_week FROM DIARY_ENTRY WHERE diary_id = ?", (did,)).fetchone()[0] == 28


@pytest.mark.parametrize("text, mood, photos, field", [
    ("", None, [], "text"),
    ("x", "Angry", [], "mood"),
    ("x", None, [("p.png", PNG)] * 6, "photos"),
    ("x", None, [("a.gif", GIF)], "photos"),
    ("x", None, [("fake.png", b"not an image at all")], "photos"),
    ("x", None, [("big.jpg", JPG + b"\x00" * (10 * 1024 * 1024))], "photos"),
])
def test_invalid_entry_writes_nothing(db, user_id, media, text, mood, photos, field):
    before = counts(db)
    with pytest.raises(diary.DiaryError) as e:
        diary.save(db, user_id("tci-000123"), text, mood, photos, NOW)
    assert field in e.value.errors
    assert counts(db) == before and list(media.rglob("*.*")) == []


def test_save_clears_the_week_cache(db, user_id, media):
    lan = user_id("tci-000123")
    weeks.load_week(db, lan, 28, NOW.date())
    diary.save(db, lan, "New memory", "Happy", [], NOW)
    assert not any(k[0] == lan for k in weeks.CACHE)


def test_no_edit_or_delete(db):
    assert not [n for n in dir(diary) if n.startswith(("update", "edit", "delete", "remove"))]      # BR-006, D-60
