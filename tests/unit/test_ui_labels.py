"""D-79 — on-screen text comes from docs/ui-label-reference.md (ui-label-reference "UI label reference")."""
from mb360 import ui


def test_table_loads_without_conflicts():
    assert len(ui.LABELS) > 300
    assert ui.CONFLICTS == []                       # one English label, one on-screen text


def test_wireframe_labels():
    assert ui.t("Normal") == "Bình thường" and ui.t("Above threshold") == "Vượt ngưỡng" and ui.t("Not assessed") == "Chưa đánh giá"
    assert ui.t("Not viewed") == "Chưa xem" and ui.t("Escalated to doctor") == "Đã chuyển bác sĩ"
    assert ui.t("From visit") == "Từ lần khám" and ui.t("Doctor-assigned") == "Bác sĩ chỉ định"
    assert ui.t("Metric alert") == "Cảnh báo chỉ số" and ui.t("Signs that need medical attention") == "Dấu hiệu cần chú ý y tế"


def test_split_and_ui_forms():
    assert ui.t("Save metrics") == "Lưu chỉ số"                        # "CTA" row
    assert ui.t("Profile") == "Hồ sơ" and ui.t("Appointments") == "Lịch hẹn"        # Tab row; "Appointments" is the TCI home tile
    assert ui.t("Severe headache / dizziness / blurred vision") == "Đau đầu dữ dội / chóng mặt / hoa mắt"   # "(UI: …)" form
    assert ui.t("Mother & Baby 360") == "Mẹ & Bé 360"                 # "(tile)" note dropped


def test_fields_and_patterns():
    assert ui.t("Week {n}", n=28) == "Tuần 28"
    assert ui.t("Above threshold when ≥ 140/90 mmHg") == "Vượt ngưỡng khi ≥ 140/90 mmHg"   # text built from THRESHOLD_RULE
    assert ui.t("Response from Nurse Trần Thị B") == "Phản hồi từ y tá Trần Thị B"
    assert ui.t_list("Palpitations, Other") == "Hồi hộp, Khác"


def test_stored_notification_titles():
    assert ui.t_known("Report BC-0926-015 resolved") == "Báo cáo BC-0926-015 đã xử lý"          # not "Report {code}"
    assert ui.t_known("Your Blood pressure report has been sent to clinical staff") == "Báo cáo Huyết áp của mẹ đã được gửi tới nhân viên y tế"
    assert ui.t_known("Nurse Trần Thị B responded to your Blood pressure report") == "Y tá Trần Thị B đã phản hồi Báo cáo Huyết áp của mẹ"
    assert ui.t_known("Your Symptom report is Viewed") == "Báo cáo triệu chứng của mẹ: Đã xem"
    assert ui.t_parts("150/95 mmHg · Above threshold") == "150/95 mmHg · Vượt ngưỡng"
    assert ui.t_known("sample text") == "sample text" and ui.MISSING == set()


def test_missing_label_is_shown_in_english_and_recorded():
    ui.MISSING.clear()
    assert ui.t("A label nobody wrote down") == "A label nobody wrote down"
    assert ui.MISSING == {"A label nobody wrote down"}
    ui.MISSING.clear()


def test_stored_text_is_translated_only_when_it_is_a_label():
    assert ui.t_known("[Sample chatbot answer]") == "[Câu trả lời mẫu của chatbot]"
    assert ui.t_known("Eat well-cooked beef.") == "Eat well-cooked beef."
    assert ui.MISSING == set()


def test_every_tab_has_a_label():
    assert [ui.t(label) for _, label, _ in ui.TABS] == ["Trang chủ", "Thai kỳ", "Chatbot", "Thông báo", "Hồ sơ"]     # Chi and Ánh, 06/11/2026
