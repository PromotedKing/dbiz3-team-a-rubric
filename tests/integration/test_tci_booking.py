import html
import re
from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from mb360 import clock, persona, tci_booking
from mb360.main import create_app

NOW = datetime(2026, 11, 14, 10)


@pytest.fixture
def host(db, monkeypatch):
    clock.set(NOW)
    monkeypatch.setattr(persona, "_copy_art", lambda: None)
    persona.install(db, NOW)
    with TestClient(create_app(db), follow_redirects=False) as client:
        yield client


def booking_form(db, **overrides):
    doctor = db.execute("SELECT staff_id FROM STAFF WHERE full_name='Nguyễn Văn A'").fetchone()[0]
    return {"day": "2026-11-16", "time": "10:00", "doctor": doctor, "mode": "doctor",
            "facility": tci_booking.FACILITY, "specialty": tci_booking.SPECIALTY,
            "reason": "Khám thai mẫu", **overrides}


def draft(host, data):
    page = host.post("/tci/booking", data=data)
    assert page.status_code == 200
    return dict((name, html.unescape(value)) for name, value in re.findall(
        r'name="(payload|signature)" value="([^"]+)"', page.text))


def sign_in(host, db, user):
    identity = dict(db.execute("SELECT * FROM USER_ACCOUNT WHERE user_id=?", (user,)).fetchone())
    assert host.post("/tci/open", data={k: v for k,v in identity.items() if v is not None}).status_code == 303


def test_booking_replay_conflicts_and_owned_cancellation(host, db, user_id):
    form = booking_form(db)
    confirm = draft(host, form)
    confirm.update(reminder_enabled="on", reminder_day="2026-11-15", reminder_time="09:00")
    for _ in range(2):
        response = host.post("/tci/booking/confirm", data=confirm)
        assert response.status_code == 303 and response.headers["location"] == "/tci/appointments"
    appointment, = db.execute(f"SELECT * FROM {tci_booking.TABLE} WHERE reason=?", (form["reason"],)).fetchall()
    assert (appointment["status"], appointment["reminder_at"]) == ("Confirmed", "2026-11-15 09:00")
    assert "Đã xác nhận" in host.get("/tci/appointments").text
    other_doctor = db.execute("SELECT staff_id FROM STAFF WHERE full_name='Phạm Quốc Dũng'").fetchone()[0]
    assert host.post("/tci/booking/confirm", data=draft(host, {**form, "doctor": other_doctor})).status_code == 409
    url = f"/tci/appointments/{appointment['appointment_id']}/cancel"
    sign_in(host, db, user_id("tci-000123"))
    assert form["reason"] not in host.get("/tci/appointments").text
    assert host.post(url).status_code == 404
    assert host.post("/tci/booking/confirm", data=confirm).status_code == 403
    assert host.post("/tci/booking/confirm", data=draft(host, form)).status_code == 409
    host.cookies.delete("tci_demo_account")
    assert host.post(url).status_code == 303
    assert "Đã hủy" in host.get("/tci/appointments?tab=history").text
    assert host.post(url).status_code == 409


@pytest.mark.parametrize("day,time", [("2026-11-14","09:00"), ("2026-11-15","06:59"),
                                      ("2026-11-15","20:01"), ("2026-12-15","09:00")])
def test_booking_rejects_invalid_slot(host, db, day, time):
    assert host.post("/tci/booking", data=booking_form(db, day=day, time=time)).status_code == 422


