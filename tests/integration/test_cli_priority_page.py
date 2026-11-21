"""D-104 on S-061: Priority is the nurse's default, "Waiting" is a nurse column, "(n)" is the count of "Not viewed"."""
import re

from tests.integration.helpers import vi


def test_nurse_list_opens_on_priority_with_a_waiting_column(client, staff_id):
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases").text
    assert f'data-sort="Priority"' in page and re.search(r'class="chip sm on" data-sort="Priority"', page)
    assert f"<th>{vi('Waiting')}</th>" in page
    assert "data-waiting" in page


def test_priority_order_starts_with_above_threshold_not_viewed(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")                 # boundary_case: 140/90 submitted 07:02, not viewed, above threshold
    page = client.get(f"/staff/{nurse}/cases", params={"status": "All"}).text
    assert page.index(f"/cases/{boundary_case}") < page.index('class="tag status done"')   # before every resolved row
    first = re.search(rf'href="/staff/{nurse}/cases/([0-9a-f-]{{36}})"', page).group(1)
    assert db.execute("SELECT status FROM CARE_CASE WHERE case_id = ?", (first,)).fetchone()[0] == "Not viewed"


def test_home_count_is_the_number_of_not_viewed_cases(client, db, staff_id):
    n = db.execute("SELECT COUNT(*) FROM CARE_CASE WHERE status = 'Not viewed'").fetchone()[0]
    page = client.get(f"/staff/{staff_id('Trần Thị B')}/cases").text
    assert f"<span data-home-count>({n})</span>" in page


def test_the_doctor_list_has_no_priority_sort_waiting_column_or_home_count(client, staff_id):
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases").text
    assert "data-sort" not in page and "data-waiting" not in page and "data-home-count" not in page
    assert vi("Sort: Newest") in page
    page = client.get(f"/staff/{staff_id('Nguyễn Văn A')}/cases", params={"sort": "Priority"}).text   # the doctor cannot ask for it
    assert "data-sort" not in page
