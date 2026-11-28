"""T-DN01 — fixture S06: staff with padded full_name must never show 'sample text' in the UI.

Covers:
- Staff header on the clinical web (staff_base.html)
- Report-status progress page on the mother app (alr/status.py _actor, S-026)
"""
import pytest

# S06 nurse: fadedc75 — full_name padded to 100 chars with ' sample text …'
S06_STAFF_ID = "fadedc75-d27b-5ef7-b51f-d633f8dca42d"
S06_REAL_NAME = "Nguyễn Thị Minh Châu"
SAMPLE_MARKER = "sample text"


# ── helpers ──────────────────────────────────────────────────────────────────

def _any_nurse_case(db):
    """Return any Not-viewed case_id (from seed) so the nurse can mark it as viewed."""
    row = db.execute(
        "SELECT case_id FROM CARE_CASE WHERE status = 'Not viewed' AND metric_report_id IS NOT NULL LIMIT 1"
    ).fetchone()
    assert row, "Seed must have at least one Not-viewed case"
    return row[0]


def _user_id_for_case(db, case_id: str) -> str:
    return db.execute(
        "SELECT user_id FROM CARE_CASE WHERE case_id = ?", (case_id,)
    ).fetchone()[0]


# ── tests ─────────────────────────────────────────────────────────────────────

def test_staff_header_does_not_show_sample_text(client):
    """The clinical-web header must show only the real name, not the fixture padding."""
    page = client.get(f"/staff/{S06_STAFF_ID}/dashboard").text
    assert SAMPLE_MARKER not in page, (
        f"Header still contains '{SAMPLE_MARKER}' — display_name() not applied to staff_base.html"
    )
    assert S06_REAL_NAME in page, (
        f"Header must still show the real name '{S06_REAL_NAME}'"
    )


def test_staff_select_does_not_show_sample_text(client):
    """The staff picker (/staff) must not expose the fixture padding."""
    page = client.get("/staff").text
    assert SAMPLE_MARKER not in page, (
        f"Staff picker still contains '{SAMPLE_MARKER}'"
    )
    assert S06_REAL_NAME in page


def test_report_status_progress_does_not_show_sample_text(client, db):
    """After S06 views and escalates a case, the mother's S-026 progress page
    must show only the real name, not 'sample text'."""
    case_id = _any_nurse_case(db)
    user = _user_id_for_case(db, case_id)

    # S06 marks as viewed
    r = client.post(f"/staff/{S06_STAFF_ID}/cases/{case_id}/view")
    assert r.status_code in (200, 302, 303), f"view POST failed: {r.status_code}"

    # Mother opens S-026 (report status page)
    report = db.execute("SELECT metric_report_id FROM CARE_CASE WHERE case_id = ?", (case_id,)).fetchone()[0]
    page = client.get(f"/m/{user}/reports/{report}").text
    assert f"{S06_REAL_NAME} {SAMPLE_MARKER}" not in page, (
        f"S-026 progress still contains '{SAMPLE_MARKER}' — display_name() not applied to alr/status.py"
    )
    assert S06_REAL_NAME in page, (
        f"S-026 progress must show the real name '{S06_REAL_NAME}'"
    )


def test_case_responses_do_not_show_sample_text(client, db):
    """When S06 sends guidance, the clinical case page must not show 'sample text' next to the name."""
    case_id = _any_nurse_case(db)

    # S06 marks as viewed first
    client.post(f"/staff/{S06_STAFF_ID}/cases/{case_id}/view")

    # Send guidance (requires a template; use an existing one from seed)
    tpl = db.execute("SELECT template_id FROM GUIDANCE_TEMPLATE LIMIT 1").fetchone()
    if tpl:
        r = client.post(
            f"/staff/{S06_STAFF_ID}/cases/{case_id}/guidance",
            data={"template_id": tpl[0], "custom_text": ""},
        )
        assert r.status_code in (200, 302, 303)

    page = client.get(f"/staff/{S06_STAFF_ID}/cases/{case_id}").text
    assert f"{S06_REAL_NAME} {SAMPLE_MARKER}" not in page, (
        f"Case page still shows '{SAMPLE_MARKER}' in response author — display_name filter not applied"
    )


def test_display_name_unit():
    """Unit test: ui.display_name strips padding and handles None gracefully."""
    from mb360 import ui

    assert ui.display_name("Nguyễn Thị Minh Châu sample text sample text") == "Nguyễn Thị Minh Châu"
    assert ui.display_name("Trần Thị B") == "Trần Thị B"
    assert ui.display_name(None) == ""
    assert ui.display_name("") == ""
    assert ui.display_name("No padding here") == "No padding here"
