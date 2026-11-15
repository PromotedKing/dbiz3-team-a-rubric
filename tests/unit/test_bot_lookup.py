"""BOT FR-012, BR-006, BR-001, BR-002 (D-89, proposed): questions about the mother's own data are answered by the app."""
import json
import uuid

import pytest

from mb360 import tci_booking
from mb360.bot import chat, classify, llm, lookup
from tests.acc_helpers import NOW

MOTHER = "tci-000126"          # seed: week 31, BP 145/92 from a report, one unread notice, one case escalated, BP watch flag


def ask(db, uid, q, conv=None, client=None):
    client = client or llm.FakeLLM()
    conv = chat.ask(db, uid, conv, q, NOW, client)
    rows = db.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY sent_at, rowid", (conv,)).fetchall()
    return conv, rows[-2], rows[-1], client


@pytest.mark.parametrize("q, found", [
    ("Lịch khám tới của em là khi nào?", {"topic": "appointment"}),
    ("When is my next appointment?", {"topic": "appointment"}),
    ("Lần khám trước của em là ngày nào?", {"topic": "last_visit"}),
    ("Huyết áp lần trước của em là bao nhiêu?", {"topic": "metric", "metric": "Blood pressure"}),
    ("What was my last blood pressure?", {"topic": "metric", "metric": "Blood pressure"}),
    ("Cân nặng của em bây giờ là bao nhiêu?", {"topic": "metric", "metric": "Weight"}),
    ("Tim thai gần nhất là bao nhiêu?", {"topic": "metric", "metric": "Fetal heart rate"}),
    ("Em đang mang thai tuần thứ mấy?", {"topic": "week"}),
    ("Ngày dự sinh của em là khi nào?", {"topic": "week"}),
    ("Em có tin nhắn mới nào không?", {"topic": "notices"}),
    ("Báo cáo của em đã ai xem chưa?", {"topic": "reports"}),
    ("Bác sĩ dặn em theo dõi gì?", {"topic": "instructions"}),
])
def test_lookup_questions(q, found):
    assert classify.classify(q) == {"category": "lookup", "danger": False, "lookup": found}


@pytest.mark.parametrize("q, category", [
    ("Huyết áp lần trước của em có cao không?", "needs_nurse"),      # what it means → nurse (BR-002, BR-006)
    ("Was my last blood pressure too high?", "needs_nurse"),
    ("Huyết áp của em bao nhiêu, có bình thường không?", "needs_nurse"),
    ("Lịch khám tới em bị ra máu thì sao?", "needs_nurse"),          # danger first
    ("Lần khám tới em cần chuẩn bị gì?", "general"),                 # not asking for data
    ("Ngày dự sinh được tính thế nào?", "general"),
    ("How can I control my weight during pregnancy?", "general"),
])
def test_questions_that_are_not_lookups(q, category):
    assert classify.classify(q)["category"] == category


def test_lookup_is_answered_by_the_app_without_the_llm(db, user_id):
    """FR-012, BR-006: no LLM call, no AI_RESPONSE_LOG row, the topic kept on the question, not a risk."""
    conv, question, answer, fake = ask(db, user_id(MOTHER), "Em đang mang thai tuần thứ mấy?")
    assert fake.last_input is None
    assert json.loads(question["parsed_intent"]) == {"intent": "lookup", "topic": "week"} and question["is_risk"] == 0
    assert answer["text"] == "Mẹ đang ở tuần thai thứ 31.\nNgày dự sinh: 29/11/2026, còn 63 ngày."
    assert db.execute("SELECT COUNT(*) FROM AI_RESPONSE_LOG WHERE conversation_id = ?", (conv,)).fetchone()[0] == 0


def test_lookup_answer_never_reaches_the_llm_later(db, user_id):
    """BR-001: a later general question gets no earlier lookup turn in its context."""
    uid = user_id(MOTHER)
    conv, _, _, _ = ask(db, uid, "Huyết áp lần trước của em là bao nhiêu?")
    _, _, _, fake = ask(db, uid, "Bà bầu nên ăn gì để đủ sắt?", conv)
    assert fake.last_input[1] == {"gestational_week": 31, "earlier": []}
    assert "145/92" not in json.dumps(fake.last_input, ensure_ascii=False)


