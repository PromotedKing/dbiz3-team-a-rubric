"""The sample mother of the v1.0.0 app (invented, hard rule 3): a full pregnancy record in Vietnamese, added on top of the seed when
the app is served. The tests and data/seed/ do not use this file. Every date is relative to the day the database is built, so
the app always opens at week 24 + 3 days, as in the UI package. The clinical wording is sample data, Pending SME (D-81)."""
import json
import sqlite3
import uuid
from datetime import datetime, timedelta
from pathlib import Path

from . import appointment_demo, art, demo_diary, tci_feed
from .tml.diary import MEDIA_DIR

TCI_REF = "tci-000200"
GESTATIONAL_DAYS = 24 * 7 + 4
DAYS_LEFT = 280 - GESTATIONAL_DAYS
FACILITY = "Bệnh viện Thu Cúc"


def _id(name: str) -> str:
    return str(uuid.uuid5(uuid.NAMESPACE_URL, f"mb360-persona/{name}"))


USER = _id("mai")
DOCTOR, NURSE = _id("doctor"), _id("nurse")

# (days before today, week, type, conclusion, doctor's note, image, length cm, weight g, BP, fetal heart rate, weight kg, fasting glucose)
VISITS = (
    (4, 24, "Khám thai định kỳ tuần 24", "Thai phát triển phù hợp tuổi thai", "Thai phát triển phù hợp tuổi thai. Mẹ tiếp tục đo huyết áp sáng – tối tại nhà.", "us-24", 30.0, 650, "116/74", "146", "58.0", None),
    (32, 20, "Siêu âm hình thái tuần 20", "Hình thái thai trong giới hạn bình thường", "Siêu âm hình thái chưa thấy bất thường. Hẹn khám lại sau 4 tuần.", "us-20", 25.0, 320, "114/72", "148", "56.5", None),
    (60, 16, "Khám thai định kỳ tuần 16", "Thai phát triển tốt", "Mẹ ăn uống tốt hơn, bớt nghén. Tiếp tục viên sắt theo đơn.", None, None, None, "112/72", "150", "55.0", None),
    (88, 12, "Sàng lọc quý 1 tuần 12", "Kết quả sàng lọc nguy cơ thấp", "Độ mờ da gáy trong giới hạn. Kết quả sàng lọc nguy cơ thấp.", "us-12", 6.1, 18, "112/70", "154", "54.0", None),
    (116, 8, "Khám thai lần đầu tuần 8", "Thai trong tử cung, có tim thai", "Đã thấy tim thai. Bác sĩ dặn mẹ bổ sung axit folic theo đơn.", None, None, None, "110/70", "148", "53.0", None),
)
# (days before today, HH:MM, value): home blood pressure reports with no case (normal, no symptoms)
BP_HOME = ((26, "20:10", "116/76"), (23, "07:05", "118/78"), (19, "20:15", "121/77"), (15, "07:10", "117/75"), (12, "20:05", "119/78"),
           (9, "07:05", "121/77"), (6, "20:15", "120/78"), (4, "07:15", "118/76"))
GUIDANCE = "Nằm nghỉ nghiêng trái 15 phút rồi đo lại.\nĐau đầu không giảm, mờ mắt hoặc đau vùng trên rốn: đến viện ngay."
BP_RESPONSE = ("Chỉ số vượt ngưỡng theo dõi. Mẹ chưa có dấu hiệu nguy hiểm, nhưng cần theo dõi sát 3 ngày tới và khám lại sớm hơn lịch.\n"
               "- Nằm nghỉ nghiêng trái 15 phút rồi đo lại, báo kết quả ở Trang chủ.\n"
               "- Đo sáng và tối mỗi ngày đến buổi khám.\n"
               "- Đến viện ngay nếu đau đầu dữ dội, mờ mắt hoặc đau vùng thượng vị.\n"
               "Hẹn khám: {follow_up}")


def _copy_art() -> None:
    folder = Path(MEDIA_DIR) / "demo"
    folder.mkdir(parents=True, exist_ok=True)
    for name, draw in art.FILES.items():
        (folder / name).write_text(draw(), encoding="utf-8")


