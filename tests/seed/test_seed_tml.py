"""T002 — TML facts of the seed (checked with queries before writing)."""
from mb360 import db as dbmod


def _lan(conn):
    return conn.execute("SELECT user_id FROM USER_ACCOUNT WHERE tci_account_ref = 'tci-000123'").fetchone()[0]


def test_lan_profile_and_visits():
    conn = dbmod.build()
    lan = _lan(conn)
    assert conn.execute("SELECT edd FROM PREGNANCY_PROFILE WHERE user_id = ?", (lan,)).fetchone()[0] == "2026-12-20"
    visits = [tuple(r) for r in conn.execute(
        """SELECT visit_date, gestational_week, ultrasound_image, fetal_length, estimated_fetal_weight, ultrasound_report_date
           FROM VISIT WHERE user_id = ? ORDER BY visit_date""", (lan,))]
    assert visits == [("2026-08-18", 22, "us/VIS-002.jpg", 27, 480, "2026-08-18"), ("2026-09-15", 26, None, None, None, None)]


def test_lan_diary_and_messages():
    conn = dbmod.build()
    lan = _lan(conn)
    diary = [tuple(r) for r in conn.execute(
        """SELECT gestational_week, mood, (SELECT COUNT(*) FROM DIARY_IMAGE i WHERE i.diary_id = d.diary_id)
           FROM DIARY_ENTRY d WHERE user_id = ? ORDER BY entry_date, mood DESC""", (lan,))]
    assert diary == [(22, "Nervous", 1), (28, "Happy", 1), (28, "Calm", 1)]
    msgs = [tuple(r) for r in conn.execute("SELECT week, author FROM FAMILY_MESSAGE WHERE user_id = ? ORDER BY created_at", (lan,))]
    assert msgs == [(28, "Mother"), (28, "Father")]
