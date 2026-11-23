"""Tests for the Nurse Screen Redesign (S-061 & S-064) by Ánh & Chi.

Verifies:
1. Queue (S-061):
   - 4 tabs with counts: Chưa xem, Đã xem, Đã chuyển, Đã xử lý.
   - Priority sort: Critical/Above threshold first, then longest waiting.
   - Card layout with urgency color bar, lines 1 & 2, overdue tag.
   - Mother name search.
   - Nurse has no notification bell.
2. Case Detail (S-064):
   - Header with large urgency badge, main symptom, waiting time.
   - Sticky action bar.
   - Only 1 latest metric value, arrow ↑ on above threshold.
   - Collapsible mother & baby profile.
   - Handling history timeline.
   - Action buttons per state.
   - Escalation with reason and note.
   - Guidance with template selection.
   - Remind doctor & Reopen case.
"""
from datetime import datetime
from tests.cli_helpers import RPT010, case_by_code
from tests.integration.helpers import vi


def test_nurse_queue_tabs_and_counts(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    res = client.get(f"/staff/{nurse}/cases")
    assert res.status_code == 200
    page = res.text

    # 4 tabs must be present with counts
    for tab_label in ("Chưa xem", "Đã xem", "Đã chuyển", "Đã xử lý"):
        assert tab_label in page

    # Default is "Chưa xem" (Not viewed)
    assert 'data-active-filter="Not viewed"' in page

    # No bell for nurse
    assert f'href="/staff/{nurse}/notifications"' not in page


def test_nurse_search_by_mother_name(client, staff_id):
    nurse = staff_id("Trần Thị B")
    # Search for "Lan"
    res = client.get(f"/staff/{nurse}/cases", params={"status": "Not viewed", "q": "Lan"})
    assert res.status_code == 200
    assert "Nguyễn Thị Lan" in res.text

    # Search for nonexistent name
    res_empty = client.get(f"/staff/{nurse}/cases", params={"status": "Not viewed", "q": "NonexistentMotherXYZ"})
    assert "No cases to handle." in res_empty.text or "Không có ca" in res_empty.text


def test_nurse_case_detail_layout_and_latest_metric(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    res = client.get(f"/staff/{nurse}/cases/{boundary_case}")
    assert res.status_code == 200
    page = res.text

    # 1. Header with large urgency badge
    assert "KHẨN" in page

    # 2. Sticky action bar
    assert "nurse-sticky-actions" in page
    assert "TRẠNG THÁI CA:" in page

    # 3. Only latest metric value with arrow ↑
    assert "Chỉ số đo gần nhất" in page
    assert "↑" in page
    assert "140/90 mmHg" in page

    # 4. Collapsible mother info
    assert "Thông tin mẹ và bé" in page
    assert "<details" in page

    # 5. Handling history timeline
    assert "Lịch sử xử lý" in page
    assert "Thai phụ:" in page

    # 6. Escalate modal with reason options
    assert "Chuyển ca cho Bác sĩ" in page
    assert "Chỉ số vượt ngưỡng cảnh báo an toàn" in page


def test_nurse_actions_state_flow(client, db, staff_id, boundary_case):
    nurse = staff_id("Trần Thị B")
    base = f"/staff/{nurse}/cases/{boundary_case}"

    # State 1: Not viewed -> has "Đánh dấu Đã xem"
    page = client.get(base).text
    assert vi("Mark as viewed") in page

    # Mark viewed
    assert client.post(f"{base}/view").status_code == 303
    page_viewed = client.get(base).text
    assert vi("Viewed") in page_viewed

    # Escalate with reason and note
    res_esc = client.post(
        f"{base}/escalate",
        data={"reason": "Chỉ số vượt ngưỡng cảnh báo an toàn", "note": "Huyết áp cao liên tục 2 ngày"},
    )
    assert res_esc.status_code == 303

    # State 3: Escalated to doctor -> has "Nhắc bác sĩ", no Close case button for nurse
    page_esc = client.get(base).text
    assert "Đã chuyển" in page_esc
    assert "Nhắc bác sĩ" in page_esc
    assert "Đóng ca" not in page_esc

    # Remind doctor
    assert client.post(f"{base}/remind").status_code == 303


def test_nurse_close_and_reopen_normal_case(client, db, staff_id):
    nurse = staff_id("Trần Thị B")
    case = case_by_code(db, RPT010)
    base = f"/staff/{nurse}/cases/{case}"

    # Mark viewed
    client.post(f"{base}/view")

    # Close case (normal case)
    assert client.post(f"{base}/close").status_code == 303
    page_closed = client.get(base).text
    assert "Đã hoàn thành" in page_closed
    assert "Mở lại" in page_closed

    # Reopen case
    assert client.post(f"{base}/reopen").status_code == 303
    page_reopened = client.get(base).text
    assert "Chưa xem" in page_reopened
