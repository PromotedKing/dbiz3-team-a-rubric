"""Diary fixture coverage on the fresh-demo path."""
from collections import Counter
from datetime import date, datetime

from fastapi.testclient import TestClient

from mb360 import clock, persona
from mb360.main import create_app

NOW = datetime(2026, 11, 13, 10)


def test_fresh_demo_diary_schedule_and_media(db, user_id, monkeypatch):
    monkeypatch.setattr(persona, "_copy_art", lambda: None)
    clock.set(NOW)
    persona.install(db, NOW)
    expected = {
        "126": (7, [1, 2, 1, 2, 3, 3, 3], 5),
        "200": (8, [1, 2, 1, 2, 2, 3, 2, 3] + [4, 5] * 4 + [4], 19),
        "123": (8, [1, 2, 1, 2, 2, 3, 2, 3] + [5] * 6 + [4] * 11, 30),
        "128": (8, [1, 2, 1, 2, 2, 3, 2, 3] + [5] * 13 + [4] * 11, 42),
        "133": (6, [], 0),
    }
    for suffix, (first_week, counts, photos) in expected.items():
        user = user_id("tci-000" + suffix)
        rows = db.execute("""SELECT d.entry_date, d.gestational_week, d.mood, COUNT(i.image_id) AS photos
                             FROM DIARY_ENTRY d LEFT JOIN DIARY_IMAGE i USING(diary_id)
                             WHERE d.user_id=? GROUP BY d.diary_id ORDER BY d.entry_date""", (user,)).fetchall()
        assert len(rows) == sum(counts)
        assert Counter(r["gestational_week"] for r in rows) == dict(enumerate(counts, first_week))
        assert sum(r["photos"] for r in rows) == photos
        assert all(r["photos"] <= 1 and date.fromisoformat(r["entry_date"]) < NOW.date() for r in rows)
        if rows:
            first, = db.execute("SELECT MIN(visit_date) FROM VISIT WHERE user_id=?", (user,)).fetchone()
            assert rows[0]["entry_date"] == first
            assert max(Counter(r["entry_date"] for r in rows).values()) <= 2
            assert len({r["mood"] for r in rows}) == 5
            days = [r["entry_date"][-2:] for r in rows if r["gestational_week"] == first_week + len(counts) - 1]
            assert days == (["09", "11", "12"] if suffix == "126" else ["09", "10", "11", "12"])
        if rows:
            entries = db.execute("SELECT entry_date,text,gestational_week FROM DIARY_ENTRY WHERE user_id=?", (user,)).fetchall()
            endings = Counter(entry["text"].split(". ")[-1] for entry in entries)
            assert max(endings.values()) / len(entries) <= 0.20
            visits = dict(db.execute("SELECT visit_date,gestational_week FROM VISIT WHERE user_id=?", (user,)))
            for entry in entries:
                visit_week = visits.get(entry["entry_date"])
                if visit_week is not None:
                    assert entry["text"].startswith(f"Hôm nay mình đi khám thai tuần {visit_week}.")
    messages = db.execute("""SELECT u.tci_account_ref, f.week, f.created_at FROM FAMILY_MESSAGE f
                             JOIN USER_ACCOUNT u USING(user_id) ORDER BY u.tci_account_ref, f.created_at""").fetchall()
    assert [(r[0], r[1], r[2][:10]) for r in messages] == [
        ("tci-000123", 32, "2026-11-12"), ("tci-000123", 32, "2026-11-12"),
        ("tci-000126", 13, "2026-11-12"), ("tci-000128", 39, "2026-11-12"),
    ]
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    with TestClient(create_app(db)) as client:
        user = user_id("tci-000133")
        for page in ("timeline", "journey", "health"):
            assert client.get(f"/m/{user}/{page}").status_code == 200

def test_fresh_demo_staff_notices_match_events(db, user_id, monkeypatch):
    monkeypatch.setattr(persona, "_copy_art", lambda: None)
    persona.install(db, NOW)
    assert dict(db.execute("SELECT read_at IS NOT NULL, COUNT(*) FROM NOTIFICATION GROUP BY 1")) == {0: 14, 1: 7}
    for suffix in ("123", "126", "128", "133", "200"):
        user = user_id("tci-000" + suffix)
        assert db.execute("""SELECT 1 FROM NOTIFICATION n WHERE user_id=? AND (
                             visit_id IS NOT NULL OR watch_flag_id IS NOT NULL OR EXISTS (
                             SELECT 1 FROM STAFF_RESPONSE s WHERE s.case_id=n.case_id))""", (user,)).fetchone()
    responses = db.execute("""SELECT n.created_at,s.sent_at,n.read_at,s.responder_role FROM NOTIFICATION n
                              JOIN STAFF_RESPONSE s ON s.case_id=n.case_id AND s.sent_at=n.created_at
                              WHERE n.title LIKE '% responded to your %'""").fetchall()
    assert Counter((r["responder_role"], r["read_at"] is not None) for r in responses) == {
        ("Doctor", False): 2, ("Nurse", False): 1, ("Nurse", True): 1,
    }
    assert all(r["created_at"] == r["sent_at"] for r in responses)
    assert not db.execute("""SELECT 1 FROM NOTIFICATION n JOIN VISIT v USING(visit_id)
                             WHERE n.user_id<>v.user_id OR substr(n.created_at,1,10)<v.visit_date""").fetchone()
    anh = user_id("tci-000133")
    assert db.execute("SELECT read_at FROM NOTIFICATION WHERE user_id=? AND type='Appointment'", (anh,)).fetchone()[0] is None
    assert dict(db.execute("SELECT status, COUNT(*) FROM CARE_CASE GROUP BY status")) == {
        "Not viewed": 2, "Viewed": 1, "Escalated to doctor": 3, "Resolved": 4,
    }
