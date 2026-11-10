"""T003 — S-103, S-011, S-010, S-009 pages and routes (specs/009-acc-profile/contracts/http-routes.md)."""
from tests.integration.helpers import bp_form, vi


def test_profile_page(client, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/profile").text
    for t in ("Nguyễn Thị Lan", "TC-00123", vi("Due date"), "20/12/2026", vi("Hospital record link"), vi("Doctor's instructions"),
              vi("Blood pressure"), vi("Blood glucose"), vi("Data sharing consent"), vi("Agreed"), vi("Notification settings")):
        assert t in page, t
    for href in ("profile/edit", "instructions", "settings/notifications"):
        assert f'href="/m/{lan}/{href}"' in page, href
    assert "<input" not in page                              # read-only view (FR-023)
    for absent in ("Log out", "Đăng xuất", "password", "Mật khẩu"):
        assert absent not in page                            # S-103 SR-001


def test_edit_page_and_save(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/profile/edit").text
    assert "Nguyễn Thị Lan" in page and "•••" in page and vi("Save changes") in page and vi("Cancel") in page
    assert 'name="full_name"' not in page and 'name="phone"' not in page     # edited in the TCI app (S-011 SR-001)
    r = client.post(f"/m/{lan}/profile/edit", data={"height_cm": "161.5"})
    assert r.status_code == 303 and r.headers["location"] == f"/m/{lan}/profile?saved=1"
    assert vi("Changes saved") in client.get(r.headers["location"]).text
    assert float(db.execute("SELECT height_cm FROM PREGNANCY_PROFILE WHERE user_id = ?", (lan,)).fetchone()[0]) == 161.5


def test_edit_errors_stay_on_the_form(client, user_id):
    lan = user_id("tci-000123")
    r = client.post(f"/m/{lan}/profile/edit", data={"height_cm": "tall"})
    assert r.status_code == 422 and 'data-error-for="height_cm"' in r.text and 'value="tall"' in r.text


def test_linked_due_date_is_read_only_and_pending_is_editable(client, user_id):
    linked, pending = user_id("tci-000123"), user_id("tci-000131")
    assert 'name="edd"' not in client.get(f"/m/{linked}/profile/edit").text
    assert 'name="edd"' in client.get(f"/m/{pending}/profile/edit").text


def test_settings_page_and_toggle(client, db, user_id):
    lan = user_id("tci-000123")
    page = client.get(f"/m/{lan}/settings/notifications").text
    assert vi("Report responses") in page and vi("New visit results") in page and vi("Doctor's-instruction reminders") in page
    assert vi("Appointment reminders") in page                    # Màn 25; appointments are held by the TCI app (D-81)
    r = client.post(f"/m/{lan}/settings/notifications", data={"key": "watch_flag_reminder", "value": "1"})
    assert r.status_code == 303
    assert db.execute("SELECT watch_flag_reminder FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (lan,)).fetchone()[0] == 1
    assert client.post(f"/m/{lan}/settings/notifications", data={"key": "report_response", "value": "0"}).status_code == 422
    assert db.execute("SELECT report_response FROM NOTIFICATION_PREFERENCE WHERE user_id = ?", (lan,)).fetchone()[0] == 1


def test_notices_list_filter_open_and_badge(client, db, user_id):
    lan = user_id("tci-000123")
    db.execute("DELETE FROM NOTIFICATION WHERE user_id = ?", (lan,))
    client.post(f"/m/{lan}/report", data=bp_form(150, 95, ["No symptoms"]))     # ALR FR-018 writes one
    page = client.get(f"/m/{lan}/notices").text
    assert page.count("data-notice") == 1 and '<span class="badge" data-unread>1</span>' in page
    assert vi("{n} unread notifications", n=1) not in page and vi("Mark all as read") in page
    assert client.get(f"/m/{lan}/notices", params={"type": "Visit result"}).text.count("data-notice") == 0
    assert client.get(f"/m/{lan}/notices", params={"type": "Report"}).text.count("data-notice") == 1
    assert vi("Your Blood pressure report has been sent to clinical staff") in page or "Huyết áp" in page
    assert client.get(f"/m/{lan}/notices", params={"type": "Unread"}).text.count("data-notice") == 1

    nid = db.execute("SELECT notification_id FROM NOTIFICATION WHERE user_id = ?", (lan,)).fetchone()[0]
    r = client.get(f"/m/{lan}/notices/{nid}")
    assert r.status_code == 303 and "/reports/" in r.headers["location"]
    page = client.get(f"/m/{lan}/notices").text
    assert "data-unread" not in page and vi("Read") in page


def test_mark_all_and_empty_state(client, db, user_id):
    lan = user_id("tci-000123")
    r = client.post(f"/m/{lan}/notices/read-all")
    assert r.status_code == 303 and r.headers["location"] == f"/m/{lan}/notices"
    assert "data-unread" not in client.get(f"/m/{lan}/notices").text
    db.execute("DELETE FROM NOTIFICATION WHERE user_id = ?", (lan,))
    assert vi("You have no notifications.") in client.get(f"/m/{lan}/notices").text


def test_notice_of_another_mother_is_404(client, db, user_id):
    lan, other = user_id("tci-000123"), user_id("tci-000131")
    db.execute("DELETE FROM NOTIFICATION WHERE user_id = ?", (other,))
    client.post(f"/m/{other}/report", data=bp_form(150, 95, ["No symptoms"]))
    nid = db.execute("SELECT notification_id FROM NOTIFICATION WHERE user_id = ?", (other,)).fetchone()[0]
    assert client.get(f"/m/{lan}/notices/{nid}").status_code == 404


def test_no_alert_word_on_the_notification_list(client, db, user_id):
    lan = user_id("tci-000123")
    client.post(f"/m/{lan}/report", data=bp_form(150, 95, ["No symptoms"]))
    page = client.get(f"/m/{lan}/notices").text
    assert vi("Alert") not in page and "alert" not in page.lower()         # S-009 SR-002


def test_notification_filters_keep_both_selections(client, db, user_id):
    lan = user_id("tci-000123")
    db.execute("DELETE FROM NOTIFICATION WHERE user_id = ?", (lan,))
    client.post(f"/m/{lan}/report", data=bp_form(150, 95, ["No symptoms"]))
    page = client.get(f"/m/{lan}/notices?type=Report&unread=1").text
    assert page.count("data-notice") == 1
    assert '<option value="Report" selected>' in page
    assert 'unread=1&amp;type=Report' in page
    assert '<input type="hidden" name="unread" value="1">' in page
    assert '<span class="tag inf">' + vi("Report") + '</span>' in page
    assert vi("Above threshold") in page
    db.execute("UPDATE NOTIFICATION SET read_at = '2026-09-27 12:00' WHERE user_id = ?", (lan,))
    db.commit()
    assert client.get(f"/m/{lan}/notices?type=Report&unread=1").text.count("data-notice") == 0
    assert client.get(f"/m/{lan}/notices?type=Report").text.count("data-notice") == 1
