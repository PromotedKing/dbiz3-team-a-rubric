"""Part A: demo timing/Q4 assumptions only; no real TCI integration."""
from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from mb360 import appointment_demo, clock, db as dbmod, persona, tci_feed
from mb360.acc import notices
from mb360.main import create_app

NOW = datetime(2026, 11, 10, 10, 0)


@pytest.fixture
def demo(db, user_id):
    clock.set(NOW)
    persona.install(db, NOW)
    app = create_app(db)
    return TestClient(app, follow_redirects=False), user_id('tci-000133'), user_id('tci-000126')


def test_accounts_open_home_with_tomorrow_card_and_no_appointment_case(demo, db):
    client, mother, empty = demo
    accounts = client.get('/tci/accounts')
    assert accounts.status_code == 200
    expected = {'tci-000123', 'tci-000126', 'tci-000128', 'tci-000133', 'tci-000200'}
    assert {r[0] for r in db.execute('SELECT tci_account_ref FROM USER_ACCOUNT')} == expected
    assert all(ref in accounts.text for ref in expected)
    for suffix in (124, 125, 127, 129, 130, 131, 132, 134):
        assert f'tci-{suffix:06d}' not in accounts.text
    for user, ref in ((mother, 'tci-000133'), (empty, 'tci-000126')):
        assert ref in accounts.text
        identity = dict(db.execute('SELECT * FROM USER_ACCOUNT WHERE user_id=?', (user,)).fetchone())
        opened = client.post('/tci/open', data={k: v for k, v in identity.items() if v is not None})
        assert opened.status_code == 303 and opened.headers['location'] == f'/m/{user}/home'
        assert client.get(opened.headers['location']).status_code == 200
    page = client.get(f'/m/{mother}/home').text
    assert 'data-appointment' in page and 'Còn 1 ngày' in page and '11/11/2026 · 09:00' in page
    assert tci_feed.next_appointment(db, empty, NOW) is None
    assert 'data-appointment' not in client.get(f'/m/{empty}/home').text
    assert not notices.list_for(db, empty, 'Appointment')


def test_appointment_filter_read_and_list_redirect(demo, db):
    client, mother, _ = demo
    row, = notices.list_for(db, mother, 'Appointment')
    assert row['read_at'] is None and row['appointment_ref']
    page = client.get(f'/m/{mother}/notices?type=Appointment')
    assert page.status_code == 200 and page.text.count('data-notice') == 1
    assert 'ngày mai 11/11/2026' in page.text
    opened = client.get(f"/m/{mother}/notices/{row['notification_id']}")
    assert opened.status_code == 303 and opened.headers['location'] == f"/m/{mother}/appointments?tab=current#appointment-{row['appointment_ref']}"
    assert notices.list_for(db, mother, 'Appointment')[0]['read_at'] == '2026-11-10 10:00'
    client.get(f'/m/{mother}/home')
    appointment_demo.install(db, NOW)
    assert len(notices.list_for(db, mother, 'Appointment')) == 1
    assert all(row['read_at'] for row in notices.list_for(db, mother, 'Appointment'))


def test_switch_off_stops_new_reminders_but_keeps_received_notices(demo, db):
    client, mother, _ = demo
    assert 'appointment_reminder' in client.get(f'/m/{mother}/settings/notifications').text
    assert db.execute('SELECT appointment_reminder FROM NOTIFICATION_PREFERENCE WHERE user_id=?', (mother,)).fetchone()[0] == 1
    path = f'/m/{mother}/settings/notifications'
    assert client.post(path, data={'key': 'appointment_reminder', 'value': '0'}).status_code == 303
    # Simulate a NEW appointment in the host feed, due tomorrow on the following day.
    db.execute(f'UPDATE {tci_feed.APPOINTMENTS} SET appointment_at=?, reminder_at=? WHERE user_id=?', ('2026-11-12 09:00', '2026-11-11 00:00', mother))
    db.commit()
    clock.set(NOW + timedelta(days=1))
    appointment_demo.install(db, clock.now())  # a restart must not turn the switch back on
    client.get(f'/m/{mother}/home')
    page = client.get(f'/m/{mother}/notices?type=Appointment').text
    assert len(notices.list_for(db, mother, 'Appointment')) == 1
    assert 'ngày mai 11/11/2026' in page
    assert client.post(path, data={'key': 'appointment_reminder', 'value': '1'}).status_code == 303
    client.get(f'/m/{mother}/notices?type=Appointment')
    client.get(f'/m/{mother}/home')
    assert len(notices.list_for(db, mother, 'Appointment')) == 2


