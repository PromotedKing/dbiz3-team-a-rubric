"""D-93 (proposed), 15/11/2026: distress goes to the nurse, self-harm is a danger sign, the baby's measures are not the mother's
weight, and her own data the chatbot cannot read yet — or a request to act for her — gets a pointer to the screen instead
of reaching the LLM, which has no data (BR-001)."""
import pytest

from mb360.bot import chat, classify, llm, lookup
from tests.acc_helpers import NOW


def ask(db, uid, q):
    fake = llm.FakeLLM()
    conv = chat.ask(db, uid, None, q, NOW, fake)
    rows = db.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at, rowid", (conv,)).fetchall()
    return rows[-2], rows[-1], fake


@pytest.mark.parametrize("q, category, danger", [
    ("Em lo lắng quá", "needs_nurse", False),
    ("Em buồn và hay khóc", "needs_nurse", False),
    ("Chồng em không quan tâm em", "needs_nurse", False),
    ("I keep crying every night", "needs_nurse", False),
    ("Gọi y tá cho em", "needs_nurse", False),
    ("Em muốn chết", "needs_nurse", True),
    ("Em không muốn sống nữa", "needs_nurse", True),
    ("Trầm cảm sau sinh là gì?", "general", False),          # knowledge, not her
    ("Mất ngủ khi mang thai", "general", False),
    ("Khi nào cần gặp bác sĩ?", "general", False),
    ("Cân nặng thai nhi 30 tuần là bao nhiêu?", "general", False),
])
def test_distress_and_requests(q, category, danger):
    k = classify.classify(q)
    assert (k["category"], k["danger"]) == (category, danger)


@pytest.mark.parametrize("q, topic", [
    ("Cân nặng thai nhi lần siêu âm gần nhất?", "fetal"),
    ("Hãy đọc hồ sơ của tôi", "see_record"),
    ("Nhóm máu của em là gì?", "see_record"),
    ("Bác sĩ kết luận gì ở lần khám trước?", "see_visit_notes"),
    ("Kết quả siêu âm lần trước thế nào?", "see_visit_notes"),
    ("Huyết áp tuần này của em thế nào?", "trend"),
    ("Em tăng bao nhiêu cân từ đầu thai kỳ?", "trend"),
    ("Giấc ngủ của em tuần này?", "trend"),
    ("Hôm qua em viết nhật ký gì?", "see_diary"),
    ("Bố bé nhắn gì cho con?", "see_family"),
    ("Y tá nói gì với em?", "see_staff_reply"),
    ("Em đã gửi bao nhiêu báo cáo?", "see_report_count"),
    ("Đặt lịch khám giúp em", "act_booking"),
    ("Đổi lịch khám sang thứ 7 được không?", "act_booking"),
    ("Gửi báo cáo huyết áp 130/85 giúp em", "act_report"),
    ("Ghi nhật ký hôm nay giúp em", "act_diary"),
    ("Bật nhắc lịch khám cho em", "act_reminders"),
])
def test_answered_in_the_app_not_by_the_llm(db, user_id, q, topic):
    k = classify.classify(q)
    assert k["category"] == "lookup" and k["lookup"]["topic"] == topic
    question, answer, fake = ask(db, user_id("tci-000126"), q)
    assert fake.last_input is None                                               # never sent to the LLM
    assert db.execute("SELECT COUNT(*) FROM AI_RESPONSE_LOG WHERE conversation_id = ?", (answer["conversation_id"],)).fetchone()[0] == 0
    assert answer["text"] and "130/85" not in answer["text"]                    # no comment on her value


def test_fetal_measures_are_not_the_mothers_weight(db, user_id):
    question, answer, _ = ask(db, user_id("tci-000123"), "Cân nặng thai nhi lần siêu âm gần nhất?")
    assert answer["text"] == "Số đo thai nhi gần nhất (18/08/2026): cân nặng ước tính 480 g, chiều dài 27 cm."
    import json
    assert lookup.link(user_id("tci-000123"), json.loads(question["parsed_intent"])).endswith("/timeline/day/2026-08-18")


def test_pointer_links():
    assert lookup.link("u", {"topic": "trend", "metric": "Blood pressure"}) == "/m/u/history?metric=Blood%20pressure"
    assert lookup.link("u", {"topic": "act_booking"}) == "/m/u/appointments"
    assert lookup.link("u", {"topic": "act_report"}) == "/m/u/report"
    assert lookup.link("u", {"topic": "see_record"}) == "/m/u/profile"
    assert lookup.link("u", {"topic": "see_visit_notes", "path": "timeline/day/2026-09-12"}) == "/m/u/timeline/day/2026-09-12"
