"""T018 — ALR FR-007, BR-002, BR-010, BR-013, BR-014 (S-028 "Metric alert")."""
import re

from .helpers import bp_form, case_of, latest_report


def _guidance(db, uid, metric):
    row = db.execute("""SELECT t.content FROM WATCH_FLAG w JOIN GUIDANCE_TEMPLATE t ON t.template_id = w.template_id
                        WHERE w.user_id = ? AND w.metric = ? AND w.active = 1""", (uid, metric)).fetchone()
    return row[0] if row else None


def test_metric_alert_shows_value_threshold_and_instruction_guidance(client, db, user_id):
    u01 = user_id("tci-000123")
    r = client.post(f"/m/{u01}/report", data=bp_form(150, 95, ["No symptoms"]))
    page = client.get(r.headers["location"]).text
    assert "Metric alert" in page
    assert "150/95 mmHg" in page and "27/09/2026 · 09:00" in page and "140/90 mmHg" in page
    assert "Your report has been sent to clinical staff" in page
    assert _guidance(db, u01, "Blood pressure") in page   # W01 -> template G02


def test_default_template_when_instruction_has_no_guidance(client, db, user_id):
    u04 = user_id("tci-000126")  # W07: no template, no custom text (BR-013)
    r = client.post(f"/m/{u04}/report", data=bp_form(150, 95, ["No symptoms"]))
    default = db.execute("SELECT content FROM GUIDANCE_TEMPLATE WHERE is_default = 1").fetchone()[0]
    assert default in client.get(r.headers["location"]).text


def test_word_alert_only_on_the_metric_alert_page(client, user_id):
    u09 = user_id("tci-000131")
    pages = [f"/m/{u09}/instructions", f"/m/{u09}/report?metric=Blood%20pressure", f"/m/{u09}/report?metric=Symptom", "/"]
    r = client.post(f"/m/{u09}/report", data=bp_form(120, 80, ["Palpitations"]))
    pages.append(r.headers["location"])                                  # S-026
    for p in pages:
        assert "alert" not in client.get(p).text.lower(), p


def test_close_returns_to_instructions_and_keeps_the_report(client, db, user_id):
    u09 = user_id("tci-000131")
    r = client.post(f"/m/{u09}/report", data=bp_form(160, 100, ["No symptoms"]))
    page = client.get(r.headers["location"]).text
    close = re.search(r'<a[^>]*href="([^"]+)"[^>]*>\s*Close\s*</a>', page)
    assert close and close.group(1) == f"/m/{u09}/instructions"
    rep = latest_report(db, u09)
    assert client.get(close.group(1)).status_code == 200
    assert case_of(db, rep["report_id"])["status"] == "Not viewed"
