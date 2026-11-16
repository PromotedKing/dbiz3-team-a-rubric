"""D-94 (proposed), 16/11/2026: the chatbot reads what the mother already sees in the sub-app — profile, the doctor's note and
ultrasound, metric statistics, diary, messages to the baby, staff replies, report count — instead of pointing to the screen.
Built in the app, never by the LLM (BR-001); arithmetic only, no judgement (BR-006); never what the sub-app does not show
her (blood type, history, allergies, the doctor's conclusion)."""
import json
from datetime import timedelta

import pytest

from mb360.bot import chat, llm, lookup
from tests.acc_helpers import NOW

LAN = "tci-000123"      # seed: linked record TC-00123, BP 128/82 → 150/95, weight 52 → 57 kg, 3 diary entries, nurse reply


@pytest.fixture
def asker(db, user_id):
    uid, n = user_id(LAN), [0]

    def ask(q):
        n[0] += 1                                        # a new minute each time, so no question counts as a repeat (D-90)
        fake = llm.FakeLLM()
        conv = chat.ask(db, uid, None, q, NOW + timedelta(minutes=10 * n[0]), fake)
        question, answer = db.execute("SELECT * FROM CHAT_MESSAGE WHERE conversation_id = ? ORDER BY rowid", (conv,)).fetchall()
        assert fake.last_input is None                   # never sent to the LLM
        return answer["text"], json.loads(question["parsed_intent"])
    return ask


def test_profile_but_never_the_clinical_record(asker):
    text, _ = asker("Hãy đọc hồ sơ của tôi")
    assert text.splitlines()[:2] == ["Mã hồ sơ khám: TC-00123.", "Liên kết hồ sơ bệnh viện: đã liên kết."]
    assert text.endswith("Nhóm máu, tiền sử và dị ứng không có trong app: mẹ hỏi bác sĩ ở lần khám tới nhé.")
    text, _ = asker("Nhóm máu của em là gì?")
    assert text == "Nhóm máu, tiền sử và dị ứng không có trong app: mẹ hỏi bác sĩ ở lần khám tới nhé."


def test_doctors_note_and_the_latest_ultrasound(asker):
    text, found = asker("Kết quả siêu âm lần trước thế nào?")
    assert text == ("Lần khám gần nhất của mẹ: ngày 15/09/2026 (12 ngày trước).\nGhi chú của bác sĩ: “Sample doctor note”\n"
                    "Số đo thai nhi gần nhất (18/08/2026): cân nặng ước tính 480 g, chiều dài 27 cm.")
    assert lookup.link("u", found) == "/m/u/timeline/day/2026-09-15"


def test_statistics_as_s025_computes_them(asker):
    text, found = asker("Huyết áp tuần này của em thế nào?")
    assert found == {"intent": "lookup", "topic": "trend", "metric": "Blood pressure", "when": "week"}
    assert text == ("Huyết áp trong 7 ngày qua: 2 lần đo, gần nhất 150/95 mmHg (26/09/2026 · 20:15).\n"
                    "Trung bình 139/88, thấp nhất 128/82, cao nhất 150/95 mmHg.")
    text, _ = asker("Em tăng bao nhiêu cân từ đầu thai kỳ?")
    assert text.endswith("Chênh lệch từ lần đo đầu đến lần gần nhất: +5 kg.")
    for judgement in ("cao huyết áp", "bình thường", "Cảnh báo", "vượt ngưỡng", "nguy hiểm"):
        assert judgement not in text


def test_diary(asker):
    assert asker("Em đã viết bao nhiêu nhật ký?")[0] == "Mẹ đã viết 3 trang nhật ký; trang gần nhất ngày 27/09/2026."
    assert asker("Hôm qua em viết nhật ký gì?")[0] == "Ngày 26/09/2026 mẹ không viết nhật ký."
    text, _ = asker("Tuần trước em ghi gì?")
    assert "“The baby kicked a lot today.”" in text


def test_messages_replies_and_reports(asker):
    assert asker("Bố bé nhắn gì cho con?")[0].startswith("Lời nhắn của bố (tuần 28): “Dad is counting the days")
    text, _ = asker("Y tá nói gì với em?")
    assert text.startswith("Phản hồi gần nhất của y tá Trần Thị B (26/09/2026 · 20:38):")
    assert asker("Em đã gửi bao nhiêu báo cáo?")[0] == "Mẹ đã gửi 3 báo cáo; 1 báo cáo đang được xử lý."


def test_empty_answers(db, user_id):
    uid = user_id("tci-000133")
    texts = []
    for i, q in enumerate(("Bố bé nhắn gì cho con?", "Y tá nói gì với em?", "Em đã viết bao nhiêu nhật ký?")):
        conv = chat.ask(db, uid, None, q, NOW + timedelta(minutes=10 * i), llm.FakeLLM())
        texts.append(db.execute("SELECT text FROM CHAT_MESSAGE WHERE conversation_id = ? AND sender = 'Chatbot'", (conv,)).fetchone()[0])
    assert all(t for t in texts)