def test_answers_from_the_seed(db, user_id):
    uid = user_id(MOTHER)
    assert ask(db, uid, "Huyết áp lần trước của em là bao nhiêu?")[2]["text"] == (
        "Chỉ số huyết áp gần nhất: 145/92 mmHg, 26/09/2026 · 18:02 (Bác sĩ chỉ định).\nĐây là giá trị huyết áp duy nhất trong app.")
    assert ask(db, uid, "Báo cáo của em đã ai xem chưa?")[2]["text"] == "Báo cáo đang được xử lý: 1. Báo cáo mới nhất: đã chuyển bác sĩ."
    assert ask(db, uid, "Bác sĩ dặn em theo dõi gì?")[2]["text"] == "Bác sĩ dặn mẹ theo dõi: huyết áp."
    assert ask(db, uid, "Em có tin nhắn mới nào không?")[2]["text"].startswith("Mẹ có 1 thông báo chưa đọc.\nMới nhất: Báo cáo BC-0926-011")
    assert ask(db, uid, "Lần khám trước của em là ngày nào?")[2]["text"] == (
        "Lần khám gần nhất của mẹ: ngày 12/09/2026 (15 ngày trước).\nGhi nhận ở lần khám đó: Tim thai 172 bpm.")
    assert ask(db, uid, "Cân nặng của em bây giờ là bao nhiêu?")[2]["text"] == "Trong app chưa có giá trị cân nặng nào."
    assert ask(db, uid, "Lịch khám tới của em là khi nào?")[2]["text"] == "Mẹ chưa có lịch hẹn sắp tới trong app TCI."


def _copy_metric(db, uid, metric, value, measured_at):
    row = dict(db.execute("SELECT * FROM HEALTH_METRIC_RECORD WHERE user_id = ? AND metric = ? LIMIT 1", (uid, metric)).fetchone())
    row.update(record_id=str(uuid.uuid4()), value=value, measured_at=measured_at, created_at=measured_at)
    db.execute(f"INSERT INTO HEALTH_METRIC_RECORD ({', '.join(row)}) VALUES ({', '.join('?' * len(row))})", list(row.values()))


def test_change_from_the_previous_value_is_arithmetic_only(db, user_id):
    """BR-006: the difference, never "high" / "low" / "normal" and never "Alert"."""
    uid = user_id(MOTHER)
    _copy_metric(db, uid, "Blood pressure", "150/90", "2026-09-27 08:00")
    text = ask(db, uid, "Huyết áp gần nhất của em là bao nhiêu?")[2]["text"]
    assert text == ("Chỉ số huyết áp gần nhất: 150/90 mmHg, 27/09/2026 · 08:00 (Bác sĩ chỉ định).\n"
                    "Lần trước đó: 145/92 mmHg, 26/09/2026 · 18:02.\nChênh lệch: tâm thu +5, tâm trương −2 mmHg.")
    for judgement in ("cao", "thấp", "bình thường", "Cảnh báo", "Alert", "vượt ngưỡng"):
        assert judgement not in text


def test_weight_change_and_other_mothers_rows_are_never_read(db, user_id):
    uid, other = user_id(MOTHER), user_id("tci-000133")
    for who, value, at in ((uid, "60.0", "2026-09-20 07:00"), (uid, "61.2", "2026-09-27 07:00"), (other, "75.0", "2026-09-27 09:00")):
        db.execute("""INSERT INTO HEALTH_METRIC_RECORD (record_id, user_id, metric, metric_group, value, unit, glucose_context, measured_at,
                      source, visit_id, gestational_week, created_at) VALUES (?, ?, 'Weight', 'Group 1', ?, 'kg', NULL, ?, 'Self-entered', NULL, 31, ?)""",
                   (str(uuid.uuid4()), who, value, at, at))
    text = ask(db, uid, "Cân nặng của em bây giờ là bao nhiêu?")[2]["text"]
    assert text.endswith("Lần trước đó: 60.0 kg, 20/09/2026 · 07:00.\nChênh lệch: +1,2 kg.") and "75.0" not in text


def test_next_appointment_from_the_tci_feed(db, user_id):
    uid = user_id(MOTHER)
    db.execute(tci_booking.DDL)
    db.execute(f"""INSERT INTO {tci_booking.TABLE} (appointment_id, user_id, facility, specialty, reason, appointment_at, status, created_at)
                   VALUES ('a-1', ?, 'Bệnh viện Thu Cúc', 'Sản khoa', 'Khám thai', '2026-09-30 09:30', 'Confirmed', '2026-09-20 10:00')""", (uid,))
    assert ask(db, uid, "Lịch khám tới của em là khi nào?")[2]["text"] == (
        "Lịch hẹn tới của mẹ: Thứ Tư, 30/09/2026 · 09:30, tại Bệnh viện Thu Cúc.\nTức là còn 3 ngày nữa.")


def test_links_to_the_screen():
    assert lookup.link("u", {"topic": "metric", "metric": "Blood pressure"}) == "/m/u/history?metric=Blood%20pressure"
    assert lookup.link("u", {"topic": "appointment"}) == "/m/u/appointments"
    assert lookup.link("u", {"intent": "general"}) is None