def install(conn: sqlite3.Connection, now: datetime) -> str:
    """Adds the sample mother. No consent and no pregnancy profile yet: she goes through the whole first-opening flow."""
    today = now.date()
    edd = today + timedelta(days=DAYS_LEFT)

    def day(n: int) -> str:
        return (today - timedelta(days=n)).isoformat()

    def at(n: int, clock: str) -> str:
        return f"{day(n)} {clock}"

    def week_of(n: int) -> int:
        return (GESTATIONAL_DAYS - n) // 7

    conn.execute(tci_feed.DDL)
    conn.execute("INSERT INTO STAFF (staff_id, full_name, role, login_account) VALUES (?, 'Trần Thu Hà', 'Doctor', 'bs.thuha'), (?, 'Phạm Thị Lan', 'Nurse', 'yt.lan')", (DOCTOR, NURSE))
    conn.execute("""INSERT INTO USER_ACCOUNT (user_id, tci_account_ref, full_name, phone, date_of_birth, sex, record_code, role)
                    VALUES (?, ?, 'Nguyễn Thị Mai', '0912000678', '1996-04-12', 'Female', 'TC-00200', 'Mother')""", (USER, TCI_REF))
    conn.execute("INSERT INTO NOTIFICATION_PREFERENCE (user_id, report_response, new_visit_result, appointment_reminder, watch_flag_reminder, updated_at) VALUES (?, 1, 1, 1, 0, ?)", (USER, at(116, "08:00")))
    conn.execute("INSERT INTO PATIENT_ASSIGNMENT (user_id, doctor_id, valid_from, valid_to) VALUES (?, ?, ?, NULL)", (USER, DOCTOR, day(116)))
    conn.execute("INSERT INTO EMR_LINKAGE_REQUEST (user_id, record_code, facility, status, requested_at, linked_at) VALUES (?, 'TC-00200', ?, 'Linked', ?, ?)", (USER, FACILITY, at(116, "08:00"), at(116, "09:00")))

    def record(key, metric, group, value, unit, when, source, week, visit=None, context=None) -> str:
        rid = _id(f"hmr/{key}")
        conn.execute("""INSERT INTO HEALTH_METRIC_RECORD (record_id, user_id, metric, metric_group, value, unit, glucose_context, measured_at, source, visit_id, gestational_week, created_at)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (rid, USER, metric, group, value, unit, context, when, source, visit, week, when))
        return rid

    for n, week, kind, conclusion, note, image, length, weight, bp, fhr, kg, glucose in VISITS:
        vid = _id(f"visit/{week}")
        conn.execute("""INSERT INTO VISIT (visit_id, user_id, visit_date, facility, visit_type, conclusion, doctor_note, ultrasound_image, fetal_length, estimated_fetal_weight, ultrasound_report_date, gestational_week)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (vid, USER, day(n), FACILITY, kind, conclusion, note, f"demo/{image}.svg" if image else None, length, weight, day(n) if image else None, week))
        when = at(n, "09:30")
        record(f"v{week}/bp", "Blood pressure", "Group 2", bp, "mmHg", when, "From visit", week, vid)
        record(f"v{week}/fhr", "Fetal heart rate", "Visit", fhr, "bpm", when, "From visit", week, vid)
        record(f"v{week}/kg", "Weight", "Group 1", kg, "kg", when, "From visit", week, vid)
        if week >= 14:
            record(f"v{week}/protein", "Urine protein", "Group 2", "Negative", None, when, "From visit", week, vid)
        if glucose:
            record(f"v{week}/glu", "Blood glucose", "Group 2", glucose, "mmol/L", when, "From visit", week, vid, "fasting")

    latest_visit = _id("visit/24")
    template = _id("guidance/bp")
    conn.execute("INSERT INTO GUIDANCE_TEMPLATE (template_id, title, content, is_default, metric, created_by) VALUES (?, 'Hướng dẫn huyết áp', ?, 0, 'Blood pressure', ?)", (template, GUIDANCE, DOCTOR))
    flags = {"Blood pressure": ("Đo sáng (07:00) và tối (20:00), ngồi nghỉ 5 phút trước khi đo.", template, 2),
             "Blood glucose": ("Đo lúc đói và sau ăn 2 giờ, 3 ngày mỗi tuần.", None, 30),
             "Urine protein": ("Thử que nước tiểu buổi sáng, 2 lần mỗi tuần.", None, 2)}
    for metric, (note, tpl, n) in flags.items():
        conn.execute("""INSERT INTO WATCH_FLAG (flag_id, user_id, visit_id, metric, flagged_by, flagged_at, note, template_id, custom_text, active)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, NULL, 1)""", (_id(f"flag/{metric}"), USER, latest_visit if n == 2 else _id("visit/20"), metric, DOCTOR, day(n), note, tpl))

    def report(key, code, metric, value, unit, n, clock, symptoms, context=None) -> str:
        when = at(n, clock)
        rec = record(f"r/{key}", metric, "Group 2", value, unit, when, "Doctor-assigned", week_of(n), None, context) if value else None
        rid = _id(f"report/{key}")
        conn.execute("""INSERT INTO METRIC_REPORT (report_id, report_code, user_id, metric, health_metric_record_id, other_symptom_text, note, submitted_at, watch_flag_id)
                        VALUES (?, ?, ?, ?, ?, NULL, NULL, ?, ?)""", (rid, code, USER, metric, rec, when, _id(f"flag/{metric}") if value else None))
        conn.executemany("INSERT INTO REPORT_SYMPTOM (report_id, symptom) VALUES (?, ?)", [(rid, s) for s in symptoms])
        return rid

    for i, (n, clock, value) in enumerate(BP_HOME):
        report(f"bp{i}", f"BC-M{i:03d}", "Blood pressure", value, "mmHg", n, clock, ["No symptoms"])
    report("glu", "BC-M020", "Blood glucose", "4.8", "mmol/L", 8, "07:10", ["No symptoms"], "fasting")
    report("urine", "BC-M021", "Urine protein", "Negative", None, 5, "07:20", ["No symptoms"])

    def case(key, source, status, created, report_id=None, chat=None, doctor=None, closed=None, closed_by=None) -> str:
        cid = _id(f"case/{key}")
        conn.execute("""INSERT INTO CARE_CASE (case_id, user_id, case_source, status, metric_report_id, chat_message_id, assigned_doctor_id, created_at, closed_at, closed_by)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""", (cid, USER, source, status, report_id, chat, doctor, created, closed, closed_by))
        conn.execute("INSERT INTO CASE_STATUS_HISTORY (case_id, status, changed_at, changed_by, role) VALUES (?, 'Not viewed', ?, NULL, 'System')", (cid, created))
        return cid

    def history(cid, status, when, staff, role) -> None:
        conn.execute("INSERT INTO CASE_STATUS_HISTORY (case_id, status, changed_at, changed_by, role) VALUES (?, ?, ?, ?, ?)", (cid, status, when, staff, role))

    def respond(key, cid, staff, role, text, when) -> None:
        conn.execute("INSERT INTO STAFF_RESPONSE (response_id, case_id, responder_id, responder_role, template_id, custom_text, sent_at) VALUES (?, ?, ?, ?, NULL, ?, ?)",
                     (_id(f"resp/{key}"), cid, staff, role, text, when))

    def notice(key, kind, title, subtitle, when, read=None, cid=None, visit=None) -> None:
        conn.execute("""INSERT INTO NOTIFICATION (notification_id, user_id, type, title, subtitle, created_at, read_at, case_id, visit_id, watch_flag_id, appointment_ref)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, NULL, NULL)""", (_id(f"n/{key}"), USER, kind, title, subtitle, when, read, cid, visit))

    # Yesterday: blood pressure above the threshold, escalated, the doctor answered (unread)
    follow_up = today + timedelta(days=2)
    rep = report("bp-high", "BC-M030", "Blood pressure", "146/94", "mmHg", 1, "08:40", ["Severe headache, dizziness or blurred vision"])
    cid = case("bp-high", "Metric report", "Escalated to doctor", at(1, "08:42"), report_id=rep, doctor=DOCTOR)
    history(cid, "Viewed", at(1, "08:55"), NURSE, "Nurse")
    history(cid, "Escalated to doctor", at(1, "09:00"), NURSE, "Nurse")
    respond("bp-high", cid, DOCTOR, "Doctor", BP_RESPONSE.format(follow_up=f"{follow_up:%d/%m/%Y} · 08:00"), at(1, "09:12"))
    notice("bp-high", "Report", "Huyết áp 146/94 mmHg cao hơn ngưỡng", f"Về huyết áp mẹ báo sáng {today - timedelta(days=1):%d/%m/%Y}", at(1, "09:12"), cid=cid)
    notice("visit", "Visit result", "Khám thai tuần 24: ổn định", "Tiếp tục đo huyết áp, đường huyết và protein niệu tại nhà, báo cáo ở Trang chủ.", at(2, "11:40"), read=at(2, "12:10"), visit=latest_visit)

    # Six days ago: fetal movement symptom, closed by the nurse without a doctor
    sym = report("sym", "BC-M031", "Symptom", None, None, 6, "14:20", ["Absence of fetal movement"])
    sid = case("sym", "Symptom", "Resolved", at(6, "14:20"), report_id=sym, closed=at(6, "15:05"), closed_by=NURSE)
    history(sid, "Viewed", at(6, "14:30"), NURSE, "Nurse")
    history(sid, "Resolved", at(6, "15:05"), NURSE, "Nurse")
    respond("sym", sid, NURSE, "Nurse", "Đã gọi tư vấn, bé cử động bình thường trở lại. Mẹ tiếp tục đếm cử động mỗi tối.", at(6, "15:05"))
    notice("sym", "Report", "Về báo cáo thai máy giảm", "Đã gọi tư vấn, bé cử động bình thường trở lại.", at(6, "15:05"), read=at(6, "15:30"), cid=sid)

    # Chatbot: one question passed to the nurse, then an ordinary question
    conv = _id("conv/1")
    conn.execute("INSERT INTO CONVERSATION (conversation_id, user_id, current_session_data) VALUES (?, ?, ?)", (conv, USER, json.dumps({"gestational_week": 24, "earlier_turns": 1})))

    def message(key, sender, text, when, intent=None, risk=0, choice=None) -> str:
        mid = _id(f"msg/{key}")
        conn.execute("""INSERT INTO CHAT_MESSAGE (message_id, conversation_id, sender, text, parsed_intent, is_risk, handoff_choice, sent_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                     (mid, conv, sender, text, json.dumps({"intent": intent}) if intent else None, risk, choice, when))
        return mid

    asked = message("q1", "Mother", "Em thấy đau bụng dưới khi đi lại có sao không?", at(4, "21:15"), "needs_nurse", 1, "Connect to nurse")
    message("a1", "Chatbot", "This needs a proper consultation. It will be sent to a nurse if you agree", at(4, "21:15"))
    message("q2", "Mother", "Tuần 24 mẹ nên ăn thêm gì?", at(1, "21:00"), "general")
    message("a2", "Chatbot", "Mẹ nên bổ sung sắt, canxi và đạm: thịt đỏ nạc, trứng, sữa, cá ít thuỷ ngân và rau xanh đậm. Viên sắt, canxi mẹ uống theo đơn bác sĩ đã kê nhé.", at(1, "21:00"))
    bot = case("bot", "Chatbot", "Resolved", at(4, "21:16"), chat=asked, closed=at(4, "22:00"), closed_by=NURSE)
    history(bot, "Viewed", at(4, "21:30"), NURSE, "Nurse")
    history(bot, "Resolved", at(4, "22:00"), NURSE, "Nurse")
    respond("bot", bot, NURSE, "Nurse", "Y tá Lan đã gọi tư vấn. Mẹ nghỉ ngơi, theo dõi thêm và báo lại nếu đau tăng.", at(4, "22:00"))

    diary_counts = [1, 2, 1, 2, 2, 3, 2, 3] + [4, 5] * 4 + [4]
    demo_diary.install(conn, USER, today - timedelta(days=GESTATIONAL_DAYS), today, diary_counts, 0)

    # Self-tracked metrics: this morning (or as early as the clock allows) and the weeks before
    morning = min(now, datetime.combine(today, datetime.min.time()) + timedelta(hours=7, minutes=30)).strftime("%Y-%m-%d %H:%M")
    for key, metric, value, unit, when, week in (("kg", "Weight", "58.4", "kg", morning, 24), ("temp", "Temperature", "36.8", "°C", morning, 24),
                                                 ("hr", "Heart rate", "82", "bpm", morning, 24), ("sleep", "Sleep", "22:30-06:00", None, morning, 24),
                                                 ("kg2", "Weight", "57.9", "kg", at(7, "07:30"), week_of(7)), ("kg3", "Weight", "57.3", "kg", at(14, "07:30"), week_of(14))):
        record(f"self/{key}", metric, "Group 1", value, unit, when, "Self-entered", week)

    conn.execute(f"INSERT INTO {tci_feed.TABLE} (user_id, hospital_edd, next_appointment, appointment_place) VALUES (?, ?, ?, ?)",
                 (USER, edd.isoformat(), f"{today + timedelta(days=7)} 08:30", FACILITY))
    conn.commit()
    appointment_demo.install(conn, now, fresh_demo=True)
    _copy_art()
    return USER
