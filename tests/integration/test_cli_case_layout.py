"""D-103 look of S-064 / S-064D: one two-column case page for both roles — the case and its actions on the left,
the mother's context on the right. Look only: the content, the rules and the labels are the same as before."""
from mb360.cli import dashboard

from tests.cli_helpers import RPT002, case_by_code
from tests.integration.helpers import vi


def test_case_page_has_the_case_on_the_left_and_the_mother_on_the_right(client, db, staff_id, boundary_case):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    assert page.index("case-main") < page.index("case-report") < page.index("case-side")
    left, right = page.split('<aside class="case-side"')
    assert vi("Mark as viewed") in left and vi("Escalate to doctor") in left and vi("Send guidance to the mother") in left
    for text in (vi("Latest visit"), vi("Medical history"), vi("Obstetric history (PARA)"), vi("Visit history")):
        assert text in right, text
    assert vi("Mark as viewed") not in right


def test_an_above_threshold_case_is_marked_urgent_and_a_normal_one_is_not(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    assert "case-report urgent" in client.get(f"/staff/{nurse}/cases/{boundary_case}").text
    normal = db.execute("""SELECT c.case_id FROM CARE_CASE c JOIN METRIC_REPORT r ON r.report_id = c.metric_report_id
                           WHERE c.status = 'Not viewed' AND r.health_metric_record_id IS NULL""").fetchone()
    if normal is not None:       # a symptom report with no alarm symptom
        page = client.get(f"/staff/{nurse}/cases/{normal[0]}").text
        assert ("case-report urgent" in page) == any(
            s in dashboard.ALARM_SYMPTOMS for (s,) in db.execute(
                "SELECT symptom FROM REPORT_SYMPTOM WHERE report_id = (SELECT metric_report_id FROM CARE_CASE WHERE case_id = ?)", (normal[0],)))


def test_the_page_shows_how_many_other_open_cases_the_mother_has(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    for user, open_n in db.execute("SELECT user_id, SUM(status != 'Resolved') FROM CARE_CASE GROUP BY user_id"):
        for (case_id,) in db.execute("SELECT case_id FROM CARE_CASE WHERE user_id = ? AND status != 'Resolved'", (user,)).fetchall():
            page = client.get(f"/staff/{nurse}/cases/{case_id}").text
            if open_n > 1:
                assert "data-other-cases" in page and vi("Other open cases of this mother: {n}", n=open_n - 1) in page
            else:
                assert "data-other-cases" not in page


def test_doctor_keeps_the_same_page_with_the_instruction_form(client, db, staff_id, boundary_case):
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases/{case_by_code(db, RPT002)}").text
    assert "case-grid" in page and "data-instruction-form" in page and "data-responsible" in page
    assert vi("Mark as viewed") not in page             # S-064D: no nurse buttons


# ---------------------------------------------------------------- colour by stage (23/11 review): look only

def test_every_card_row_and_tag_carries_the_colour_of_its_stage(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    classes = {"Not viewed": "s-new", "Viewed": "s-seen", "Escalated to doctor": "s-esc", "Resolved": "s-done"}
    board = client.get(f"/staff/{nurse}/board").text
    listing = client.get(f"/staff/{nurse}/cases", params={"status": "All"}).text
    for case_id, status in db.execute("SELECT case_id, status FROM CARE_CASE"):
        for page in (board, listing):
            chunk = page[page.index(case_id) - 400: page.index(case_id) + 50]
            assert classes[status] in chunk, (case_id, status)


def test_overview_has_the_colour_key_and_the_stacked_bar(client, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/dashboard").text
    assert "data-color-key" in page and 'class="stack"' in page
    for text in (vi("Red: above threshold, alarm symptoms"), vi("Amber: waiting for the nurse"),
                 vi("Blue: waiting for the doctor"), vi("Green: done"), vi("Open case")):
        assert text in page, text


def test_nurse_history_is_one_click_away_and_the_doctor_keeps_it_open(client, db, staff_id, boundary_case):
    nurse = client.get(f"/staff/{staff_id('Trần Thị B')}/cases/{boundary_case}").text
    doctor = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases/{case_by_code(db, RPT002)}").text
    assert "data-history-collapsed" in nurse and "140/90 mmHg" in nurse       # still on the page, collapsed
    assert "data-history-collapsed" not in doctor