@pytest.mark.parametrize('when', [NOW, datetime(2027, 1, 31, 23, 59), datetime(2028, 2, 28, 0, 0)])
def test_fresh_deploy_uses_relative_dates_and_never_creates_appointment_table(db, user_id, when):
    db.execute(tci_feed.DDL)
    appointment_demo.install(db, when)
    mother = user_id('tci-000133')
    assert tci_feed.next_appointment(db, mother, when)['days'] == 1
    notice, = notices.list_for(db, mother, 'Appointment')
    assert (when.date() + timedelta(days=1)).strftime('%d/%m/%Y') in notice['subtitle']
    names = {r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
    assert len(names) == 28 and not any(name.startswith('APPOINTMENT') for name in names)


def test_existing_demo_database_upgrade_and_reopen_are_idempotent(db, user_id, tmp_path):
    ids = (user_id('tci-000133'), user_id('tci-000126'))
    db.execute("UPDATE PREGNANCY_PROFILE SET edd='2026-12-01' WHERE user_id=?", (ids[1],))
    control_profile = tuple(db.execute('SELECT * FROM PREGNANCY_PROFILE WHERE user_id=?', (ids[1],)).fetchone())
    for table in ('CONSENT_RECORD', 'PREGNANCY_PROFILE', 'NOTIFICATION_PREFERENCE', 'USER_ACCOUNT'):
        db.execute(f'DELETE FROM {table} WHERE user_id=?', (ids[0],))
    db.execute(tci_feed.DDL)
    appointment_demo.install(db, NOW)
    original = [tuple(r) for r in db.execute(f'SELECT * FROM {tci_feed.TABLE} ORDER BY user_id')]
    assert len(original) == 2
    assert tci_feed.hospital_edd(db, ids[1]) == '2026-12-01'
    assert tuple(db.execute('SELECT * FROM PREGNANCY_PROFILE WHERE user_id=?', (ids[1],)).fetchone()) == control_profile
    file = tmp_path / 'demo.sqlite'
    target = dbmod.open_file(str(file))
    db.backup(target)
    target.close()
    reopened = dbmod.open_file(str(file))
    try:
        appointment_demo.install(reopened, NOW + timedelta(hours=1))
        assert [tuple(r) for r in reopened.execute(f'SELECT * FROM {tci_feed.TABLE} ORDER BY user_id')] == original
        assert len(notices.list_for(reopened, ids[0], 'Appointment')) == 1
        assert tuple(reopened.execute('SELECT * FROM PREGNANCY_PROFILE WHERE user_id=?', (ids[1],)).fetchone()) == control_profile
        assert not reopened.execute('PRAGMA foreign_key_check').fetchall()
    finally:
        reopened.close()


def test_plain_seed_has_no_host_appointments(client, db):
    assert not db.execute("SELECT 1 FROM sqlite_master WHERE name=?", (tci_feed.TABLE,)).fetchone()

def test_fresh_demo_profiles_and_appointments(db, user_id, monkeypatch):
    when = datetime(2026, 11, 13, 10)
    monkeypatch.setattr(persona, "_copy_art", lambda: None)
    persona.install(db, when)
    expected = {
        "tci-000123": ("2027-01-04", None, "2026-11-02 09:00"),
        "tci-000126": ("2027-05-17", None, None),
        "tci-000128": ("2026-11-16", None, "2026-11-13 16:00"),
        "tci-000133": ("2027-07-05", "2026-09-28", "2026-11-14 09:00"),
        "tci-000200": ("2027-03-01", None, "2026-11-20 08:30"),
    }
    for ref, (edd, lmp, appointment) in expected.items():
        uid = user_id(ref)
        host = db.execute(f"SELECT * FROM {tci_feed.TABLE} WHERE user_id=?", (uid,)).fetchone()
        assert (host["hospital_edd"], host["next_appointment"]) == (edd, appointment)
        if ref != persona.TCI_REF:
            profile = db.execute("SELECT edd, lmp, first_visit_date FROM PREGNANCY_PROFILE WHERE user_id=?", (uid,)).fetchone()
            first = db.execute("SELECT MIN(visit_date) FROM VISIT WHERE user_id=?", (uid,)).fetchone()[0]
            assert tuple(profile) == (edd, lmp, first)
    huong = user_id("tci-000128")
    assert db.execute("SELECT appointment_reminder FROM NOTIFICATION_PREFERENCE WHERE user_id=?", (huong,)).fetchone()[0] == 0
    assert not notices.list_for(db, huong, "Appointment")
    assert [r[0] for r in db.execute("SELECT gestational_week FROM VISIT WHERE user_id=? ORDER BY visit_date", (huong,))] == [8, 12, 16, 21, 27, 31, 36, 38, 39]
    assert db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id=? AND status='Escalated to doctor'", (huong,)).fetchone()[0] == 1
    anh = user_id("tci-000133")
    assert db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE user_id=? AND case_source='Chatbot' AND status='Viewed'", (anh,)).fetchone()[0] == 1
    assert db.execute("SELECT COUNT(*) FROM VISIT WHERE user_id=?", (anh,)).fetchone()[0] == 0
    assert not db.execute("PRAGMA foreign_key_check").fetchall()
    assert tci_feed.next_appointment(db, huong, when)["days"] == 0
    assert tci_feed.next_appointment(db, user_id("tci-000123"), when) is None