def test_host_history_matches_visits_and_empty_tabs(host, db, user_id):
    rows = db.execute(f"SELECT * FROM {tci_booking.TABLE} WHERE status='Completed'").fetchall()
    assert len(rows) == 22
    for row in rows:
        visit = db.execute("SELECT user_id,visit_date FROM VISIT WHERE visit_id=?", (row["visit_id"],)).fetchone()
        assert tuple(visit) == (row["user_id"], row["appointment_at"][:10])
    assert db.execute(f"SELECT COUNT(*) FROM {tci_booking.TABLE} WHERE status='Confirmed'").fetchone()[0] == 3
    sign_in(host, db, user_id("tci-000123"))
    assert "Bạn chưa có lịch hẹn nào!" in host.get("/tci/appointments").text
    assert "Đã khám" in host.get("/tci/appointments?tab=history").text
    sign_in(host, db, user_id("tci-000133"))
    assert "Bạn chưa có lịch hẹn nào!" in host.get("/tci/appointments?tab=history").text
    clock.set(datetime(2026, 11, 15, 10))
    assert "Đã qua giờ hẹn, chưa ghi nhận lần khám." in host.get("/tci/appointments?tab=history").text


@pytest.mark.parametrize("hour,minute,expected", [(10,0,"16:00"), (16,10,"17:10"), (19,30,"20:00"), (20,15,"20:00")])
def test_same_day_slot_is_deterministic(hour, minute, expected):
    now = NOW.replace(hour=hour, minute=minute)
    assert tci_booking.same_day_slot(now).strftime("%H:%M") == expected

def test_mb360_appointments_round_trip(host, db, user_id):
    for suffix, current_count, history_count in (("123", 0, 6), ("126", 0, 2), ("128", 1, 9), ("133", 1, 0), ("200", 1, 5)):
        user = user_id("tci-000" + suffix)
        # The runtime persona starts with consent pending; use its demo session.
        from mb360.acc import entry
        if suffix == "200":
            entry._new_session(db, user, NOW)
            db.commit()
            host.cookies.set(entry.COOKIE, entry.latest_session(db, user))
        else:
            sign_in(host, db, user)
        path = f"/m/{user}/appointments"
        current = host.get(path)
        history = host.get(path + "?tab=history")
        assert current.status_code == history.status_code == 200
        assert current.text.count('<article') == current_count
        assert history.text.count("Xem kết quả") == history_count
        assert "data-back" in current.text and '<nav class="tabs"' not in current.text
        assert "/tci/booking?source=mb360" in current.text
        home = host.get(f"/m/{user}/home")
        if suffix != "200":
            assert path in home.text
            assert ("Chưa có lịch sắp tới" in home.text) == (current_count == 0)
    host.cookies.delete(entry.COOKIE)
    user = user_id("tci-000123")
    sign_in(host, db, user)
    path = f"/m/{user}/appointments"
    assert host.get(f"/m/{user_id('tci-000133')}/appointments").status_code == 404
    assert "/tci/appointments?source=mb360" in host.get(path).text
    management = host.get("/tci/appointments?source=mb360")
    assert management.status_code == 303 and management.headers["location"] == "/tci/appointments"
    assert path in host.get("/tci/appointments").text
    assert host.get("/tci/booking?source=mb360&return=https://example.invalid").status_code == 200
    form = draft(host, booking_form(db))
    form.update(reminder_enabled="on", reminder_day="2026-11-14", reminder_time="10:00")
    assert host.post("/tci/booking/confirm", data=form).status_code == 303
    assert path in host.get("/tci/appointments").text
    assert "example.invalid" not in host.get("/tci/appointments").text
    appointment = db.execute(f"SELECT appointment_id FROM {tci_booking.TABLE} WHERE reason='Khám thai mẫu'").fetchone()[0]
    assert appointment in host.get(path).text
    host.get(f"/m/{user}/home")
    notice = db.execute("SELECT notification_id FROM NOTIFICATION WHERE appointment_ref=?", (appointment,)).fetchone()[0]
    assert host.get(f"/m/{user}/notices/{notice}").headers["location"].endswith(f"#appointment-{appointment}")
    assert host.post(f"/tci/appointments/{appointment}/cancel").status_code == 303
    assert "Đã hủy" in host.get(path + "?tab=history").text
    host.get(f"/m/{user}/home")
    assert db.execute("SELECT COUNT(*) FROM NOTIFICATION WHERE appointment_ref=?", (appointment,)).fetchone()[0] == 1
